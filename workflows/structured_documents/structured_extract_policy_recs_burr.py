#%%
from sentence_transformers import SentenceTransformer
import torch
import lancedb
from openai import OpenAI
import re
import pandas as pd
import numpy as np
import json
import time
import re
import hashlib

from google import genai
from google.genai import types
from dotenv import load_dotenv
from tqdm.notebook import tqdm
import os
load_dotenv('env_var')
#%%
from pathlib import Path
import sqlite3
from datetime import datetime
from uuid import uuid4
from copy import deepcopy
import wikipediaapi
import wikipedia

project_folder = Path('project_research')
project_folder.mkdir(parents=True, exist_ok=True)
research_json_folder = project_folder.joinpath('json_data')
research_json_folder.mkdir(parents=True, exist_ok=True)
# database_location = project_folder.joinpath('research.sqlite')
# conn = sqlite3.connect('working_folder/project_research/research.sqlite')
# cursor = conn.cursor()

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
def call_llm(query, temperature=0.35, seed=42, model="gemma-3-12b-it-qat"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": query}
        ],
        temperature=temperature,
        seed=seed,
    )
    return completion.choices[0].message.content

model = "gemini-2.0-flash"
total_tokens = list()

def call_llm_flash(query, temperature=0.1, seed=42, max_tokens=7500 ):
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    retries = 3
    time_delay = 15
    for i in range(retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[query],
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    seed=seed
                )
            )
            break
        except Exception as e:
            print(e)
            print(f"Retries left: {retries - i}")
            time.sleep(time_delay)
            continue



    total_tokens.append({'prompt_tokens':response.usage_metadata.prompt_token_count,
                         'completion_tokens':response.usage_metadata.candidates_token_count,
                         'total_tokens':response.usage_metadata.total_token_count,
                         'timestamp':datetime.now().strftime("%Y_%m_%d_%H_%M_%S")})

    return response.text


## Need to create a generic and a specific version of the prompt for handling stream based or project based summaries
# policy_recommendations_prompt = """
# You are an expert policy analyst and strategist. Your task is to identify, categorize, and detail all policy recommendations, options, and alternatives proposed in the provided research document(s), including strategic advice for an organization wishing to act on them.
#
# **Research Context:**
# * **Subject:** {subject}
# * **Focus:** {focus}
#
# Your analysis must provide a clear, structured overview of the potential solutions discussed in the text. Pay special attention to recommendations that are most relevant to the research focus.

policy_recommendations_prompt = """
You are an expert policy analyst and strategist. Your task is to identify, categorize, and detail all policy recommendations, options, and alternatives proposed in the provided research document(s), including strategic advice for an organization wishing to act on them.

Your analysis must provide a clear, structured overview of the potential solutions discussed in the text. Pay special attention to recommendations that are most relevant to the main information in the text.

### **Analysis Rules**

**Rule 1: Systematically Identify All Recommendations.**
* Thoroughly scan the document(s) to find any proposed course of action, policy alternative, or direct recommendation.
* Focus your search on these key fields: `Policy Options or Alternatives Discussed by Report` (Section 5) and `Issues for Governing/Legislative Body(ies) Highlighted by Report` (Section 6).

**Rule 2: Categorize Each Recommendation.**
* For each recommendation you identify, assign it to one of the following categories based on its nature:
    * **Legislative Action:** A proposal that requires action by a legislative body (e.g., passing a new law, amending an existing one).
    * **Regulatory Change:** A proposal for a government agency to create, modify, or rescind a rule.
    * **Funding Initiative:** A proposal to allocate, increase, or redirect financial resources.
    * **Strategic De-escalation:** A proposal to reduce or eliminate a program, service, or piece of infrastructure (e.g., closing underused roads).
    * **Further Study/Analysis:** A proposal for more research or data collection before action is taken.

**Rule 3: Profile Each Recommendation in Detail.**
* For each recommendation, extract the following details from the text:
    * **The Core Recommendation:** State the proposed action clearly and concisely.
    * **Responsible Actor(s):** Which entity (e.g., Congress, FCC, State DOTs) is being called upon to act?
    * **Intended Goal:** What specific problem is this recommendation trying to solve?
    * **Supporting Evidence:** Find a specific statistic, finding, or challenge mentioned elsewhere in the document that justifies this recommendation. This is the "why" behind the action.
    * **Rationale:** Based on the goal and evidence, briefly explain why this recommendation is a logical course of action.
    * **Source Reference:** The direct citation from the text `[ID__Section__Paragraph]` where the recommendation itself is found.

**Rule 4: Assess Strategic Considerations.**
* For each recommendation, analyze the stakeholder landscape and the nature of the policy to identify:
    * **Points of Intervention:** Where could an organization most effectively exert influence? (e.g., Public awareness campaigns, direct lobbying of the 'Responsible Actor', forming coalitions with allied stakeholders, submitting public comments during a regulatory process).
    * **Potential Hurdles:** What obstacles might arise? (e.g., Political opposition from specific actors identified in the document, high financial cost, legal challenges, lack of public support).

### **Output Formatting**

* Use a main heading: **Policy Recommendations and Strategic Analysis for {subject}**
* Use the categories from Rule 2 as your secondary headings.
* Under each heading, list the relevant recommendations you identified.
* For each recommendation, provide a detailed profile that includes:
    * The recommendation itself in bold.
    * A short paragraph synthesizing the **Rationale**, the **Intended Goal**, and the **Responsible Actor(s)**.
    * A nested bullet point labeled "**Evidence:**" followed by the specific supporting fact or statistic from the document, including its source reference.
    * A final section labeled "**Strategic Considerations:**" that contains a brief paragraph summarizing the key **Points of Intervention** and **Potential Hurdles** identified in Rule 4.

---
DOCUMENTS:
{documents_text}
---

POLICY RECOMMENDATIONS:
"""

