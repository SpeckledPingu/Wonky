from burr.core import action, State, ApplicationBuilder, ApplicationContext, Action
from pathlib import Path
import re
import json
from rag.llms.google import call_llm as call_llm_flash
from rag.llms.local import Encoder, call_llm
from glue import format_documents
from sentence_transformers import SentenceTransformer
import pandas as pd

from ..processes.glue import parse_report
import torch
from ..prompts.base_prompts import *



# Topic Research Document Parsing Workflow
@action(reads=[], writes=["report_data", "file_name", "file_path"])
def load_report_from_file(state: State, file_path: Path):
    with open(file_path,'r') as f:
        report_data = json.load(f)

    return state.update(report_data=report_data,
                        file_path=str(file_path),
                        file_name=str(file_path.name))

@action(reads=["report_data"], writes=["report","section_markers", "parsing_prompt","summary"])
def llm_segment_and_summarize(state: State) -> State:
    report = state['report_data']['report']
    formatted_parsing_prompt = parsing_prompt.format(report=report)
    sections_and_summary = call_llm_flash(formatted_parsing_prompt)
    document_title = re.search(r"DOCUMENT_TITLE: (.+?)\n", sections_and_summary).group(1)
    document_summary = re.search(r"SUMMARY:\s+(.+)", sections_and_summary, flags=re.DOTALL | re.MULTILINE).group(1).strip('`')
    section_numbers = re.findall(r"SECTION (\d+): (.+?)\n", sections_and_summary)
    section_markers = [('title', document_title)] + section_numbers
    return state.update(report=report, section_markers=section_markers, parsing_prompt=formatted_parsing_prompt, summary=document_summary)

@action(reads=["report","report_data","section_markers","summary"], writes=["parsed_document"])
def parse_report_to_segments(state: State) -> State:
    report = state['report']
    segments = state['section_markers']
    report_data = state['report_data']
    parsed_document = parse_report(report, segments)
    parsed_data = {
        "sections":parsed_document,
        "report":report_data['report'],
        "summary":state['summary'],
        "topic":report_data['topic'],
        "focus":report_data['focus'],
        "relevant_citations":report_data['relevant_citations'],
        "source_file":state['file_path'],
        "source_file_name":state['file_name']
    }
    return state.update(parsed_document=parsed_data)

@action(reads=["parsed_document"], writes=["parsed_document"])
def encode_text(state: State, encoder: SentenceTransformer) -> State:
    parsed_document = state['parsed_document']
    for section in parsed_document['sections']:
        section['section_vector'] = encoder.encode(section['section_text']).tolist()
        torch.mps.empty_cache()

    parsed_document['report_vector'] = encoder.encode(parsed_document['report']).tolist()
    torch.mps.empty_cache()
    parsed_document['summary_vector'] = encoder.encode(parsed_document['summary']).tolist()
    torch.mps.empty_cache()
    return state.update(parsed_document=parsed_document)


### Topic Research Document Generation Components

@action(reads=[], writes=['search_expansion_prompt'])
def search_expansion_prompt_format(state: State, topic: str, focus: str) -> State:
    formatted_prompt = search_expansion_prompt.format(topic=topic,
                                                      focus=focus)
    return state.update(search_expansion_prompt=formatted_prompt)

@action(reads=['search_expansion_prompt'], writes=['search_expansion'])
def search_expansion(state: State) -> State:
    expansion_prompt = state['search_expansion_prompt']
    search_expansion = call_llm(expansion_prompt, model="gemma-3-12b-it@Q8_0")
    search_expansion = re.findall(r'\d+\. (.+?\?)', search_expansion)
    return state.update(search_expansion=search_expansion)

@action(reads=['search_expansion'], writes=['query_expansion'])
def query_expansion(state: State, topic: str, focus: str) -> State:
    queries = list()
    for question in state['search_expansion']:
        expansion_prompt = query_expansion_prompt.format(topic=topic,
                                                         focus=focus,
                                                         question=question)
        query_expansion = call_llm(expansion_prompt, model="gemma-3-12b-it@Q8_0")
        queries.append({'question': question, 'query': query_expansion})
    return state.update(query_expansion=queries)


