from typing import List
from app import schemas
from app.search.base import SearchIndex
from app.converters import convert_dataframe_to_pydantic
from sentence_transformers import SentenceTransformer
import lancedb
import pandas as pd
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables to get file paths
load_dotenv("/Users/jameslittiebrant/DataspellProjects/Mycroft/notebooks/env_var")
project_folder = Path(os.environ['PROJECT_FOLDER'])
index_folder_path = project_folder.joinpath('indexes')

extraction_index_path = project_folder.joinpath(f'indexes/extractions')
policies_table_name = 'policies'
insight_table_name = 'insights'

class LanceDBIndex(SearchIndex):
    """
    Implementation of the SearchIndex that connects to real LanceDB indexes.
    """
    
    def __init__(self, encoder: SentenceTransformer):
        """
        The constructor now accepts a sentence encoder model.
        """
        self.encoder = encoder
        print("Initialized LanceDB Index with Sentence Encoder.")
    
    def search_documents(self, project_id: int, query: schemas.SearchQuery) -> List[schemas.RawSearchResult]:
        print(f"[LanceDB] Searching documents in index 'crs_reports' for: '{query.query}'")
        
        try:
            db = lancedb.connect(index_folder_path.joinpath('crs_reports'))
            table = db.open_table('sections')
        except Exception as e:
            print(f"Error connecting to LanceDB or opening table: {e}")
            return []
        
        query_vector = self.encoder.encode(query.query)
        results_df = table.search(query_vector).limit(10).to_pandas()
        
        # Use the converter to map the DataFrame to the RawSearchResult schema
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
        print(f"Found {len(raw_results)} raw results from LanceDB documents index.")
        return raw_results
    
    def search_extractions(self, project_id: int, query: schemas.ExtractionSearchQuery) -> List[schemas.RawSearchResult]:
        print(f"[LanceDB] Searching extractions in index 'insights' for: '{query.query}'")

        try:
            # Connect to the different index for extractions
            db = lancedb.connect(extraction_index_path)
            table = db.open_table(insight_table_name)
        except Exception as e:
            print(f"Error connecting to LanceDB or opening table: {e}")
            return []

        query_vector = self.encoder.encode(query.query)
        results_df = table.search(query_vector).limit(10).to_pandas()
        print(results_df.columns)
        
        raw_results = convert_dataframe_to_pydantic(
            results_df,
            schemas.RawSearchResult,
            field_mapping={
                'citation': 'id',
                'insight_name': 'title',
                'insight_text': 'content',
                'insight_type': 'tags'
            }
        )
        
        print(f"Found and mapped {len(raw_results)} extractions to the common search format.")
        return raw_results
