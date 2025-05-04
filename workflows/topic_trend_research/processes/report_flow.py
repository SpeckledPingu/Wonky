from burr.core import action, State, ApplicationBuilder
from glue import call_llm_flash, call_llm, format_documents

import pandas as pd
import torch
import lancedb
import re
from sentence_transformers import SentenceTransformer
from report_prompts import *
from pathlib import Path
import json

## Convert to remote server call
encoder = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', device='mps',trust_remote_code=True)
###

@action(reads=[], writes=['search_expansion_prompt'])
def search_expansion_prompt_format(state: State, topic: str, focus: str, prompts: dict) -> State:
    formatted_prompt = prompts['search_expansion_prompt'].format(topic=topic,
                                                                 focus=focus)
    return state.update(search_expansion_prompt=formatted_prompt)

@action(reads=['search_expansion_prompt'], writes=['search_expansion'])
def search_expansion(state: State) -> State:
    expansion_prompt = state['search_expansion_prompt']
    # search_expansion = call_llm(expansion_prompt, model="gemma-3-12b-it-qat")
    search_expansion = call_llm_flash(expansion_prompt)
    search_expansion = re.findall(r'\d+\. (.+?\?)', search_expansion)
    return state.update(search_expansion=search_expansion)

@action(reads=['search_expansion'], writes=['query_expansion'])
def query_expansion(state: State, topic: str, focus: str, prompts: dict) -> State:
    queries = list()
    for question in state['search_expansion']:
        expansion_prompt = prompts['query_expansion_prompt'].format(topic=topic,
                                                         focus=focus,
                                                         question=question)
        # query_expansion = call_llm(expansion_prompt, model="gemma-3-12b-it-qat")
        query_expansion = call_llm_flash(expansion_prompt)
        queries.append({'question': question, 'query': query_expansion})
    return state.update(query_expansion=queries)

@action(reads=['query_expansion'], writes=["query_expansion"])
def embed_text(state: State) -> State:
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
def retrieve_documents(state: State, number_of_results: int, index_locations: dict) -> State:
    index = lancedb.connect(index_locations['index_path'])
    table = index.open_table(index_locations['index_table'])
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
def build_extraction_prompt(state: State, topic: str, focus: str, prompts: dict) -> State:
    extraction_prompts = list()
    for _expansion, _documents in zip(state['query_expansion'], state['documents']):
        formatted_documents = format_documents(_documents)
        # print(_expansion)
        prompt = prompts['relevant_documents_prompt'].format(question=_expansion['question'],
                                          topic=topic,
                                          focus=focus,
                                          documents=formatted_documents)
        extraction_prompts.append(prompt)
    return state.update(extraction_prompt=extraction_prompts)


@action(reads=["extraction_prompt"], writes=["extraction"])
def generate_extraction(state: State) -> State:
    extractions = list()
    for _expansion_prompt in state['extraction_prompt']:
        # extraction = call_llm(_expansion_prompt)
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
def format_report_prompt(state: State, topic: str, focus: str, prompts: dict) -> State:
    grounding = state['report_grounding']
    formatted_grounding = format_documents(grounding)
    formatted_prompt = prompts['report_prompt'].format(topic=topic,focus=focus, sources=formatted_grounding)
    return state.update(formatted_report_grounding=formatted_grounding, report_prompt=formatted_prompt)

@action(reads=["report_prompt"], writes=["report"])
def generate_report(state: State) -> State:
    # report = call_llm(state['report_prompt'], model="gemma-3-4b-it-qat")
    report = call_llm_flash(state['report_prompt'])
    report = report.replace('$','\\$')
    extracted_report = re.search(r'<report>(.*?)</report>', report, flags=re.DOTALL)
    if extracted_report:
        report = extracted_report.group(1)
    return state.update(report=report)

def build_flow():
    report_generation_app = (
        ApplicationBuilder()
        .with_actions(
            search_expansion_prompt_format,
            search_expansion,
            query_expansion,
            embed_text,
            retrieve_documents,
            build_extraction_prompt,
            generate_extraction,
            merge_grounding,
            format_report_prompt,
            generate_report
        )
        .with_transitions(
            ("search_expansion_prompt_format", "search_expansion"),
            ("search_expansion", "query_expansion"),
            ("query_expansion", "embed_text"),
            ("embed_text", "retrieve_documents"),
            ("retrieve_documents", "build_extraction_prompt"),
            ("build_extraction_prompt", "generate_extraction"),
            ("generate_extraction", "merge_grounding"),
            ("merge_grounding", "format_report_prompt"),
            ("format_report_prompt", "generate_report"))
        .with_entrypoint("search_expansion_prompt_format")
        .with_tracker(
            "local",
            project=f"research_batch-single_run",
        )
        .build()
    )
    return report_generation_app

class ReportFlow():
    def __init__(self, topic: str, focus: str, number_of_results: int, index_locations: dict):
        self.pipeline_prompts = {
            "relevant_documents_prompt": extraction_prompt,
            "query_expansion_prompt": query_expansion_prompt,
            "search_expansion_prompt": search_expansion_prompt,
            "report_prompt": report_prompt
        }
        self.topic = topic
        self.focus = focus
        self.number_of_results = number_of_results
        self.index_locations = index_locations

    def build_flow(self):
        self.app = build_flow()

    def run_workflow(self):
        report_action, report_result, report_state = self.app.run(
            halt_after=["generate_report"],
            inputs={
                "topic": self.topic,
                "focus": self.focus,
                "number_of_results": self.number_of_results,
                "prompts": self.pipeline_prompts,
                "index_locations": self.index_locations
            }
        )
        self.result_state = report_state
        self.result_data = report_state.get_all()
        return report_state

    def extract_report_information(self):
        self.report = {
            'document':self.result_data['report'],
            'topic':self.topic,
            'focus':self.focus
        }
        return self.report

    def save_artifacts(self, project_folder: str, report_name: str):
        save_path = Path(project_folder)
        save_path = save_path.joinpath('topic_report')
        save_path.mkdir(parents=True, exist_ok=True)
        document_path = save_path.joinpath('documents')
        supporting_data = save_path.joinpath('supporting_data')
        document_path.mkdir(parents=True, exist_ok=True)
        supporting_data.mkdir(parents=True, exist_ok=True)

        with open(document_path.joinpath(report_name + '.json'), 'w') as f:
            json.dump(self.report, f)

        with open(supporting_data.joinpath(report_name + '.json'), 'w') as f:
            json.dump(self.result_data, f)


