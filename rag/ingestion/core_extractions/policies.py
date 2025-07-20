
from typing import List

from rag.ingestion.datamodels import Policy, SearchDocument, ResearchPath
from rag.retrieval.db_sqlite import insert_policy
from rag.llms.google import call_llm_flash
from rag.llms.helper_funcs import convert_response_to_json, create_citation
from rag.retrieval.db_sqlite import get_research_path_by_id, get_search_results_by_id
import sqlite3


def format_policy_text(policy):
    locations_in_source = ', '.join(policy['locations_in_source'])
    stakeholders = policy['key_stakeholders']
    stakeholders = f"""*Key Stakeholders:*\n  * *Beneficiaries*: {stakeholders['beneficiaries']}\n  * *Regulated Parties*: {stakeholders['regulated_parties']}\n  * *Implementing Agency*: {stakeholders['implementingAgency']}"""

    arguments_in_favor = ''
    for argument in policy['arguments_in_favor']:
        arguments_in_favor += f"  * {argument['argument']}\n"
    if len(arguments_in_favor) > 0:
        arguments_in_favor = f"*Arguments In Favor:*\n{arguments_in_favor}".strip()
    else:
        arguments_in_favor = "*Arguments In Favor:*\n  * No Arguments In Favor"

    arguments_against = ''
    for argument in policy['arguments_against']:
        arguments_against += f"  * {argument['argument']}\n"
    if len(arguments_against) > 0:
        arguments_against = f"*Arguments Against:*\n{arguments_against}".strip()
    else:
        arguments_against = f"*Arguments Against:*\n* No Arguments Against"

    arguments = f"{arguments_in_favor}\n{arguments_against}".strip()

    policy_text = f"""*Policy Name:* {policy['policy_name']}
*Policy Citation:* {policy['citation']}
*Policy Type:* {policy['policy_type']}
*Primary Objective:* {policy['primary_objective']}
*Mechanism of Action:* {policy['mechanism_of_action']}
*Policy Details:* {policy['policy_details']}
*Specific Evidence:* {policy['specific_evidence']}
{stakeholders}
{arguments}
*Locations in Source:* {locations_in_source}
"""
    return policy_text


def extract_policies(search_document: SearchDocument,
                     extraction_prompt: str,
                     # conn: sqlite3.Connection,
                     temperature: float = 0.2,
                     max_tokens: int = 10000,
                     citation_prefix='PLCY_',
                     citation_hash_length=6) -> List[Policy]:
    
    extraction_prompt_formatted = extraction_prompt.format(document_text=search_document.grounding)
    policies_text = call_llm_flash(extraction_prompt_formatted,
                                   temperature=temperature,
                                   max_tokens=max_tokens
                                   )
    policies = convert_response_to_json(policies_text)
    all_policies = list()
    for policy in policies['policies']:
        print(policy['policy_name'])
        policy['run_id'] = search_document.run_id
        policy['result_id'] = search_document.result_id
        policy['source_document_id'] = search_document.id
        policy['citation'] = create_citation(policy,
                                             ['policy_name','policy_type','primary_objective','mechanism_of_action','policy_details'],
                                             prefix=citation_prefix,
                                             number_of_digits=citation_hash_length
                                             )
        policy['policy_text'] = format_policy_text(policy)
        policy = Policy(**policy)
        all_policies.append(policy)
        # insert_policy(policy, conn)
    return all_policies


def extract_from_search_document(search_document: SearchDocument,
                                 extract_prompt: str,
                                 conn: sqlite3.Connection,
                                 citation_prefix='PLCY_',
                                 citation_hash_length=6,
                                 temperature: float = 0.2,
                                 max_tokens: int = 10000
                                 ) -> List[Policy]:
    """
    :param search_document:
    :param prompt: In the current json it's: "policy_extraction"
    :return:
    """
    policies = extract_policies(search_document=search_document,
                                extraction_prompt=extract_prompt,
                                # conn=conn,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                citation_prefix=citation_prefix,
                                citation_hash_length=citation_hash_length
                                )
    return policies


def extract_all_search_results(research_id: str,
                               extract_prompt: str,
                               conn: sqlite3.Connection,
                               temperature: float = 0.2,
                               max_tokens: int = 10000,
                               citation_prefix='PLCY_',
                               citation_hash_length=6,
                               ) -> List[Policy]:
    
    research_path = ResearchPath(**get_research_path_by_id(research_id, conn))
    search_documents = get_search_results_by_id(research_path.run_id, conn)
    search_documents = [SearchDocument(**document) for document in search_documents]
    all_policies = list()
    for search_document in search_documents:
        policies = extract_from_search_document(search_document,
                                                extract_prompt=extract_prompt,
                                                conn=conn,
                                                temperature=temperature,
                                                max_tokens=max_tokens,
                                                citation_prefix=citation_prefix,
                                                citation_hash_length=citation_hash_length)
        all_policies.extend(policies)
    return all_policies