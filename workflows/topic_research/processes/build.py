from components import load_report_from_file, llm_segment_and_summarize, parse_report_to_segments, encode_text
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

    def run(self, app, report_file: Path):
        parsing_action, parsing_result, parsing_state = app.run(
            halt_after=["encode_text"],
            inputs={
                "file_path": report_file
            }
        )

        with open(self.save_folder.joinpath(f'{report_file.name}'), 'w') as f:
            json.dump(parsing_state['parsed_document'], f)

        return parsing_state