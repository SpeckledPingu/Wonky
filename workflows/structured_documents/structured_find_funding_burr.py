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


funding_opportunities_prompt = """
You are an expert grant writer and policy analyst. Your task is to identify all funding opportunities mentioned in the provided research document(s) and present them in a clear, structured, and actionable format.

**Research Context:**
* **Subject:** {subject}
* **Focus:** {focus}

Your analysis must be comprehensive, extracting specific details for each opportunity. Pay special attention to opportunities that are most relevant to the research focus.

### **Analysis Rules**

**Rule 1: Systematically Scan for Funding Keywords.**
* Thoroughly read the entire document with the specific goal of identifying any mention of financial support.
* Search for keywords like "funding," "grant," "loan," "subsidy," "appropriations," "fund," "allocated," and "discounts."
* Pay close attention to these key fields across all sections: `Funding/Resource Allocation...`, `Policy Levers, Programs, or Actions...`, and `Key Actions by Primary Governing/Legislative Body...`.

**Rule 2: Extract a Detailed Profile for Each Opportunity.**
* For every funding opportunity you identify, you must extract the following specific details from the text:
    * **Program Name:** The official name of the grant, fund, or program.
    * **Administering Agency:** The government body or organization responsible for managing the funds.
    * **Purpose & Objective:** A concise description of what the funding is intended to achieve.
    * **Eligibility & Recipients:** Who the funding is for (e.g., states, counties, specific industries, non-profits, low-income households).
    * **Financial Details:** Any specific monetary amounts, percentages, or cost-sharing requirements mentioned in the text. If no specific amount is given, note that it is not specified.
    * **Context and Use Case:** Based on the document's context, provide a brief explanation of *why* this funding is important and a hypothetical but plausible scenario of how it would be used. For example, "This fund addresses the high cost of last-mile fiber deployment. A rural town could use this grant to partner with a local ISP to connect its school and library to a regional fiber network."
    * **Source Reference:** The direct citation from the text `[ID__Section__Paragraph]` that provides this information.

**Rule 3: Prioritize by Relevance.**
* After identifying all opportunities, review them to determine which are most directly related to the research **Focus**.
* The final output should be ordered with the most relevant opportunities appearing first.

### **Output Formatting**

* Use a main heading: **Funding Opportunities for {subject}**
* Present the final output as a list of detailed funding profiles.
* For each program, use its name as a bolded subheading.
* Under each subheading, use labeled bullet points to present the comprehensive details you extracted in Rule 2. Ensure each piece of information is clearly labeled (e.g., "Administering Agency:", "Purpose & Objective:", "Context and Use Case:").

---
DOCUMENTS:
{documents_text}
---

FUNDING OPPORTUNITIES:
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
def generate_funding_opportunities_summary(state: State, funding_opportunities_prompt: str, subject_matter:str, focus: str,
                               temperature: float) -> State:
    print(len(state['extracted_documents']))
    actors_to_compare_prompt_formatted = funding_opportunities_prompt.format(documents_text=state['extracted_documents'], subject=subject_matter, focus=focus)
    summary = call_llm_flash(actors_to_compare_prompt_formatted, temperature=temperature)
    return state.update(summary=summary)


def structured_compare_actor_positions_build():
    summary_app = (
        ApplicationBuilder()
        .with_actions(
            sql_select_overview_documents,
            generate_funding_opportunities_summary,
            # insert_extractions_sql,
            # save_research_to_json
        )
        .with_transitions(
            ("sql_select_overview_documents", "generate_funding_opportunities_summary"),
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
