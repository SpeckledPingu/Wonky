import re
import hashlib
from copy import deepcopy
from typing import List

# def format_documents(documents):
#     formatted_texts = []
#     report_ids = list(set([record['id'] for record in documents]))
#     for id in report_ids:
#         report_sections = [section for section in documents if section['id'] == id]
#         report_sections = sorted(report_sections, key=lambda section: section['section_start'])
#         report_text = [text['text'] for text in report_sections]
#         report_text = [re.sub('\n+', '\n', _text) for _text in report_text]
#         report_text = [re.sub(' +', ' ', _text) for _text in report_text]
#         report_text = [re.sub(r'(\[.*?\])','', _text) for _text in report_text]
#         report_text = [_text.replace('\\','') for _text in report_text]
#         report_text = [re.sub(r'(\[.*?\])','', _text) for _text in report_text]
#         report_text = [re.sub(r'(\n?-{10,})','', _text) for _text in report_text]
#         report_text = [re.sub(r'(\n.*?#_Toc.*?\n)','', _text) for _text in report_text]
#         report_text = [re.sub(r'(- \n)','', _text) for _text in report_text]
#         report_text = [re.sub(r'\n{2,}','\n', _text) for _text in report_text]
#         report_text = [_text.strip() for _text in report_text]
#         report_text = '\n-----\n'.join(report_text)
#         report_header = f"""**{report_sections[0]['id']}:** {report_sections[0]['title']}"""
#         formatted_texts.append(f"""{report_header}\n{report_text}""".strip())
#     # print(formatted_texts[0])
#     return '\n=======\n'.join(formatted_texts)

def format_wiki_sections_w_citations(wiki_document: List[dict], base_citation: str) -> List[str]:
    """
    :param wiki_document: List of formatted wikipedia sections
    :param base_citation: Alphanumeric citation pattern, often in the format of AAAA#####
    :return: List of the formatted sections that contain the citations
    """
    first_section = wiki_document[0]
    current_level_1_idx = 1
    current_level_2_idx = 1
    current_level_1_name = first_section['hierarchy']['level_0']
    current_level_2_name = first_section['hierarchy']['level_1']
    formatted_sections = list()
    base_citation = '_'.join(re.findall(r'(\w+)', base_citation))

    first_section['citation'] = f"{base_citation}__{current_level_1_idx}___{current_level_2_idx}"
    formatted_sections.append(first_section)
    if len(wiki_document) > 1:
        for section in wiki_document[1:]:
            if current_level_1_name != section['hierarchy']['level_0']:
                current_level_1_name = section['hierarchy']['level_0']
                current_level_2_name = section['hierarchy']['level_1']
                current_level_1_idx += 1
                current_level_2_idx = 1
            elif (current_level_1_name == section['hierarchy']['level_0']) and (current_level_2_name != section['hierarchy']['level_1']):
                current_level_2_name = section['hierarchy']['level_1']
                current_level_2_idx += 1
            else:
                current_level_2_idx += 1

            section['citation'] = f"{base_citation}__{current_level_1_idx}___{current_level_2_idx}"
            formatted_sections.append(section)

    return formatted_sections

def format_wikipedia_page(wiki_document: list) -> str:
    """
    To improve the grounding quality, the wikipedia page is formatted as a bullet point list of each section/subsection
    This helps the llm clearly delineate what section corresponds to what citation for proper citation handling
    Indentation helps the llm with relational structures between subsections and sections
    :param wiki_document:
    :return: string that contains list styled wikipedia page with nesting
    """
    formatted_wikipedia_page = ''
    for section in wiki_document:
        indent = section['level'] * '  '
        section_text = section['text'].split('\n')
        section_text = [indent + ' - ' + text for text in section_text if text.strip() != '']
        section_text = '\n'.join(section_text)
        formatted_wikipedia_page += indent + '- ' + f"**{section['title']}** `[{section['citation']}]`:\n{section_text}\n"
    return formatted_wikipedia_page


def generate_numeric_hash(text, number_of_characters=5):
    numeric_hash = int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16) % 10**number_of_characters
    return str(numeric_hash)

class ParseWikipediaSections():
    def __init__(self):
        """
        The initialized sections and hierarchy are per-page, not a static class object that is reused over and over
        current_hierarchy is used to track the titles of the nested sections so that helpful metadata is preserved about
        the overall topical relationships within the page.
        """
        self.parsed_sections = list()
        self.current_hierarchy = {'level_0': '', 'level_1': '', 'level_2': '', 'level_3': '', 'level_4': ''}

    def _recursive_extract(self, sections, level=0):
        """
        :param sections: This is the specific section to parse. Wikipedia pages are returned in nesting patterns.
        :param level: This is the section level for metadata handling in the hierarchy to indicate where a section is related to the overall page sections, it should not be manually set
        :return:
        """
        for s in sections:
            hierarchy_string = list()
            for i in range(0, 5):
                # Current hierarchy tracks the titles of the wikipedia page in their nesting
                # The level is provided in the data
                # The level title is not persisted through the entire page data
                # current_hierarchy tracks this metadata so that sections maintain information about their position and topicality to the wiki article
                if i == level:
                    self.current_hierarchy[f"level_{i}"] = s.title
                elif i > level:
                    self.current_hierarchy[f"level_{i}"] = ''

            for i in range(0, 5):
                _hierarchy_header = self.current_hierarchy[f"level_{i}"]
                if _hierarchy_header != "":
                    hierarchy_string.append(_hierarchy_header)
            hierarchy_string = '|'.join(hierarchy_string)

            self.parsed_sections.append({"level": level,
                                         "title": s.title,
                                         "text": s.text,
                                         "hierarchy": deepcopy(self.current_hierarchy),
                                         "hierarchy_string": hierarchy_string})

            self._recursive_extract(s.sections, level + 1)

    def parse_wikipedia_sections(self, sections):
        self._recursive_extract(sections, level=0)
        return self.parsed_sections