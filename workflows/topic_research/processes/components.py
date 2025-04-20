from burr.core import action, State, ApplicationBuilder, ApplicationContext, Action
from pathlib import Path
import re
import json
from rag.llms.google import call_llm_flash
from rag.llms.local import Encoder
from ..processes.glue import parse_report
import torch
from ..prompts.base_prompts import *


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
def encode_text(state: State) -> State:
    parsed_document = state['parsed_document']
    for section in parsed_document['sections']:
        section['section_vector'] = encoder.encode(section['section_text']).tolist()
        torch.mps.empty_cache()

    parsed_document['report_vector'] = encoder.encode(parsed_document['report']).tolist()
    torch.mps.empty_cache()
    parsed_document['summary_vector'] = encoder.encode(parsed_document['summary']).tolist()
    torch.mps.empty_cache()
    return state.update(parsed_document=parsed_document)