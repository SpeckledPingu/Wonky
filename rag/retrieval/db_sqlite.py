from typing import List
import sqlite3
from rag.ingestion.datamodels import Insight, Policy, SearchDocument, ResearchPath
from dataclasses import asdict
import json

def get_research_path_by_id(research_id: str, conn: sqlite3.Connection) -> dict:
    conn.row_factory = sqlite3.Row
    tmp_cursor = conn.cursor()
    tmp_cursor.execute(f"""
        SELECT * FROM research_paths
        WHERE run_id='{research_id}'
        LIMIT 1""")
    result = [dict(row) for row in tmp_cursor.fetchall()][0]
    return result

def get_search_results_by_id(research_id: str, conn: sqlite3.Connection) -> List[dict]:
    conn.row_factory = sqlite3.Row
    tmp_cursor = conn.cursor()
    tmp_cursor.execute(f"""
        SELECT * FROM search_results
        WHERE run_id='{research_id}';""")
    result = [dict(row) for row in tmp_cursor.fetchall()]
    return result

def retrieve_document_from_db(doc_id: str, conn: sqlite3.Connection) -> List[dict]:
    conn.row_factory = sqlite3.Row
    tmp_cursor = conn.cursor()
    tmp_cursor.execute(f"""
        SELECT * FROM sections
        WHERE id='{doc_id}'""")
    result = [dict(row) for row in tmp_cursor.fetchall()]
    return result

def retrieve_segment_from_db(chunk_id: str, conn: sqlite3.Connection) -> List[dict]:
    conn.row_factory = sqlite3.Row
    tmp_cursor = conn.cursor()
    tmp_cursor.execute(f"""
        SELECT * FROM sections
        WHERE chunk_id='{chunk_id}'""")
    result = [dict(row) for row in tmp_cursor.fetchall()]
    return result

def retrieve_passages_by_indexes(doc_id: str, start_index: int, end_index: int, conn: sqlite3.Connection) -> List[dict]:
    conn.row_factory = sqlite3.Row
    tmp_cursor = conn.cursor()
    tmp_cursor.execute(f"""
        SELECT * FROM sections
        WHERE doc_index >= {start_index} AND doc_index <= {end_index} and id = '{doc_id}'""")
    result = [dict(row) for row in tmp_cursor.fetchall()]
    return result

def retrieve_metadata(doc_id: str, conn: sqlite3.Connection) -> dict:
    conn.row_factory = sqlite3.Row
    tmp_cursor = conn.cursor()
    tmp_cursor.execute(f"""
        SELECT * FROM metadata
        WHERE id='{doc_id}'
        LIMIT 1""")
    result = [dict(row) for row in tmp_cursor.fetchall()][0]
    return result

class CitationFormatter():
    def formatter_boxend_section(self, text: str, citation: str):
        return f"""{text.strip()} [{citation}]"""

    def formatter_enclosed_box_section(self, text: str, citation: str):
        return f"""[{citation}]\n{text.strip()}\n[/{citation}]"""

    def formatter_xml_tag_section(self, text: str, citation: str):
        return f"""<{citation}>\n{text.strip()}\n</{citation}>"""

    def formatter_boxend_article(self, sections, citations):
        formatted_sections = list()
        for section, citation in zip(sections, citations):
            formatted_sections.append(self.formatter_boxend_section(section, citation))
        return '\n\n'.join(formatted_sections)

    def formatter_enclosed_box_article(self, sections, citations):
        formatted_sections = list()
        for section, citation in zip(sections, citations):
            formatted_sections.append(self.formatter_enclosed_box_section(section, citation))
        return '\n\n-----\n\n'.join(formatted_sections)

    def formatter_xml_tag_article(self, sections, citations):
        formatted_sections = list()
        for section, citation in zip(sections, citations):
            formatted_sections.append(self.formatter_xml_tag_section(section, citation))
        return '\n\n'.join(formatted_sections)
    
    
    
### Insert functions for the different core extraction datamodels

def insert_insight(insight: Insight, conn: sqlite3.Connection):
    insight_dict = asdict(insight)

    insight_dict['related_citations'] = json.dumps(insight_dict['related_citations'])
    insight_dict['insight_data'] = json.dumps(insight_dict['insight_data'])

    columns = ', '.join(insight_dict.keys())
    placeholders = ', '.join(['?'] * len(insight_dict))

    sql = f"INSERT OR REPLACE INTO insights ({columns}) VALUES ({placeholders})"

    try:
        cursor = conn.cursor()
        cursor.execute(sql, list(insight_dict.values()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def insert_policy(policy: Policy, conn: sqlite3.Connection):
    policy_dict = asdict(policy)

    policy_dict['key_stakeholders'] = json.dumps(policy_dict['key_stakeholders'])
    policy_dict['arguments_in_favor'] = json.dumps(policy_dict['arguments_in_favor'])
    policy_dict['arguments_against'] = json.dumps(policy_dict['arguments_against'])
    policy_dict['locations_in_source'] = json.dumps(policy_dict['locations_in_source'])

    columns = ', '.join(policy_dict.keys())
    placeholders = ', '.join(['?'] * len(policy_dict))

    sql = f"INSERT OR REPLACE INTO policies ({columns}) VALUES ({placeholders})"

    try:
        cursor = conn.cursor()
        # Execute the query with the dictionary values as parameters
        cursor.execute(sql, list(policy_dict.values()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def insert_research_path(doc: ResearchPath, conn: sqlite3.Connection):
    doc_dict = asdict(doc)
    columns = ', '.join(doc_dict.keys())
    placeholders = ', '.join(['?'] * len(doc_dict))

    sql = f"INSERT OR REPLACE INTO research_paths ({columns}) VALUES ({placeholders})"

    try:
        cursor = conn.cursor()
        cursor.execute(sql, list(doc_dict.values()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def insert_search_document(doc: SearchDocument, conn: sqlite3.Connection):
    doc_dict = asdict(doc)

    doc_dict['topics'] = json.dumps(doc_dict['topics'])
    doc_dict['active'] = int(doc_dict['active'])

    columns = ', '.join(doc_dict.keys())
    placeholders = ', '.join(['?'] * len(doc_dict))

    sql = f"INSERT OR REPLACE INTO search_results ({columns}) VALUES ({placeholders})"

    try:
        cursor = conn.cursor()
        cursor.execute(sql, list(doc_dict.values()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")