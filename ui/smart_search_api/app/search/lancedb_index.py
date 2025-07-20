from typing import List
from app import schemas
from app.search.base import SearchIndex
from app.converters import convert_dataframe_to_pydantic
from sentence_transformers import SentenceTransformer
import lancedb
import pandas as pd  # Import pandas for DataFrame creation

from dotenv import load_dotenv
import os
from pathlib import Path
import sqlite3

load_dotenv("/Users/jameslittiebrant/DataspellProjects/Mycroft/notebooks/env_var")

# This is a mock implementation. In a real scenario, you would import lancedb
# and connect to your database here.
# import lancedb
data_folder = Path(os.environ['DATA_FOLDER'])
project_folder = Path(os.environ['PROJECT_FOLDER'])
research_json_folder = project_folder.joinpath('research_json')
database_location = project_folder.joinpath('databases')

research_database_name = "research.sqlite"
document_database_name = "documents.sqlite"
insight_db_sql = 'insights'
search_result_table_sql = 'search_results'
metadata_table_sql = 'metadata'
data_conn = sqlite3.connect(database_location.joinpath(document_database_name))
research_conn = sqlite3.connect(database_location.joinpath(research_database_name))

index_sr_location = 'crs_reports'
table_sr_name = 'sections'
index_folder = project_folder.joinpath(f'indexes/{index_sr_location}')


class LanceDBIndex(SearchIndex):
    """
    A mock implementation of the SearchIndex that uses a sentence encoder.
    """
    
    def __init__(self, encoder: SentenceTransformer):
        """
        The constructor now accepts a sentence encoder model.
        """
        self.db = lancedb.connect(index_folder)
        self.encoder = encoder
        print("Initialized Mock LanceDB Index with Sentence Encoder.")
    
    def search_documents(self, project_id: int, query: schemas.SearchQuery) -> List[schemas.RawSearchResult]:
        print(f"[LanceDB] Encoding query for documents in project {project_id}: '{query.query}'")
        
        query_vector = self.encoder.encode(query.query)
        print(f"[LanceDB] Query vector created with shape: {query_vector.shape}")
        
        table = self.db.open_table(table_sr_name)
        results_df = table.search(query_vector).limit(10).to_pandas()
        
        # --- FIX: Convert the DataFrame to the RawSearchResult schema ---
        # This ensures the data is in the correct format before being sent to the CRUD layer.
        raw_results = convert_dataframe_to_pydantic(
            results_df,
            schemas.RawSearchResult,
            field_mapping={
                'id': 'id',
                'title': 'title',
                'passage_text': 'content',
                'topics': 'tags'
            }
        )
        print(f"Found {len(raw_results)} raw results from LanceDB.")
        return raw_results
    
    def search_extractions(self, project_id: int, query: schemas.ExtractionSearchQuery) -> List[schemas.Extraction]:
        print(f"[LanceDB] Encoding query for extractions in project {project_id}: '{query.query}'")
        
        query_vector = self.encoder.encode(query.query)
        print(f"[LanceDB] Query vector created with shape: {query_vector.shape}")
        
        # This part still uses mock data and would need a similar implementation
        return [
            schemas.Extraction(id='ext-001', source_doc_id='doc-001', type='insight', stance='pro',
                               content='LanceDB found an insight about AI.')
        ]
