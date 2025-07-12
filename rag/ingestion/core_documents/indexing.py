import gzip
import pandas as pd
import json
import lancedb
def load_data(file_path):
    with gzip.open(file_path ,'rt') as f:
        data = json.load(f)
    return data

def prep_document_segments(sections_df):
    '''
    sections_df is an expanded dataframe of the metadata and specific section dictionary
    The sections column is the section data, while the section_df contains useful information about the chunk
    :param sections_df:
    :return:
    '''
    sections = list()
    for _section in sections_df:
        _section_data = _section['sections']
        _section_data['start_index'] = _section['start_index']
        _section_data['end_index'] = _section['end_index']
        _section_data['chunk_id'] = _section['chunk_id']
        _section_data['id'] = _section['id']
        sections.append(_section_data)
    return sections

def separate_data(data):
    data = pd.DataFrame(data)
    data['version_id'] = data['version_id'].astype(str)
    data['chunk_id'] = data.apply(lambda row: f"{row['id']}_{row['start_index']}_{row['end_index']}", axis=1)
    data = data.drop_duplicates(subset=['chunk_id'])
    
    metadata_df = data[['id' ,'type' ,'typeId' ,'number' ,'active' ,'source' ,'topics' ,'version_id' ,'date' ,'title' ,'summary'
         ,'source_file']]
    metadata_df['topics'] = metadata_df['topics'].str.join(',')
    print(metadata_df.shape)
    metadata_df = metadata_df.drop_duplicates()
    print(metadata_df.shape)
    
    text_df = data[['id' ,'title' ,'passage_text' ,'start_index' ,'end_index' ,'chunk_id' ,'vector']].copy()
    text_df['vector'] = text_df['vector'].apply(lambda vector: ','.join([str(x) for x in vector]))
    
    sections_df = data[['sections' ,'start_index' ,'end_index' ,'chunk_id' ,'id']].copy()
    sections_df = sections_df.explode('sections').to_dict(orient='records')
    sections_df = prep_document_segments(sections_df)
    sections_df = pd.DataFrame(sections_df)
    return metadata_df, text_df, sections_df


def load_to_sql(dataframe, table_name, conn):
    dataframe.to_sql(table_name, conn, if_exists='replace')


def ingest_data_to_sql(data, conn):
    metadata_df, text_df, sections_df = separate_data(data)
    load_to_sql(metadata_df, 'metadata', conn)
    load_to_sql(text_df, 'text', conn)
    load_to_sql(sections_df, 'sections', conn)


def ingest_data_to_lancedb(data, table_name, index_path):
    index = lancedb.connect(index_path)
    if table_name in index.table_names():
        index.drop_table(table_name)
    table = index.create_table(table_name, data=data)
    table.create_index(metric='cosine')
    table.create_fts_index(['id', 'typeId', 'title', 'summary', 'passage_text', 'chunk_id'], replace=True)