from typing import List
import hashlib
import re
from fuzzy_json import loads as fuzzy_loads



def citation_hash(source_string: str, n_digits: int = 6) -> str:
    hash_object = hashlib.sha256(source_string.encode())
    hex_digest = hash_object.hexdigest()
    hash_int = int(hex_digest, 16)
    numeric_id = hash_int % (10**n_digits)
    return f"{numeric_id:0{n_digits}d}"


def convert_response_to_json(response_text: str) -> List[dict]:
    '''

    :param response_text: string response from the llm that only has json data either formatted with ```json...```, or ONLY json data
    :return: list of extracted items
    '''
    json_re = re.compile(r'```json(.+?)```', flags=re.DOTALL)
    if json_re.search(response_text):
        json_text = json_re.search(response_text).group(1)
    else:
        json_text = response_text
    response_json = fuzzy_loads(json_text)
    return response_json

def create_citation(item: dict, fields: List[str], prefix='INST_', number_of_digits=6):
    citation_string = ""
    for field in fields:
        citation_string += f" {field}: {item[field]}"
    citation_number = citation_hash(citation_string, n_digits=number_of_digits)
    return f"{prefix}{citation_number}"

def create_batches(batch_items: List, batch_size: int, batch_flex: int = 1) -> List[dict]:
    '''
    Keeping this simple and easy to read
    :param batch_items: A list of items that you want to batch
    :param batch_size: How big the batch size is
    :param batch_flex: At what divisor should be applied to the batch size be stepped down to avoid a batch of a single item
        e.g. a batch size of 5 and the last batch is 2, then you will have two batches of 4 and 3. If 6 remain, then 3 and 3
        This is future functionality to build in.
    :return: list of batch items
    '''
    number_of_items = len(batch_items)
    batches = list()
    for start in range(0, number_of_items, batch_size):
        batch = batch_items[start:start+batch_size]
        batches.append(batch)
    return batches