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

two_part_summary_prompt = """
You are an expert policy analyst. Your task is to generate a comprehensive, two-part executive summary.

**Research Context:**
* **Subject:** {subject}
* **Focus:** {focus}

First, internally analyze the provided document(s) by meticulously following the 'Rules for Analysis' below. These rules are for your process only. DO NOT use the rule titles (e.g., "Rule 1.1") as headers in your final output.
Second, structure your final, user-facing response according to the 'Output Formatting Instructions'.

### **Rules for Analysis (Internal Use Only)**

**Rule 1.1: Identify the Core Problem.**
* **Goal:** Create a concise "problem statement."
* **Step A: Find the Subject.** From Section 1 of the document(s), extract the `Primary Domestic Policy Issue(s) Addressed`. This is the "what."
* **Step B: Find the Complicating Factor.** From Section 5, find the fundamental tension in the `Overall Challenges or Systemic Issues Identified by Report` field. This is the "why it's hard."
* **Step C: Synthesize the Problem Statement.** Combine these points into a single, compelling 1-2 sentence statement, following the pattern: "The core issue is [The Subject], which is complicated by [The Complicating Factor]."

**Rule 1.2: Detail the Key Findings and Context.**
* **Goal:** Create a narrative explaining the current situation, the key players, and their dynamics.
* **Step A: Set the Scene.** From Section 3, use the `Current Status/Situation Overview` to establish the factual baseline. Pull out 2-3 critical statistics or facts.
* **Step B: Identify Key Actor Dynamics.** Scan Section 4 to identify the 2-4 most influential actors. Use Section 5's `Interactions & Interdependencies` field to explain the relationships (conflicts, cooperation) between them in a narrative format.
* **Step C: Highlight Outcomes and Challenges.** For the key actors, briefly summarize their successes and failures using information from the `Reported Outcomes/Impacts/Effectiveness` and `Reported Challenges, Criticisms...` fields.

**Rule 1.3: State the Main Conclusions and Recommendations.**
* From Section 7, use the `Report's Main Conclusion(s) or Key Judgments` to state the report's final word.
* From Section 5, list the potential solutions presented in `Policy Options or Alternatives Discussed by Report`.
* If available, add any `Issues for Governing/Legislative Body(ies) Highlighted by Report` from Section 6.
* Combine these into a final paragraph for Part 1.

**Rule 2.1: Identify Information Gaps.**
* Carefully read through Section 4. If a field contains "**Not Specified in Report**", list what information is missing.
* Read through the document(s), especially Section 7, looking for phrases that indicate uncertainty (e.g., "is less clear," "lack of comparable data"). Explicitly state these as information gaps.

**Rule 2.2: Propose Actionable Next Steps.**
* For each information gap, propose a concrete action to fill it (e.g., "Conduct outreach to [Stakeholder Name] to determine their official stance.").
* Review the `Policy Options or Alternatives` from Section 5. For each option, propose a next step to evaluate its feasibility (e.g., "Conduct a cost-benefit analysis of [Policy Option].").

### **Output Formatting Instructions (Follow for Final Response)**

**Part 1: Summary of the Research**
* Use a main heading: **Executive Summary: {subject}**
* The first paragraph should be the 'Core Problem' you identified in Rule 1.1.
* Use a subheading for the next section: **Key Findings on {focus}**
* Under this subheading, write a flowing narrative that combines the 'Key Findings and Context' (Rule 1.2) and the 'Main Conclusions and Recommendations' (Rule 1.3).

**Part 2: Recommended Next Steps**
* Use a single heading: **Priority Next Steps**
* Based on your analysis in Rules 2.1 and 2.2, create a single, condensed, bulleted list.
* This list should synthesize the most critical information gaps and their corresponding actionable next steps.
* **Prioritize this list by selecting only the items most relevant to the research focus: "{focus}".** Only include the top 3-5 most important next steps.

---
DOCUMENTS:
{documents_text}
---

EXECUTIVE SUMMARY:
"""

from burr.core import action, State, ApplicationBuilder, ApplicationContext, Action
@action(reads=[], writes=['extracted_documents'])
def sql_select_overview_documents(state: State,document_ids: list, cursor, fields) -> State:
    ## change to the run_id when using it with the project to only select the generated documents in the project/stream
    # fields = ['overview', 'run_id', 'run_timestamp', 'project_id', 'subject_matter', 'focus','source_document']
    documents = cursor.execute("""SELECT {fields} FROM overviews
                                   WHERE source_document IN ({number_of_documents});""".format(number_of_documents=', '.join(['?']*len(document_ids)),
                                                                                               fields=', '.join(fields)),
                               [x for x in document_ids]).fetchall()
    documents_df = pd.DataFrame(documents, columns=fields)
    documents_df = documents_df.sort_values(by=['run_timestamp'], ascending=False).drop_duplicates(subset=['source_document'], keep='first')
    extracted_documents = documents_df['overview'].to_list()
    return state.update(extracted_documents=extracted_documents)

@action(reads=['extracted_documents'], writes=['summary'])
def generate_executive_summary(state: State, summary_prompt_template: str, subject_matter:str, focus: str,
                               temperature: float) -> State:
    two_part_summary_prompt_formatted = summary_prompt_template.format(documents_text=state['extracted_documents'], subject=subject_matter, focus=focus)
    summary = call_llm_flash(two_part_summary_prompt_formatted, temperature=temperature)
    return state.update(summary=summary)


def structured_executive_summary_report_build():
    summary_app = (
        ApplicationBuilder()
        .with_actions(
            sql_select_overview_documents,
            generate_executive_summary,
            # insert_extractions_sql,
            # save_research_to_json
        )
        .with_transitions(
            ("sql_select_overview_documents", "generate_executive_summary"),
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
