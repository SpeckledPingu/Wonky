from typing import List
import sqlite3
import lancedb
from pathlib import Path
from rag.ingestion.datamodels import ResearchPath, SearchDocument
from rag.ingestion.general_documents.search_results import format_chunk_grounding
from rag.retrieval.db_sqlite import insert_research_path, insert_search_document, get_research_path_by_id
from rag.llms.helper_funcs import citation_hash
from datetime import datetime
from sentence_transformers import SentenceTransformer

def create_research_path(query: str, conn: sqlite3.Connection) -> ResearchPath:
    runtime = datetime.now()
    run_id = runtime.strftime("%Y_%m_%d_%H_%M_%S")
    runtime = runtime.strftime("%Y-%m-%d %H:%M:%S")
    
    research_path = ResearchPath(run_id=run_id,
                                 query=query,
                                 run_time=runtime,
                                 )
    
    insert_research_path(research_path, conn)
    return research_path

def search_research_path(research_id: str,
                         data_conn: sqlite3.Connection,
                         research_conn: sqlite3.Connection,
                         encoder: SentenceTransformer,
                         search_index: Path,
                         search_table: str,
                         number_of_results: int=5,
                         citation_hash_length=6,
                         citation_start_format: str = '[{citation}]',
                         citation_end_format: str = '[{citation}]') -> List[SearchDocument]:
    
    research_path = get_research_path_by_id(research_id, research_conn)
    research_path = ResearchPath(**research_path)
    query_vec = encoder.encode(research_path.query)
    index = lancedb.connect(search_index)
    table = index.open_table(search_table)
    
    search_results = table.search(query_vec) \
        .limit(number_of_results) \
        .select(['id', 'type', 'typeId', 'active', 'source', 'topics',
                 'version_id', 'date', 'title', 'summary',
                 'source_file', 'start_index', 'end_index',
                 'chunk_id', '_distance']) \
        .to_pandas()
    
    search_results['topics'] = search_results['topics'].apply(lambda x: x.tolist())
    
    search_documents = list()
    for index, row in search_results.iterrows():
        row = row.to_dict()
        row['run_id'] = research_path.run_id
        row['result_id'] = f"{row['run_id']}_{row['chunk_id']}_" + \
                           citation_hash(
                               f"{row['title']} {row['chunk_id']}",
                               n_digits=citation_hash_length)
        search_document = SearchDocument(**row)
        search_documents.append(search_document)
    
    for document in search_documents:
        document.grounding = format_chunk_grounding(search_document=document,
                                                    citation_start_format=citation_start_format,
                                                    citation_end_format=citation_end_format,
                                                    passage_separator='\n\n',
                                                    data_conn=data_conn)
    for document in search_documents:
        insert_search_document(document, research_conn)
    
    return search_documents
    
    