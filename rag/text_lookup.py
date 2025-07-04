import pandas as pd
import sqlite3


def get_sections_by_id(id: str, conn: sqlite3.Connection):
    lookup_df = pd.read_sql(f"""
SELECT * FROM sections
WHERE id='{id}'""", conn)
    return lookup_df

def get_sections_by_chunk(chunk_id: str, conn: sqlite3.Connection):
    lookup_df = pd.read_sql(f"""
SELECT * FROM sections
WHERE chunk_id='{chunk_id}'""", conn)
    return lookup_df

def get_sections_by_indexes(id: str, start_index: int, end_index: int, conn: sqlite3.Connection):
    lookup_df = pd.read_sql(f"""
        SELECT * FROM sections
        WHERE doc_index >= {start_index} AND doc_index <= {end_index} and id = '{id}'""", conn)
    return lookup_df

def get_text_by_id(id: str, conn: sqlite3.Connection):
    lookup_df = pd.read_sql(f"""
    SELECT * FROM text
    WHERE id='{id}'""", conn)
    return lookup_df

def get_text_by_chunk_id(chunk_id: str, conn: sqlite3.Connection):
    lookup_df = pd.read_sql(f"""
    SELECT * FROM text
    WHERE chunk_id='{chunk_id}'""", conn)
    return lookup_df

def get_text_by_indexes(id: str, start_index: int, end_index: int, conn: sqlite3.Connection):
    lookup_df = pd.read_sql(f"""
    SELECT * FROM text
    WHERE id='{id}' AND start_index >= {start_index} AND end_index <= {end_index}""", conn)
    return lookup_df

def get_text_by_indexes_expansion(id: str, start_index: int, end_index: int, conn: sqlite3.Connection):
    lookup_df = pd.read_sql(f"""
    SELECT * FROM text
    WHERE id='{id}'
    AND
    (
        (start_index <= {start_index} AND end_index >= {start_index})
        OR
        (start_index <= {end_index} AND end_index >= {end_index})
        OR
        (start_index >= {start_index} AND end_index <= {end_index})
    )
    """, conn)
    return lookup_df

def get_text_by_indexes_sections(id: str, start_index: int, end_index: int, conn: sqlite3.Connection):
    lookup_df = pd.read_sql(f"""
    SELECT * from sections
    WHERE
    id='{id}'
    AND
    doc_index >= {start_index} AND doc_index <= {end_index}""", conn)
    return lookup_df

def get_full_article_text(id: str, conn: sqlite3.Connection):
    df = get_text_by_id(id, conn)
    text = CitationFormatter().formatter_xml_tag_article(df['passage_text'].to_list(), df['chunk_id'].to_list())
    return text

def get_chunk_text_by_indexes(id: str, start_index: int, end_index: int, conn: sqlite3.Connection):
    df = get_text_by_indexes(id, start_index, end_index, conn)
    text = CitationFormatter().formatter_xml_tag_article(df['passage_text'].to_list(), df['chunk_id'].to_list())
    return text

def get_chunk_text_by_indexes_expansion(id: str, start_index: int, end_index: int, conn: sqlite3.Connection):
    df = get_text_by_indexes_expansion(id, start_index, end_index, conn)
    text = CitationFormatter().formatter_xml_tag_article(df['passage_text'].to_list(), df['chunk_id'].to_list())
    return text

def get_section_text_by_indexes(id: str, start_index, end_index, conn: sqlite3.Connection):
    df = get_text_by_indexes_sections(id, start_index, end_index, conn)
    print(df.columns)
    text = CitationFormatter().formatter_xml_tag_article(df['content'].to_list(), df['citation'].to_list())
    return text

def make_on_the_fly_citations(base_citation: str, start_index: int, number_of_records: int, connector='_'):
    return [f"""{base_citation}{connector}{_idx}""" for _idx in range(start_index, start_index+number_of_records)]

def get_section_text_by_indexes_otf_citation(id: str, start_index: int, end_index, conn: sqlite3.Connection, otf_connector='_', reset_index=True):
    df = get_text_by_indexes_sections(id, start_index, end_index, conn)
    if reset_index:
        otf_citations = make_on_the_fly_citations(base_citation=id, start_index=0, number_of_records=len(df), connector=otf_connector)
    else:
        otf_citations = make_on_the_fly_citations(base_citation=id, start_index=start_index, number_of_records=len(df), connector=otf_connector)
    text = CitationFormatter().formatter_xml_tag_article(df['content'].to_list(), otf_citations)
    return text

def get_section_text_by_indexes_otf_citation_reset(id: str, start_index: int, end_index, conn: sqlite3.Connection, otf_connector='_'):
    df = get_text_by_indexes_sections(id, start_index, end_index, conn)
    otf_citations = make_on_the_fly_citations(base_citation=id, start_index=0, number_of_records=len(df), connector=otf_connector)
    text = CitationFormatter().formatter_xml_tag_article(df['content'].to_list(), otf_citations)
    return text

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