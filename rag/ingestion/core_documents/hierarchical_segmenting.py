## Initial sketches for parsing html to stratified markdown in json
## This still needs work on recall for all crs reports and fall backs.
## This will be developed for CRS reports and then split into CRS report specific and this general
## Document segmentation strategy.

from collections import Counter
from bs4 import BeautifulSoup

def convert_to_markdown(element):
    text = ''
    if isinstance(element, str):
        return element

    if not hasattr(element, 'contents'):
        return ''

    for child in element.contents:
        if isinstance(child, str):
            text += child
        elif child.name in ['strong', 'b']:
            text += f"**{convert_to_markdown(child)}**"
        elif child.name in ['em', 'i']:
            text += f"*{convert_to_markdown(child)}*"
        elif child.name == 'a':
            link_text = convert_to_markdown(child).strip()
            href = child.get('href', '')
            text += f"[{link_text}]({href})"
        elif child.name == 'span':
            # Do not process span as any character.
            text += convert_to_markdown(child)
        else:
            text += child.get_text(strip=True)
    return text

def parse_html_content(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    structured_content = []

    # Outer elements that indicate different main structures
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'table', 'ul', 'ol']):
        # Skip elements that are parents of other processed elements to avoid duplication
        if element.find_parent(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'table', 'ul', 'ol', 'li']):
             continue

        # Process based on the tag type
        if element.name.startswith('h'):
            structured_content.append({
                'type': f'heading_{element.name[1]}',
                'content': element.get_text(strip=True)
            })
        elif element.name == 'p':
            markdown_content = convert_to_markdown(element).strip()

            # Only add non-empty paragraphs
            if markdown_content:
                structured_content.append({
                    'type': 'paragraph_markdown',
                    'content': markdown_content
                })
        elif element.name == 'div' and element.get_text(strip=True) and not element.find(['h1', 'h2', 'h3', 'p', 'table', 'ul', 'ol']):
             structured_content.append({
                'type': 'div_text',
                'content': element.get_text(strip=True)
             })
        elif element.name == 'table':
            markdown_table = ""
            rows = element.find_all('tr')
            for i, row in enumerate(rows):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                markdown_table += "| " + " | ".join(cells) + " |\n"
                if i == 0:
                    markdown_table += "| " + " | ".join(['---'] * len(cells)) + " |\n"

            structured_content.append({
                'type': 'table_markdown',
                'content': markdown_table
            })
        elif element.name == 'ul':
            markdown_list = ""
            for item in element.find_all('li', recursive=False):
                item_content = convert_to_markdown(item).strip()
                markdown_list += f"- {item_content}\n"

            structured_content.append({
                'type': 'list_markdown',
                'content': markdown_list
            })
        elif element.name == 'ol':
            markdown_list = ""
            for i, item in enumerate(element.find_all('li', recursive=False)):
                 item_content = convert_to_markdown(item).strip()
                 markdown_list += f"{i+1}. {item_content}\n"

            structured_content.append({
                'type': 'list_markdown',
                'content': markdown_list
            })


    return structured_content


## Initial Chunker -> about a 50% loss
def count_words_in_chunk(chunk):
    count = 0
    for item in chunk:
        # Split content by whitespace to count words
        count += len(item.get('content', '').split())
    return count

# --- Original Hierarchical Chunker Logic (from the first script) ---
# This part is included to make the example runnable. In a real pipeline,
# you would import this function or run the scripts sequentially.

def hierarchical_chunker_recursive(current_chunk, level, max_words, buffer):
    final_chunks = []
    heading_tag = f'heading_{level}'
    has_headings_at_this_level = any(item['type'] == heading_tag for item in current_chunk)

    if not has_headings_at_this_level:
        return [current_chunk]

    sub_groups = []
    current_group = []
    first_heading_index = -1
    for i, item in enumerate(current_chunk):
        if item['type'] == heading_tag:
            first_heading_index = i
            break

    if first_heading_index > 0:
        initial_group = current_chunk[:first_heading_index]
        word_count = count_words_in_chunk(initial_group)
        if word_count > max_words + buffer:
            deeper_chunks = hierarchical_chunker_recursive(initial_group, level + 1, max_words, buffer)
            final_chunks.extend(deeper_chunks)
        else:
            final_chunks.append(initial_group)
        remaining_items = current_chunk[first_heading_index:]
    else:
        remaining_items = current_chunk

    for item in remaining_items:
        if item['type'] == heading_tag:
            if current_group:
                sub_groups.append(current_group)
            current_group = [item]
        else:
            current_group.append(item)

    if current_group:
        sub_groups.append(current_group)

    for group in sub_groups:
        word_count = count_words_in_chunk(group)
        if word_count <= max_words + buffer:
            final_chunks.append(group)
        else:
            deeper_chunks = hierarchical_chunker_recursive(group, level + 1, max_words, buffer)
            final_chunks.extend(deeper_chunks)

    return final_chunks

