import re
from rag.ingestion.datamodels import SearchDocument
import sqlite3
from rag.retrieval.db_sqlite import retrieve_passages_by_indexes, retrieve_metadata


def format_passages_w_citation_crs(passages: list,
                                   citation_start_format: str = '',
                                   citation_end_format:str = '',
                                   separator: str = '\n') -> str:
    '''

    :param passages:
    :param citation_start_format:
    :param citation_end_format:
    :param separator:
    :return:
    '''
    if citation_start_format == '':
        citation_start_format = "[{citation}]"
    if citation_end_format == '':
        citation_end_format = "[{citation}]"
    
    chunk_text = list()
    passages = sorted(passages, key=lambda passage: passage['start_index'])
    for row in passages:
        citation_start = citation_start_format.format(citation=row['citation'])
        citation_end = citation_end_format.format(citation=row['citation'])
        citation_start = citation_start + '\n'
        if 'heading' in row['type']:
            heading_size = re.search(r'heading_(\d+)', row['type'])
            if heading_size:
                heading_size = int(heading_size.group(1))
                heading = '#'*heading_size + ' '
        else:
            heading = ''

        chunk_text.append(f"{citation_start}{heading}{row['content']}\n{citation_end}")
    chunk_text = separator.join(chunk_text)
    return chunk_text

def format_document_metadata(metadata) -> str:
    '''

    :param metadata:
    :return:
    '''
    article_heading = f"""# *Article ID:* {metadata['id']}\n# *Article Title:* {metadata['title']}"""
    return article_heading

def format_chunk_grounding(search_document: SearchDocument,
                           citation_start_format:str,
                           citation_end_format:str,
                           passage_separator: str,
                           data_conn: sqlite3.Connection) -> str:
    '''

    :param search_results:
    :param citation_start_format:
    :param citation_end_format:
    :param passage_separator:
    :param data_conn:
    :return:
    '''
    # chunk_id = search_document.chunk_id
    chunk_start = search_document.start_index
    chunk_end = search_document.end_index
    doc_id = search_document.id

    passages = retrieve_passages_by_indexes(doc_id=doc_id,
                                            start_index=chunk_start,
                                            end_index=chunk_end,
                                            conn=data_conn)
    passage_text = format_passages_w_citation_crs(passages,
                                                  citation_start_format,
                                                  citation_end_format,
                                                  separator=passage_separator)
    metadata = retrieve_metadata(doc_id=doc_id, conn=data_conn)
    metadata_text = format_document_metadata(metadata)
    document_text = f"""{metadata_text}\n{passage_text}"""
    return document_text