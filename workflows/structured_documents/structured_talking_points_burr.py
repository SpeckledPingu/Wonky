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


talking_points_prompt = """
You are an expert communications strategist and policy analyst. Your task is to generate a set of clear, persuasive talking points based on the provided research document(s).

**Assignment Context:**
* **Subject:** {subject}
* **Focus:** {focus}
* **Target Audience:** {audience}
* **Viewpoint to Advocate:** {viewpoint}

Analyze the documents according to the rules below to extract the most relevant information. Then, format your final output as instructed.

### **Analysis Rules**

**Rule 1: Deconstruct the Audience and Viewpoint.**
Before reading the document, first deeply analyze the assignment context.
* **1.1 Analyze the Target Audience:**
    * **Priorities:** What are the likely primary concerns of this audience? (e.g., For a 'County Commissioner', priorities might be budget impact, local jobs, and constituent complaints. For 'Industry Lobbyists', priorities might be profit, market barriers, and regulation.)
    * **Knowledge Level:** How much will this audience know about the topic? Frame your language accordingly. (e.g., Use technical terms for 'Federal Regulators'; use simple, direct language for a 'Community Town Hall'.)
    * **Disposition:** What is their likely stance toward your viewpoint? (e.g., If 'friendly', reinforce shared values. If 'hostile', find common ground or focus on undeniable facts. If 'neutral', use data to build a logical case.)
* **1.2 Analyze the Viewpoint to Advocate:**
    * **Core Objective:** What is the ultimate goal? (e.g., To secure funding, to block a regulation, to encourage public support, to discredit an opposing view.)
    * **Underlying Values:** What values does this viewpoint represent? (e.g., "Fiscal responsibility," "public safety," "economic opportunity," "innovation," "equity.") Your messaging should subtly appeal to these values.

**Rule 2: Find and Align Evidence.**
* With the context from Rule 1 in mind, thoroughly scan the document(s) for facts, statistics, policy details, and expert conclusions that can be used to support your **Viewpoint**.
* Mine these key fields for evidence: `Current Status/Situation Overview`, `Policy Levers, Programs,or Actions...`, `Funding/Resource Allocation...`, `Reported Outcomes/Impacts/Effectiveness...`, and `Policy Options or Alternatives Discussed...`.
* For each piece of evidence, consider how it can be framed to appeal to the **Audience's Priorities** and **Viewpoint's Values**.

**Rule 3: Construct and Tailor Each Talking Point.**
* For each talking point, construct two parts:
    * **A. The Message:** A single, concise, and persuasive sentence. This message is your interpretation and argument. It should be explicitly tailored to the audience's priorities, knowledge level, and disposition as determined in Rule 1.1.
    * **B. The Evidence:** The specific data point, finding, or policy detail from the document that directly supports the message. You must include the citation `[ID__Section__Paragraph]` if it is present in the source text. This grounds your argument in fact.

**Rule 4: Prioritize for Maximum Impact.**
* From all the points you could make, select only the 3-5 most impactful arguments.
* Your selection should be based on which points are most likely to persuade the **Target Audience**, as analyzed in Rule 1.1. Curation is essential.

### **Output Formatting**

* Use a main heading: **Talking Points: {viewpoint}**
* Add a subheading to specify the audience: **Prepared for: {audience}**
* Present the final output as a bulleted list. Each item in the list represents a single talking point.
* For each talking point, first state **The Message**, then on a new nested line, provide **The Evidence**.

---
DOCUMENTS:
{documents_text}
---

TALKING POINTS:
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
def generate_talking_points_summary(state: State, talkingpoints_prompt: str, subject_matter:str, focus: str,
                                 audience:str, viewpoint:str,
                               temperature: float) -> State:
    print(len(state['extracted_documents']))
    talkingpoints_prompt_formatted = talkingpoints_prompt.format(documents_text=state['extracted_documents'], subject=subject_matter, focus=focus,
                                                                       audience=audience, viewpoint=viewpoint)
    summary = call_llm_flash(talkingpoints_prompt_formatted, temperature=temperature)
    return state.update(summary=summary)


def structured_talking_points_build():
    summary_app = (
        ApplicationBuilder()
        .with_actions(
            sql_select_overview_documents,
            generate_talking_points_summary,
            # insert_extractions_sql,
            # save_research_to_json
        )
        .with_transitions(
            ("sql_select_overview_documents", "generate_talking_points_summary"),
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
#     halt_after=["generate_talking_points_summary"],
#     inputs={
#         "subject_matter": subject_matter,
#         "focus": focus,
#         "fields":fields,
#         "audience": audience,
#         "viewpoint": viewpoint,
#         "document_ids": document_ids,
#         "talkingpoints_prompt":talking_points_prompt,
#         "temperature":0.2,
#         "conn": conn,
#         "cursor": cursor,
#     }
# )
