from copy import deepcopy
import re
from tqdm import tqdm
import torch

metadata_fields = ['id', 'type', 'typeId', 'number', 'active', 'source', 'topics', 'version_id', 'date', 'retrieved_date', 'title', 'summary', 'source_file']

def format_chunks(chunks):
    markdown_text = list()
    for chunk in chunks:
        if 'heading' in chunk['type']:
            heading_strength = int(chunk['type'].split('_')[1])
            markdown_text.append("#"* heading_strength + ' ' + chunk['content'].strip() + '\n')
        if 'table' in chunk['type']:
            continue
        else:
            # Remove any trailing footnote numbers
            # markdown_text.append(f"[{chunk['citation']}]\n" + chunk['content'].rstrip('0123456789').strip() + f"\n[/{chunk['citation']}]\n")
            # Only vectorized_text
            raw_text = chunk['content'].strip()
            if '#_Toc' in raw_text:
                continue
            raw_text = re.sub(r'(http:[\w\W]+?)\)','',raw_text.strip())
            raw_text = re.sub(r'(\[|\])',' ', raw_text)
            raw_text = re.sub(r'(\(\))',' ', raw_text)
            raw_text = re.sub(r'(\s+)',' ',raw_text.strip())
            markdown_text.append(f"{raw_text.strip()}")
    return '\n'.join(markdown_text)


def split_chunks(document, metadata_fields):
    '''
    As part of the vectorization process (currently) the specific metadata around the document indexes
    is managed here instead of the parsing.
    Refactor will migrate all of these into separate segmenters
    :param document:
    :param metadata_fields:
    :return:
    '''
    passages = list()
    metadata = {k:v for k, v in document.items() if k in metadata_fields}
    for _chunk in document['chunks']:
        start_index = min([x['doc_index'] for x in _chunk])
        end_index = max([x['doc_index'] for x in _chunk])
        formatted_chunk = format_chunks(_chunk)
        passage_metadata = deepcopy(metadata)
        passage_metadata['passage_text'] = formatted_chunk
        passage_metadata['sections'] = deepcopy(_chunk)
        passage_metadata['start_index'] = start_index
        passage_metadata['end_index'] = end_index
        passages.append(passage_metadata)
    return passages


def vectorize_crs(data, encoder):
    vectorized_chunks = list()
    for document in tqdm(data):
        passages = split_chunks(document, metadata_fields)
        # print(len(passages))
        for passage in passages:
            passage['vector'] = encoder.encode(passage['passage_text'])
            torch.mps.empty_cache()
        vectorized_chunks.extend(passages)
    return vectorized_chunks