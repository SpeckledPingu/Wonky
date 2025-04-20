from components import *
from burr.core import ApplicationBuilder
import json
from pathlib import Path

class ReportParser():
    def __init__(self, save_folder):
        self.save_folder = save_folder

    def build(self, report_file: Path) -> dict:
        parsing_app = (
            ApplicationBuilder()
            .with_actions(
                load_report_from_file,
                llm_segment_and_summarize,
                parse_report_to_segments,
                encode_text
            )
            .with_transitions(
                ("load_report_from_file", "llm_segment_and_summarize"),
                ("llm_segment_and_summarize", "parse_report_to_segments"),
                ("parse_report_to_segments", "encode_text"))
            .with_entrypoint("load_report_from_file")
            .with_tracker(
                "local",
                project=f"research_batch-parsing-{report_file.stem[:25]}",
            )
            .build()
        )
        return parsing_app

    def run(self, report_file: Path, app):
        parsing_action, parsing_result, parsing_state = app.run(
            halt_after=["encode_text"],
            inputs={
                "file_path": report_file
            }
        )

        with open(self.save_folder.joinpath(f'{report_file.name}'), 'w') as f:
            json.dump(parsing_state['parsed_document'], f)

        return parsing_state

class TopicReportGenerator():
    def __init__(self):
        pass

    def build(self):
        app = (
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
        return app

    def run(self, topic:str, focus:str, app):
        extraction_action, extraction_result, extraction_state = app.run(
            halt_after=["generate_report"],
            inputs={
                "topic": topic,
                "focus": focus,
                "number_of_results": 10
            }
        )
        report_data = extraction_state.get_all()
        report_data['topic'] = topic
        report_data['focus'] = focus
        return report_data