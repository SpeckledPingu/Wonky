import lancedb
from pathlib import Path
import json
from copy import deepcopy


class IndexArtifactsReports():
    def __init__(self, base_folder: Path, source_folder: Path, index_folder: Path, index_name: str):
        self.base_folder = base_folder
        self.source_folder = source_folder
        self.index_folder = index_folder
        self.index_name = index_name
        self.db = lancedb.connect(index_folder)

    def load_full_reports(self):
        processed_report_files = list(self.save_folder.rglob('*.json'))
        parsed_reports = list()
        for file in processed_report_files:
            with open(file) as json_file:
                parsed_report = json.load(json_file)
                parsed_report['vector'] = parsed_report['report_vector']
                parsed_reports.append(parsed_report)

        return parsed_reports

    def build_table(self, parsed_reports):
        tbl = self.db.create_table("reports", data=parsed_reports, mode='overwrite')
        tbl.create_fts_index(["report", 'summary', 'topic', 'source_file_name'], use_tantivy=True, replace=True)
        return tbl

    def load_report_sections(self, processed_report_files):
        parsed_section_reports = list()
        for file in processed_report_files:
            with open(file) as json_file:
                parsed_report = json.load(json_file)
                del parsed_report['report_vector']
                del parsed_report['summary_vector']
                sections = deepcopy(parsed_report['sections'])
                del parsed_report['sections']
                for section in sections:
                    section_report = deepcopy(parsed_report)
                    section_report['section_id'] = section['section_id']
                    section_report['section_idx'] = section['section_idx']
                    section_report['section_text'] = section['section_text']
                    section_report['section_title'] = section['section_title']
                    section_report['vector'] = section['section_vector']
                    parsed_section_reports.append(section_report)

        return parsed_section_reports

    def index_report_sections(self, parsed_section_reports):
        tbl = self.db.create_table("reports_section", data=parsed_section_reports, mode='overwrite')
        tbl.create_fts_index(["section_text", 'section_title', 'source_file_name'], use_tantivy=True, replace=True)
        return tbl