def chunk_document(data, max_words, buffer, target_level=1):
    return hierarchical_chunker_recursive(data, target_level, max_words, buffer)


# --- Chunk Merging Logic ---

def merge_chunks(chunks, target_word_count):
    """
    Merges smaller chunks together to reach a target word count.

    This function iterates through a list of chunks and combines adjacent ones
    as long as the combined word count does not exceed the target.

    Args:
        chunks (list): A list of chunks, where each chunk is a list of content items.
        target_word_count (int): The desired word count for the merged chunks.

    Returns:
        list: A new list of merged chunks.
    """
    if not chunks:
        return []

    merged_chunks = []
    # Start with the first chunk
    current_merged_chunk = list(chunks[0])
    current_word_count = count_words_in_chunk(current_merged_chunk)

    # Iterate through the rest of the chunks
    for next_chunk in chunks[1:]:
        next_chunk_word_count = count_words_in_chunk(next_chunk)

        # If adding the next chunk doesn't exceed the target, merge it
        if current_word_count + next_chunk_word_count <= target_word_count:
            current_merged_chunk.extend(next_chunk)
            current_word_count += next_chunk_word_count
        else:
            # Otherwise, finalize the current merged chunk
            merged_chunks.append(current_merged_chunk)
            # And start a new one with the next chunk
            current_merged_chunk = list(next_chunk)
            current_word_count = next_chunk_word_count

    # Don't forget to add the last processed chunk
    if current_merged_chunk:
        merged_chunks.append(current_merged_chunk)

    return merged_chunks


# --- Citation Logic ---

def add_citations(chunks, base_citation):
    """
    Adds a unique citation to each passage within each chunk.

    The function iterates through each chunk and each passage, adding a
    'citation' field in the format of "[base_citation_chunk_id__passage_id]".

    Args:
        chunks (list): A list of chunks.
        base_citation (str): The base string to use for citations.

    Returns:
        list: The list of chunks with citations added to each passage.
    """
    cited_chunks = []
    # Enumerate from 1 to get human-readable chunk IDs
    for chunk_id, chunk in enumerate(chunks, 1):
        new_chunk = []
        # Enumerate from 1 for passage IDs within the chunk
        for passage_id, passage in enumerate(chunk, 0):
            # Create a copy to avoid modifying the original data in place.
            # This preserves all existing fields, including 'doc_index'.
            new_passage = passage.copy()
            new_passage['citation'] = f"{base_citation}_{chunk_id}__{passage_id}"
            new_chunk.append(new_passage)
        cited_chunks.append(new_chunk)
    return cited_chunks

def find_highest_heading(passages, min_necessary=1):
    passage_counts = Counter([x['type'] for x in passages])
    possible_headings = [passage for passage, _count in passage_counts.items() if _count > min_necessary]
    possible_headings = [x for x in possible_headings if 'heading' in x]
    possible_headings = [int(x.split('_')[1]) for x in possible_headings]
    return min(possible_headings)

def skip_heading_1(passages, min_necessary=1):
    passage_counts = Counter([x['type'] for x in passages])
    possible_headings = {passage_type:_count for passage_type, _count in passage_counts.items() if 'heading' in passage_type}
    if len(possible_headings) == 0:
        return 0
    if possible_headings.get('heading_1', 0):
        if possible_headings.get('heading_1') > min_necessary:
            return 1
        else:
            _min_header = min([int(passage_type.split('_')[1]) for passage_type in possible_headings.keys()])
            return _min_header
    return -1


### Simple Chunker

def simple_chunker(data, target_word_count):
    """
    Chunks a document by greedily adding passages until a target word count is reached.
    This does not rely on any hierarchical structure.

    Args:
        data (list): The list of passages from the document.
        target_word_count (int): The approximate word count for each chunk.

    Returns:
        list: A list of chunks.
    """
    if not data:
        return []

    chunks = []
    current_chunk = []
    current_word_count = 0

    for passage in data:
        passage_word_count = count_words_in_chunk([passage])

        # If the current chunk is not empty and adding the next passage would
        # exceed the target, finalize the current chunk.
        if current_chunk and (current_word_count + passage_word_count > target_word_count):
            chunks.append(current_chunk)
            # Start a new chunk
            current_chunk = []
            current_word_count = 0

        # Add the passage to the current (or new) chunk.
        current_chunk.append(passage)
        current_word_count += passage_word_count

    # Add the last remaining chunk if it exists.
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def parse_report_metadata(metadata):
    parsed_metadata = dict()
    parsed_metadata['id'] = metadata['id']
    parsed_metadata['type'] = metadata['type']
    parsed_metadata['typeId'] = metadata['typeId']
    parsed_metadata['number'] = metadata['number']
    parsed_metadata['active'] = metadata['active']
    parsed_metadata['source'] = metadata['source']
    parsed_metadata['topics'] = metadata['topics']
    _version_info = metadata['versions'][0]
    parsed_metadata['version_id'] = _version_info['id']
    parsed_metadata['date'] = _version_info['date']
    parsed_metadata['retrieved_date'] = _version_info['retrieved']
    parsed_metadata['title'] = _version_info['title']
    parsed_metadata['summary'] = _version_info['summary']
    parsed_metadata['source_file'] = [x for x in _version_info['formats'] if x['format'] == 'HTML'][0]['filename']
    return parsed_metadata





