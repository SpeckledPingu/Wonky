import pandas as pd
from pathlib import Path
import lancedb
import re
from sentence_transformers import SentenceTransformer
from typing import List

class CRSLanceDBFTS():
    def __init__(self, lance_index: Path, lance_table: str, fields:List[str] = None):
        """
        :param lance_index: Path to where the lance index is located
        :param lance_table: Specific table that contains the content for the search
        :param fields: List of the fields to return from the search.
            - Helpful for avoiding the data dump of vectors and all associated metadata.
        """
        self.lance_index = lancedb.connect(lance_index)
        self.lance_table = self.lance_index.open_table(lance_table)
        self.fields = fields

    def search(self, query: str, limit=10, filter_conditions: str = None):
        query = self.clean_query(query)
        if self.fields:
            if filter_conditions:
                return self.lance_table.search(query).limit(limit=limit).where(filter_conditions).select(self.fields).to_list()
            else:
                return self.lance_table.search(query).limit(limit).select(self.fields).to_list()
        else:
            if filter_conditions:
                return self.lance_table.search(query).limit(limit=limit).where(filter_conditions).to_list()
            else:
                return self.lance_table.search(query).limit(limit).to_list()

    def clean_query(self, query: str) -> str:
        """
        Most FTS indexes do not index numbers, special characters, and other characters
        :param query: str
        :return: str - Returns the query stripped of any non-alphabetical characters
        """
        query_parts = re.findall(r'([a-zA-Z]+)', query)
        return ' '.join(query_parts)

class CRSLanceDBVector():
    def __init__(self, lance_index: Path, lance_table: str, encoder: SentenceTransformer, fields:List[str] = None):
        """
        :param lance_index: Path to where the lance index is located
        :param lance_table: Specific table that contains the content for the search
        :param encoder: SentenceTransformer that aligns with the lance_table
            - in case the embedding model is not integrated into the index
        :param fields: List of the fields to return from the search.
            - Helpful for avoiding the data dump of vectors and all associated metadata.
        """
        self.lance_index = lancedb.connect(lance_index)
        self.lance_table = self.lance_index.open_table(lance_table)
        self.encoder = encoder
        self.fields = fields

    def search(self, query: str, limit=10, filter_conditions: str = None):
        query_embedding = self.encoder.encode(query)
        if self.fields:
            if filter_conditions:
                return self.lance_table.search(query_embedding).limit(limit=limit).where(filter_conditions).select(
                    self.fields).to_list()
            else:
                return self.lance_table.search(query_embedding).limit(limit).select(self.fields).to_list()
        else:
            if filter_conditions:
                return self.lance_table.search(query_embedding).limit(limit=limit).where(filter_conditions).to_list()
            else:
                return self.lance_table.search(query_embedding).limit(limit).to_list()


class CRSLanceDBHybrid():
    def __init__(self, fts_index: CRSLanceDBFTS, vector_index: CRSLanceDBVector, alpha=0.5,
                 document_id_column: str = 'id', section_id_column:str = 'section_id', score_column: str = 'score'):
        """
        :param fts_index: Existing fts index
        :param vector_index: Existing vector index
        :param alpha: weighting preference for normalized fts scores vs vector scores
        """
        self.fts_index = fts_index
        self.vector_index = vector_index
        self.alpha = alpha
        self.document_id_column = document_id_column
        self.section_id_column = section_id_column
        self.score_column = score_column
        self.section_id_column = section_id_column

    def search_fts(self, query: str, limit=10, filter_conditions: str = None):
        return self.fts_index.search(query, limit, filter_conditions)

    def search_vector(self, query: str, limit=10, filter_conditions: str = None):
        return self.vector_index.search(query, limit, filter_conditions)

    def normalize_scores(self, scores: pd.Series):
        normalized_scores = (scores - scores.min()) / (scores.max() - scores.min())
        return normalized_scores

    def calculate_hybrid_score(self, fts_results: pd.DataFrame, vector_results: pd.DataFrame):
        fts_joiner = fts_results.sort_values(by=['normalized_score'], ascending=False)
        fts_joiner = fts_joiner.drop_duplicates(subset=[self.document_id_column])
        vector_joiner = vector_results.sort_values(by=['normalized_score'], ascending=False)
        vector_joiner = vector_joiner.drop_duplicates(subset=[self.document_id_column])

        hybrid_results = pd.merge(fts_joiner, vector_joiner, on=self.document_id_column, how='inner',
                                  suffixes=('_fts', '_vec'))
        hybrid_results['hybrid_score'] = self.alpha * hybrid_results['normalized_score_fts'] + (1 - self.alpha) * hybrid_results['normalized_score_vec']
        return hybrid_results[[self.document_id_column, 'hybrid_score']]

    def search(self, query: str, limit=10, filter_conditions: str = None):
        """
        :param query:
        :param limit:
        :param filter_conditions:
        :return:

        Calculates the hybrid score independently for each result set.
        Inner join is used to ensure results are valid given both search types (no imputing scores)
            - Often, a deeper depth than normal is needed to ensure overlap
        Why Inner and Pre-normalization?
            - Normalized hybrid scores are better than RRF when preserving the relative magnitude of distribution is helpful.
            - Inner join means that keywords have to be matched
        Requirements for Inner join hybrid search:
            Queries **must** be expanded prior to search. HyDE is often effective.
            If using an established index with synonym expansion, this requirement is less needed.
            HyDE is still the preferred way to maximize both recall on FTS and provide better embeddings.
        """
        fts_results = self.search_fts(query, limit, filter_conditions)
        vector_results = self.search_vector(query, limit, filter_conditions)
        fts_results = pd.DataFrame(fts_results)
        vector_results = pd.DataFrame(vector_results)

        fts_results['normalized_score'] = self.normalize_scores(fts_results['score'])
        vector_results['normalized_score'] = self.normalize_scores(vector_results['score'])
        hybrid_scores = self.calculate_hybrid_score(fts_results, vector_results)

        fts_results = pd.merge(fts_results, hybrid_scores, how='inner', on=self.document_id_column)
        vector_results = pd.merge(vector_results, fts_results, how='inner', on=self.document_id_column)
        all_results = pd.concat([fts_results, vector_results], axis=0)
        all_results = all_results.sort_values(by=[self.document_id_column, self.section_id_column, 'hybrid_score'],
                                              ascending=False)
        all_results = all_results.drop_duplicates(subset=[self.section_id_column])
        return all_results.to_dict(orient='records')




