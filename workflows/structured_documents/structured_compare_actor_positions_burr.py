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

actor_comparison_prompt = """
You are an expert policy analyst. Your task is to produce a comparative analysis of the positions of the following actors, based on the provided research document(s).

**Assignment Context:**
* **Subject:** {subject}
* **Focus of Comparison:** {focus}
* **Actors to Compare:** {actors_to_compare}

Your analysis must move beyond summarizing each actor individually. Instead, you will identify specific points of agreement and disagreement between them related to the research focus, supporting every claim with direct evidence from the text.

### **Analysis Rules**

**Rule 1: Isolate the Core Issue for Comparison.**
* The **Focus of Comparison** defines the specific issue you will analyze. All your analysis must relate directly back to this central theme (e.g., if the focus is "funding," only compare their stances on funding).

**Rule 2: Extract Actor-Specific Positions and Actions.**
* For each actor listed in **Actors to Compare**, go to their respective subsection in Section 4 of the document(s).
* Extract their specific positions, objectives, and actions related to the **Focus of Comparison**. Key fields to investigate are:
    * `Stated Objectives, Position, Interests...` (to understand their goals).
    * `Policy Levers, Programs, or Actions Implemented/Advocated...` (to see their actions).
    * `Reported Challenges, Criticisms...` (to understand their perceived problems).

**Rule 3: Identify Points of Alignment.**
* Compare the extracted information for all actors.
* An "alignment" occurs when two or more actors have similar stated goals, advocate for similar policies, or face similar challenges related to the **Focus of Comparison**.
* For each point of alignment, you must note the specific issue they agree on and then provide the evidence for each actor's position.

**Rule 4: Identify Points of Divergence.**
* Compare the extracted information for all actors.
* A "divergence" occurs when actors have conflicting goals, advocate for opposing policies, or their actions create friction with one another regarding the **Focus of Comparison**.
* For each point of divergence, you must note the specific issue they disagree on and then provide the evidence for each actor's conflicting position.

### **Output Formatting**

* Use a main heading: **Comparative Analysis: {focus}**
* Use a subheading: **A Comparison of {actors_to_compare}**
* Create two primary sections with the following headings: **Points of Alignment** and **Points of Divergence**.
* Under each heading, use bullet points to detail each specific point of agreement or disagreement.
* For each bullet point, first state the issue of alignment/divergence in bold. Then, on nested lines, present the position and supporting evidence for each actor involved in that specific point.

---
DOCUMENTS:
{documents_text}
---

COMPARATIVE ANALYSIS:
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
def generate_actor_comparison_summary(state: State, actor_comparison_prompt: str, subject_matter:str, focus: str,
                                 actors_to_compare: str,
                               temperature: float) -> State:
    print(len(state['extracted_documents']))
    actors_to_compare_prompt_formatted = actor_comparison_prompt.format(documents_text=state['extracted_documents'], subject=subject_matter, focus=focus,
                                                                       actors_to_compare=actors_to_compare)
    summary = call_llm_flash(actors_to_compare_prompt_formatted, temperature=temperature)
    return state.update(summary=summary)


def structured_compare_actor_positions_build():
    summary_app = (
        ApplicationBuilder()
        .with_actions(
            sql_select_overview_documents,
            generate_actor_comparison_summary,
            # insert_extractions_sql,
            # save_research_to_json
        )
        .with_transitions(
            ("sql_select_overview_documents", "generate_actor_comparison_summary"),
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
#     halt_after=["generate_actor_comparison_summary"],
#     inputs={
#         "subject_matter": subject_matter,
#         "focus": focus,
#         "fields":fields,
#         "document_ids": document_ids,
#         "actor_comparison_prompt":actor_comparison_prompt,
#         "actors_to_compare": actors_to_compare,
#         "temperature":0.2,
#         "conn": conn,
#         "cursor": cursor,
#     }
# )