@action(reads=['query_expansion'], writes=["query_expansion"])
def embed_text(state: State, encoder: SentenceTransformer) -> State:
    query_expansions = list()
    for expansion in state['query_expansion']:
        embedding = encoder.encode(expansion['query'],
                                   padding=False,
                                   show_progress_bar=False).tolist()
        expansion['vector'] = embedding
        query_expansions.append(expansion)
        torch.mps.empty_cache()
    return state.update(query_expansion=query_expansions)

@action(reads=["query_expansion"], writes=["documents"])
def retrieve_documents(state: State, number_of_results: int, table) -> State:
    expansions = state['query_expansion']
    search_results = list()
    for expansion in expansions:
        query_embedding = expansion["vector"]
        sanitized_query = ' '.join(re.findall(r'(\w+)', expansion['query']))
        results = table.search(query_type='hybrid') \
            .vector(query_embedding) \
            .text(sanitized_query) \
            .limit(number_of_results) \
            .select(['id','title','text','summary','section_start','section_end']) \
            .to_pandas()

        if 'score' in results.columns:
            results['report_score'] = results.groupby('id')['score'].transform('max')
        elif '_distance' in results.columns:
            results['score'] = 1 - results['_distance']
            results['report_score'] = results.groupby('id')['score'].transform('max')
        elif '_relevance_score' in results.columns:
            results['report_score'] = results['_relevance_score']
        results = results.sort_values(['report_score','section_start'], ascending=[False,True])
        search_results.append(results.to_dict(orient='records'))

    return state.update(documents=search_results)

@action(reads=["query_expansion", "documents"], writes=["extraction_prompt"])
def build_extraction_prompt(state: State, topic: str, focus: str) -> State:
    extraction_prompts = list()
    for _expansion, _documents in zip(state['query_expansion'], state['documents']):
        formatted_documents = format_documents(_documents)
        # print(_expansion)
        prompt = extraction_prompt.format(question=_expansion['question'],
                                          topic=topic,
                                          focus=focus,
                                          documents=formatted_documents)
        extraction_prompts.append(prompt)
    return state.update(extraction_prompt=extraction_prompts)


@action(reads=["extraction_prompt"], writes=["extraction"])
def generate_extraction(state: State) -> State:
    extractions = list()
    for _expansion_prompt in state['extraction_prompt']:
        extraction = call_llm_flash(_expansion_prompt)
        extractions.append(extraction)
    return state.update(extraction=extractions)


@action(reads=["extraction","documents"], writes=["report_grounding", "relevant_citations"])
def merge_grounding(state: State) -> State:
    retrieved_documents = list()
    for result_set in state['documents']:
        retrieved_documents.extend(result_set)
    retrieved_documents = pd.DataFrame(retrieved_documents)
    retrieved_documents = retrieved_documents.drop_duplicates(subset=['id','section_start'], keep='first')
    retrieved_documents = retrieved_documents.sort_values(by=['id','section_start'], ascending=[False,True])
    retrieved_documents = retrieved_documents.to_dict(orient='records')

    relevant_citations = ""
    for extraction in state['extraction']:
        relevant_citations += f", {extraction}"
    relevant_citations = sorted(list(set(re.findall(r'(\w+\(\d+\))', relevant_citations))))

    relevant_sections = list()
    for row in retrieved_documents:
        for citation in relevant_citations:
            if citation in row['text']:
                relevant_sections.append(row)
                break

    relevant_sections = pd.DataFrame(relevant_sections)
    relevant_sections = relevant_sections.drop_duplicates(subset=['id','section_start'], keep='first')
    relevant_sections = relevant_sections.sort_values(by=['id','section_start'], ascending=[False,True])
    relevant_sections = relevant_sections.to_dict(orient='records')

    return state.update(report_grounding=relevant_sections, relevant_citations=relevant_citations)

@action(reads=["report_grounding"], writes=["formatted_report_grounding", "report_prompt"])
def format_report_prompt(state: State, topic: str, focus: str) -> State:
    grounding = state['report_grounding']
    formatted_grounding = format_documents(grounding)
    formatted_prompt = report_prompt.format(topic=topic,focus=focus, sources=formatted_grounding)
    return state.update(formatted_report_grounding=formatted_grounding, report_prompt=formatted_prompt)

@action(reads=["report_prompt"], writes=["report"])
def generate_report(state: State) -> State:
    # report = call_llm(state['report_prompt'], model="gemma-3-12b-it@Q8_0")
    report = call_llm_flash(state['report_prompt'])
    report = report.replace('$','\\$')
    return state.update(report=report)