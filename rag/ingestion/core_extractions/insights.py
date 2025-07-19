from typing import List

from rag.ingestion.datamodels import Insight, SearchDocument, ResearchPath
from rag.retrieval.db_sqlite import insert_insight
from rag.llms.google import call_llm_flash
from rag.llms.helper_funcs import convert_response_to_json, create_citation, create_batches
from rag.retrieval.db_sqlite import get_research_path_by_id, get_search_results_by_id
from dataclasses import asdict
import sqlite3
import json


def llm_identify_insights(search_document: SearchDocument, identification_prompt: str) -> str:
    identification_prompt_formatted = identification_prompt.format(document=search_document.grounding)
    identified_insights = call_llm_flash(identification_prompt_formatted,
                                         temperature=0.2,
                                         max_tokens=1000
                                         )
    return identified_insights

def process_identified_insights(identified_insights: str,
                                search_document: SearchDocument,
                                citation_prefix: str = "INST_",
                                citation_hash_length: int = 6) -> List[Insight]:
    try:
        identified_insights_json = convert_response_to_json(identified_insights)
        insights = list()
        for _insight in identified_insights_json:
            _insight['run_id'] = search_document.run_id
            _insight['result_id'] = search_document.result_id
            _insight['citation'] = create_citation(_insight,
                                                  fields=['insight_type','insight_name','insight_synopsis'],
                                                  prefix=citation_prefix,
                                                  number_of_digits=citation_hash_length
                                                   )
            insights.append(Insight(**_insight))
    except Exception as e:
        print(search_document.run_id, search_document.chunk_id, search_document.result_id)
        print(identified_insights)
        return []
    return insights

def identify_insights(search_document: SearchDocument,
                      prompt: str,
                      citation_prefix: str ='INST_',
                      citation_hash_length: int=6) -> List[Insight]:
    
    insight_raw = llm_identify_insights(search_document=search_document,
                                        identification_prompt=prompt
                                        )

    insights = process_identified_insights(identified_insights=insight_raw,
                                           search_document=search_document,
                                           citation_prefix=citation_prefix,
                                           citation_hash_length=citation_hash_length
                                           )
    return insights

def format_insight(insight):
    return f"""*Insight Citation:* {insight.citation}
*Insight Type:* {insight.insight_type}
*Insight Name:* {insight.insight_name}
*Insight Synopsis:* {insight.insight_synopsis}
*Found in:* {', '.join(insight.related_citations)}"""

def format_insight_text(insight):
    _insight_data = insight.insight_data
    insight_statements = '\n\n'.join([_insight['statement'] for _insight in _insight_data])
    related_citations = ', '.join(insight.related_citations)
    insight_explanations = '\n\n'.join([_insight['explanation'] for _insight in _insight_data])
    insight_text = f"""**Insight Name:** {insight.insight_name}
**Insight Citation:** {insight.citation}
**Insight Type:** {insight.insight_type}
**Insight Synopsis:** {insight.insight_synopsis}
**Insight Description:** {insight_statements}
**Insight Explanation:** {insight_explanations}
**Insight Source Citations:** {related_citations}"""
    return insight_text

def extract_insights(insights: List[Insight],
                     search_document: SearchDocument,
                     prompt: str,
                     conn: sqlite3.Connection,
                     batch_size: int = 5,
                     temperature: float = 0.2,
                     max_tokens: int = 10000) -> List[Insight]:
    
    insight_extraction_batches = create_batches([format_insight(_insight) for _insight in insights],
                                            batch_size=batch_size)
    for batch in insight_extraction_batches:
        insight_text = '\n\n-----\n\n'.join(batch)
        batch_insight_prompt = prompt.format(insights=insight_text,
                                             document=search_document.grounding
                                             )

        insight_extraction = call_llm_flash(batch_insight_prompt,
                                            temperature=temperature,
                                            max_tokens=max_tokens
                                            )
        insight_extraction = convert_response_to_json(insight_extraction)
        insight_extraction = {_insight_extraction['insight_citation']: _insight_extraction \
                              for _insight_extraction in insight_extraction}
        
        for insight in insights:
            if insight.citation in insight_extraction:
                print(insight.insight_name)
                insight.insight_data.append(insight_extraction[insight.citation])
                insight.insight_text = format_insight_text(insight)
                insert_insight(insight, conn)
    return insights

def extract_from_search_document(search_document: SearchDocument,
                                 identify_prompt: str,
                                 extract_prompt: str,
                                 conn: sqlite3.Connection,
                                 citation_prefix='INST_',
                                 citation_hash_length=6,
                                 batch_size: int = 5,
                                 temperature: float = 0.2,
                                 max_tokens: int = 10000
                                 ) -> List[Insight]:
    """
    :param search_document:
    :param prompt: In the current json it's: "insight_identification"
    :return:
    """
    insights = identify_insights(search_document,
                                 identify_prompt,
                                 citation_prefix=citation_prefix,
                                 citation_hash_length=citation_hash_length
                                 )
    insights = extract_insights(insights,
                                search_document=search_document,
                                prompt=extract_prompt,
                                conn=conn,
                                batch_size=batch_size,
                                temperature=temperature,
                                max_tokens=max_tokens)
    return insights
    
def extract_all_search_results(research_id: str,
                               identify_prompt:str,
                               extract_prompt: str,
                               conn: sqlite3.Connection,
                               batch_size: int = 5,
                               temperature: float = 0.2,
                               max_tokens: int = 10000,
                               citation_prefix='INST_',
                               citation_hash_length=6,
                               ) -> List[Insight]:
    
    research_path = ResearchPath(**get_research_path_by_id(research_id, conn))
    search_documents = get_search_results_by_id(research_path.run_id, conn)
    search_documents = [SearchDocument(**document) for document in search_documents]
    all_insights = list()
    for search_document in search_documents:
        insights = extract_from_search_document(search_document,
                                                identify_prompt=identify_prompt,
                                                extract_prompt=extract_prompt,
                                                conn=conn,
                                                batch_size=batch_size,
                                                temperature=temperature,
                                                max_tokens=max_tokens,
                                                citation_prefix=citation_prefix,
                                                citation_hash_length=citation_hash_length)
        all_insights.extend(insights)
    return all_insights

    