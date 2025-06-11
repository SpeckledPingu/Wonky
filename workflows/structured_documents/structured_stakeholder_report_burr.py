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


stakeholder_analysis_prompt = """
You are an expert policy analyst. Your task is to produce a detailed stakeholder analysis based on the provided research document(s).

**Research Context:**
* **Subject:** {subject}
* **Focus:** {focus}

Your analysis must go beyond a simple list. For each stakeholder, you will produce a concise analytical brief that explains their role, interests, and demonstrated impact, supported by specific evidence from the text. Follow the rules and formatting instructions below.

### **Analysis Rules**

**Rule 1: Extract and Categorize All Actors.**
* Scan Section 2 (`Key Domestic Actors, Entities, & Affected Groups Identified`) to compile a complete list of stakeholders.
* For each stakeholder, assign one of the following categories: **Government Agency, Legislative Body, Private Sector, Association/Advocacy Group, or Affected Group**.

**Rule 2: Determine Each Actor's Role, Stance, and Influence.**
* For each actor, go to their subsection in Section 4 (`Detailed Analysis of Key Domestic Actors...`).
* **2.1: Define Their Role.** What is their fundamental function in this policy area? (e.g., Is it regulatory, operational, funding-based, advocacy-focused, or are they a subject of the policy?) Look at the `Current Policy/Stance/Program Description or Role` field.
* **2.2: Identify Their Stated Position.** What does the document say they want, believe, or have stated as an objective? Look at the `Stated Objectives, Position, Interests...` field. This reveals their intent.
* **2.3: Identify Their Influence.** What power or action does the document show they can wield? Look at the `Policy Levers, Programs, or Actions...` field to find their levers of influence.

**Rule 3: Select Relevant Evidence.**
* For each actor, find 1-2 pieces of concrete, quantitative, or highly specific evidence that illustrates their role and influence in practice.
* **3.1: Prioritize by Relevance.** The evidence you choose MUST be directly related to the research **Focus**. For example, if the focus is on "funding," evidence of budgetary allocations is critical. If the focus is on "safety," accident rate data is more relevant.
* **3.2: Mine Key Fields.** Pull this evidence from fields like `Funding/Resource Allocation...`, `Reported Outcomes/Impacts/Effectiveness...`, and `Reported Challenges, Criticisms...`. Always include the citation `[ID__Section__Paragraph]` if available.

### **Output Formatting**

* Use a main heading: **Stakeholder Analysis for {subject}**
* Use the categories from Rule 1 as your secondary headings.
* Under each heading, create a brief for each stakeholder. Each brief should contain:
    * The stakeholder's name in bold.
    * A synthesized paragraph that integrates the findings from your analysis. It should start by stating their role (Rule 2.1), describe their position and influence (Rules 2.2 & 2.3), and seamlessly weave in the specific evidence you selected (Rule 3) to support the analysis. The goal is a flowing narrative, not a list of facts.

---
DOCUMENTS:
{documents_text}
---

STAKEHOLDER ANALYSIS:
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
def generate_stakeholder_summary(state: State, summary_prompt_template: str, subject_matter:str, focus: str,
                               temperature: float) -> State:
    print(len(state['extracted_documents']))
    summary_prompt_formatted = summary_prompt_template.format(documents_text=state['extracted_documents'], subject=subject_matter, focus=focus)
    summary = call_llm_flash(summary_prompt_formatted, temperature=temperature)
    return state.update(summary=summary)


def structured_stakeholder_report_build():
    summary_app = (
        ApplicationBuilder()
        .with_actions(
            sql_select_overview_documents,
            generate_stakeholder_summary,
            # insert_extractions_sql,
            # save_research_to_json
        )
        .with_transitions(
            ("sql_select_overview_documents", "generate_stakeholder_summary"),
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
#     halt_after=["generate_funding_opportunities_summary"],
#     inputs={
#         "subject_matter": subject_matter,
#         "focus": focus,
#         "fields":fields,
#         "document_ids": document_ids,
#         "funding_opportunities_prompt":funding_opportunities_prompt,
#         "temperature":0.2,
#         "conn": conn,
#         "cursor": cursor,
#     }
# )