from burr.core import action, State, ApplicationBuilder, ApplicationContext, Action
@action(reads=[], writes=['extracted_documents'])
def sql_select_overview_documents(state: State, document_ids: list, cursor, fields) -> State:
    ## change to the run_id when using it with the project to only select the generated documents in the project/stream
    # fields = ['overview', 'run_id', 'run_timestamp', 'project_id', 'subject_matter', 'focus','source_document']
    documents = cursor.execute("""SELECT {fields} FROM overviews
                                   WHERE source_document IN ({number_of_documents});""".format(number_of_documents=', '.join(['?']*len(document_ids)),
                                                                                               fields=', '.join(fields)),
                               [x for x in document_ids]).fetchall()
    documents_df = pd.DataFrame(documents, columns=fields)
    documents_df = documents_df.sort_values(by=['run_timestamp'], ascending=False).drop_duplicates(subset=['source_document'], keep='first')
    print(documents_df.shape)
    extracted_documents = documents_df['overview'].to_list()
    return state.update(extracted_documents=extracted_documents)

@action(reads=['extracted_documents'], writes=['summary'])
def generate_policy_recommendations_summary(state: State, policy_recommendations_prompt: str, subject_matter:str, focus: str,
                               temperature: float) -> State:
    print(len(state['extracted_documents']))
    actors_to_compare_prompt_formatted = policy_recommendations_prompt.format(documents_text=state['extracted_documents'], subject=subject_matter, focus=focus)
    summary = call_llm_flash(actors_to_compare_prompt_formatted, temperature=temperature)
    return state.update(summary=summary)


def structured_extract_policy_recommendations_report_build():
    summary_app = (
        ApplicationBuilder()
        .with_actions(
            sql_select_overview_documents,
            generate_policy_recommendations_summary,
            # insert_extractions_sql,
            # save_research_to_json
        )
        .with_transitions(
            ("sql_select_overview_documents", "generate_policy_recommendations_summary"),
        )
        .with_entrypoint("sql_select_overview_documents")
        .with_tracker(
            "local",
            project=f"temp_summary",
        )
        .build()
    )
    return summary_app


# run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
# run_id = str(uuid4())
# project_id = str(uuid4())
# project_id = 'rural broadband'
# source_dataset = 'wikipedia'
#
# summary_action, summary_result, summary_state = summary_app.run(
#     halt_after=["generate_policy_recommendations_summary"],
#     inputs={
#         "subject_matter": subject_matter,
#         "focus": focus,
#         "fields":fields,
#         "document_ids": document_ids,
#         "policy_recommendations_prompt":policy_recommendations_prompt,
#         "temperature":0.2,
#         "conn": conn,
#         "cursor": cursor,
#     }
# )