### General script for parsing
# # BASE_CITATION = "RL31572"
# # Config for the initial splitting phase
# INITIAL_MAX_WORDS = 800
# INITIAL_BUFFER = 1300
# MINIMUM_NECESSARY_HEADINGS = 1
# # Config for the merging phase
# TARGET_MERGE_WORD_COUNT = 1500
# TARGET_CHUNK_WORDS = 1500

# errored_files = list()
# re_parse_files = list()
# parsed_data = list()
# total_chunks = 0
# total_parsed_chunks = 0
# start_point = len(errored_files) + len(parse_report_metadata(data))
# for json_file in tqdm(json_files[start_point:]):
#     did_load, html_document, metadata = load_file(json_file)
#     if not did_load:
#         with open(json_file, 'r', encoding='utf-8') as f:
#             _error_data = json.load(f)
#         errored_files.append({'filename': json_file.name, 'json':_error_data, 'error':'error_loading'})
#         continue
#
#     if len(html_document.strip()) == 0:
#         print('no html')
#         with open(json_file, 'r', encoding='utf-8') as f:
#             _error_data = json.load(f)
#         errored_files.append({'filename': json_file.name, 'json':_error_data, 'error':'no_html'})
#         continue
#
#     metadata = parse_report_metadata(metadata)
#     document_data_raw = parse_html_content(html_document)
#     document_data = []
#     for i, passage in enumerate(document_data_raw):
#         passage['doc_index'] = i
#         document_data.append(passage)
#     if len(document_data) == 0:
#         errored_files.append({'filename': json_file.name, 'json':metadata, 'error':'no_parsed_data'})
#         continue
#     # --- Step 1: Perform the initial hierarchical chunking ---
#     highest_heading = skip_heading_1(document_data, min_necessary=MINIMUM_NECESSARY_HEADINGS)
#     if highest_heading > 0:
#         initial_chunks = chunk_document(document_data, INITIAL_MAX_WORDS, INITIAL_BUFFER, target_level=highest_heading)
#     else:
#         initial_chunks = simple_chunker(document_data, TARGET_CHUNK_WORDS)
#
#     total_parsed_chunks += len(initial_chunks)
#     # initial_chunks = chunk_document(document_data, INITIAL_MAX_WORDS, INITIAL_BUFFER, target_level=highest_heading)
#     # print(f"Step 1: Document initially split into {len(initial_chunks)} chunks.\n")
#
#     # --- Step 2: Perform the merging post-processing ---
#     final_merged_chunks = merge_chunks(initial_chunks, TARGET_MERGE_WORD_COUNT)
#     total_chunks += len(final_merged_chunks)
#     # print("---" * 15)
#     # print(f"\nStep 2: Merged into {len(final_merged_chunks)} final chunks.")
#     # print(f"Target Merge Size: {TARGET_MERGE_WORD_COUNT} words\n")
#
#     # --- Step 3: Add citations to the final chunks ---
#     final_cited_chunks = add_citations(final_merged_chunks, metadata['id'])
#     metadata['chunks'] = final_cited_chunks
#     metadata['initial_chunks'] = initial_chunks
#     parsed_data.append(metadata)
#     # print("---" * 15)
#     # print(f"\nStep 3: Added citations to {len(final_cited_chunks)} chunks.")
#     # print(f"Base Citation: '{BASE_CITATION}'\n")
#     #
#     # # --- Output and Verification ---
#     # print("---" * 15)
#     # print("\nFinal Output Verification:\n")
#     # total_word_count = 0
#     # for i, chunk in enumerate(final_cited_chunks):
#     #     word_count = count_words_in_chunk(chunk)
#     #     total_word_count += word_count
#     #
#     #     first_item_type = chunk[0].get('type', 'N/A')
#     #     first_item_content = chunk[0].get('content', '').replace('\n', ' ')[:70]
#     #     first_item_citation = chunk[0].get('citation', 'N/A')
#     #     first_item_doc_index = chunk[0].get('doc_index', -1)
#     #
#     #     print(f"--- Final Chunk {i+1} ---")
#     #     print(f"  Word Count: {word_count}")
#     #     print(f"  Items: {len(chunk)}")
#     #     print(f"  Starts with '{first_item_type}': \"{first_item_content}...\"")
#     #     print(f"  First Citation: {first_item_citation}")
#     #     print(f"  First Doc Index: {first_item_doc_index}")
#     #     print()
#     #
#     # print(f"Total word count across all final chunks: {total_word_count}")
#     # print(f"Total word count in original document: {count_words_in_chunk(document_data)}")
#
