import pandas as pd
from pathlib import Path
import lancedb
import re
from sentence_transformers import SentenceTransformer
from typing import List
import wikipediaapi
import wikipedia
from .format import ParseWikipediaSections, generate_numeric_hash
import time
from datetime import datetime

def retrieve_wikipedia_page(query):
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='Wonky', language='en')
    wikipedia_page = wiki_wiki.page(query)
    wikipedia_parser = ParseWikipediaSections()
    parsed_sections = wikipedia_parser.parse_wikipedia_sections(wikipedia_page.sections)
    doc_id = generate_numeric_hash(wikipedia_page.title)
    citation = "WIKI" + doc_id
    # try:
    wikipedia_data = {'title': wikipedia_page.title,
                      'filename': wikipedia_page.fullurl,
                      "number": doc_id,
                      'source_file': wikipedia_page.fullurl,
                      'typeId': 'WIKIPEDIA',
                      'sections': parsed_sections,
                      'full_text': wikipedia_page.text,
                      'summary': wikipedia_page.summary,
                      'citation': citation,
                      'id': citation,
                      'type': 'Wikipedia',
                      'doc_id': doc_id,
                      'source_document': wikipedia_page.fullurl,
                      'source_dataset': 'Wikipedia',
                      'topics': '',
                      'active': True,
                      'date': datetime.now().strftime("%Y-%m-%d")
                      }
    # except Exception as e:
    #     return
    return wikipedia_data


def search_wikipedia(query, num_results=10):
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='Wonky', language='en')
    search_results = wikipedia.search(query, results=num_results, suggestion=False)
    print(search_results)
    wikipedia_page_results = list()
    for search_result in search_results:
        wikipedia_page = wiki_wiki.page(search_result)
        wikipedia_parser = ParseWikipediaSections()
        parsed_sections = wikipedia_parser.parse_wikipedia_sections(wikipedia_page.sections)
        doc_id = generate_numeric_hash(wikipedia_page.title)
        citation = "WIKI" + doc_id
        try:
            wikipedia_data = {'title': wikipedia_page.title,
                              'filename': wikipedia_page.fullurl,
                              "number": doc_id,
                              'source_file': wikipedia_page.fullurl,
                              'typeId': 'WIKIPEDIA',
                              'sections': parsed_sections,
                              'full_text': wikipedia_page.text,
                              'summary': wikipedia_page.summary,
                              'citation': wikipedia_page.citation,
                              'id': citation,
                              'type': 'Wikipedia',
                              'doc_id': doc_id,
                              'source_document': wikipedia_page.fullurl,
                              'source_dataset': 'Wikipedia',
                              'topics': '',
                              'active': True,
                              'date': datetime.now().strftime("%Y-%m-%d")
                              }
        except Exception as e:
            continue
        wikipedia_page_results.append(wikipedia_data)
        time.sleep(1)
    return wikipedia_page_results


class SearchWikipedia_SubjectFocus():
    def __init__(self, user_agent: str = "Wonky"):
        self.wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language='en')

    def _search(self, subject_matter: str, focus: str, num_results: int = 10):
        """
        :param subject_matter:
        :param focus:
        :param num_results:
        :return:
        """
        subject_matter_search_results = wikipedia.search(subject_matter, results=num_results, suggestion=False)
        focus_search_results = wikipedia.search(focus, results=num_results, suggestion=False)
        subject_matter_search_results.extend(focus_search_results)
        article_ids = list(set(subject_matter_search_results))
        return article_ids

    def retrieve_wikipedia_page(self, page_id):
        """
        :param page_id:
        :return:
        """
        wikipedia_page = self.wiki_wiki.page(page_id)
        wikipedia_parser = ParseWikipediaSections()
        parsed_sections = wikipedia_parser.parse_wikipedia_sections(wikipedia_page.sections)
        doc_id = generate_numeric_hash(wikipedia_page.title)
        citation = "WIKI" + doc_id
        # try:

        ## Below schema maintains compatibility with on-disk data that is already indexed
        ## Can be used to format.py to separate functionality and compatibility
        wikipedia_data = {'title': wikipedia_page.title,
                          'filename': wikipedia_page.fullurl,
                          "number": doc_id,
                          'source_file': wikipedia_page.fullurl,
                          'typeId': 'WIKIPEDIA',
                          'sections': parsed_sections,
                          'full_text': wikipedia_page.text,
                          'summary': wikipedia_page.summary,
                          'citation': citation,
                          'id': citation,
                          'type': 'Wikipedia',
                          'doc_id': doc_id,
                          'source_document': wikipedia_page.fullurl,
                          'source_dataset': 'Wikipedia',
                          'topics': '',
                          'active': True,
                          'date': datetime.now().strftime("%Y-%m-%d")
                          }
        # except Exception as e:
        #     return
        return wikipedia_data

    def search(self, subject_matter: str, focus: str, num_results: int = 10):
        """
        :param subject_matter:
        :param focus:
        :param num_results:
        :return:
        """
        article_ids = self._search(subject_matter, focus, num_results)
        wikipedia_pages = list()
        for article_id in article_ids:
            wikipedia_page = self.retrieve_wikipedia_page(article_id)
            wikipedia_pages.append(wikipedia_page)
        return wikipedia_pages


