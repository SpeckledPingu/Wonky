Okay, let's adapt the enhanced SIRP prompts specifically for a smaller, less capable Language Model (like a hypothetical "Gemma 3 4B" or similar models in the few-billion parameter range). These prompts break down tasks further, use simpler language, and rely more heavily on human guidance and review.

Key Changes for Smaller LLMs:

Simpler Tasks: Complex steps like synthesis are broken down or simplified.
Highly Explicit Instructions: Rules are very direct, leaving minimal room for ambiguity.
Rigid Formatting: Expected output formats are simple lists or predefined structures.
Reduced Context: Prompts focus on essential inputs for the immediate task.
More Human Steps: Explicitly marking where human review, synthesis, or input is essential.
Citation Pattern Remains the Same: Q#, N#, S##, I##, A##, C#

Enhanced & Simplified Step 1 Prompts (SIRP for Smaller LLM)

LLM Role: Minimal. Can perform simple list generation or formatting.
Human Role: Defines all core content (objective, questions, scope, needs, sources, assumptions, constraints).
Python

# --- HUMAN INPUTS (Define all Step 1 fields as Python variables/structures) ---
# research_topic, research_focus, research_objective, q1_text, q2_text, etc.

# --- (Optional) Simplified Prompt 1.1 (Brainstorm Assist - Example for Needs) ---
prompt_1_brainstorm_n_simple = f"""
My research objective is: "{research_objective}"
My key research questions are:
Q1: {q1_text}
Q2: {q2_text}

List potential *types* of information I might need to find to answer these questions.
Use a simple bullet point list. Do not explain why. Just list information types.

Potential Information Types Needed:
* [LLM generates list]
"""
# brainstormed_needs = llm_generate(prompt_1_brainstorm_n_simple)
# --- HUMAN REVIEWS and selects/refines final N1, N2... ---

# --- (Optional) Simplified Prompt 1.2 (Formatting Assist) ---
# step1_doc = { ... All human-defined content ... } # Create the dictionary first

prompt_1_format_simple = f"""
Format the following information using the exact field names provided.

Input Information:
---
{step1_doc}
---

**Formatting Rules:**
1.  Use each field name exactly once as a heading or label.
2.  Present the information under its correct field name.
3.  Use simple lists for Scope, Needs, Assumptions, Constraints.

**Formatted Document:**
"""
# formatted_step1_doc = llm_generate(prompt_1_format_simple)
# --- HUMAN REVIEWS/FINALIZES step1_doc (the structured data dictionary is primary) ---
# step1_doc['Next Step Reference'] = "Collect information based on N1, N2, N3 for Q1, Q2. Log findings in 'Information Gathering Log & Source Assessment'."
Enhanced & Simplified Step 2 Prompts (SIRP for Smaller LLM)

LLM Role: Extract very specific facts/quotes based on keywords; format log entries rigidly.
Human Role: Formulate queries; heavily review/filter extractions; assign relevance (Q#); write source assessment/assumptions.
Python

# (Query formulation and RAG execution remain the same)
# retrieved_chunks = rag_query(query_for_q1)

# Process each chunk:
# for chunk_text, chunk_metadata in retrieved_chunks:
    # research_question_or_need = The specific Q# or N# this query targeted
    # keywords_for_extraction = ["productivity", "output", "quality", "revenue", "bugs"] # Human provides keywords relevant to Q1/N#

    # Enhanced Prompt 2.2 (Information Extraction - Simplified & Keyword Focused)
    prompt_2_extract_simple = f"""
    Read the Source Document Chunk below. Find sentences containing the following keywords relevant to the research context.

    Research Question/Information Need Context: "{research_question_or_need}"
    Keywords to find sentences for: {keywords_for_extraction}

    Source Document Chunk:
    ---
    {chunk_text_example}
    ---

    **Instructions & Rules for Extraction:**
    1.  **Keyword Search:** Find sentences that contain one or more of the specified 'Keywords'.
    2.  **Relevance Check:** Only list sentences that are also clearly related to the 'Research Question/Information Need Context'.
    3.  **Exact Copy:** Copy the *entire* relevant sentence exactly as it appears.
    4.  **List Output:** Present each found sentence as a bullet point.
    5.  **No Match:** If no sentences match both keywords and relevance, state *exactly*: "No relevant sentences found matching keywords."

    **Relevant Sentences Found:**
    * [LLM lists sentences]
    """
    extracted_sentences = llm_generate(prompt_2_extract_simple)
    # --- CRITICAL HUMAN REVIEW: Analyst reads sentences, selects the actual useful info points, discards noise ---
    # human_selected_info = "[Analyst copies/pastes/edits the truly relevant fact/data from the sentences]"

    # Human determines relevance
    relevant_q_ids = ['Q1'] # Example

    # Enhanced Prompt 2.3 (Draft Log Entry - Very Rigid Formatting)
    prompt_2_draft_log_simple = f"""
    Create an Information Log entry using the data below. Follow the exact format.

    Selected Information Point (from Human Review):
    ---
    {human_selected_info}
    ---
    Source Metadata: {chunk_metadata_example}
    Relevant Research Question(s) (Analyst Assigned): {relevant_q_ids}
    Next Available Info ID: I{i_id_counter}
    Next Available Source ID: S{s_id_counter} # Assuming new source

    **Instructions & Rules for Log Entry Drafting:**
    1.  **Use Exact IDs:** Use I{i_id_counter} and S{s_id_counter}.
    2.  **Use Today's Date:** Use [Insert Today's Date YYYY-MM-DD].
    3.  **Populate Fields:** Fill the fields below *exactly* as specified.
    4.  **Assessment Placeholder:** Use the *exact* placeholder text for 'Source Assessment & Analyst Notes'.

    **Formatted Log Entry Draft:**

    Info ID: I{i_id_counter}
    Date Found: [Today's Date YYYY-MM-DD]
    Information/Data Point: {human_selected_info}
    Source Details: S{s_id_counter} - {chunk_metadata_example.get('source_name', 'N/A')}, {chunk_metadata_example.get('date', 'N/A')}
    Relevance to Research Question(s): {relevant_q_ids}
    Source Assessment & Analyst Notes: [HUMAN INPUT REQUIRED: Assess source credibility, bias, timeliness; note assumptions made interpreting this info.]
    """
    log_entry_draft = llm_generate(prompt_2_draft_log_simple)

    # --- HUMAN FINALIZES log_entry_draft (adds assessment - MANDATORY) ---
    # final_log_entry = { ... structure from prompt, with human assessment added ... }
    # step2_log.append(final_log_entry)
    # i_id_counter += 1
    # s_id_counter += 1
Enhanced & Simplified Step 3 Prompts (SIRP for Smaller LLM)

LLM Role: Perform simple comparisons (contradiction/confirmation) between pre-summarized info points; draft very basic analysis structure. Cannot be relied upon for nuanced synthesis or weighing evidence quality.
Human Role: Crucial for filtering relevant info, summarizing info points concisely for the LLM, interpreting LLM comparisons, considering source quality, formulating the actual Analysis Points (A##), identifying insights.
Python

# --- Perform analysis for each question ---
# Example for Q1

# 1. Identify Relevant Info IDs (Human task)
q1_relevant_info_ids = ['I01', 'I03', 'I05'] # Example

# 2. Human Pre-processes Information for LLM
# Analyst reviews I01, I03, I05 entries (including their own assessment notes)
# Analyst writes *brief summaries* focusing on the core point relevant to Q1.
q1_info_summaries_for_llm = """
- I01 Summary: Large pilots report stable/increased self-reported productivity & revenue (Source S01 assessed as potentially biased).
- I03 Summary: Tech study found lower code volume but higher code quality (fewer bugs) (Source S02 assessed as credible but small sample).
- I05 Summary: Survey shows manager concerns about collaboration impacting productivity (Source S04 reports perceptions, not outcomes).
"""

# 3. Simplified Prompt 3.2a (Identify Simple Relationships)
prompt_3_find_relationships_simple = f"""
Look at the following summaries of information points related to Research Question Q1 about productivity.

Information Point Summaries:
---
{q1_info_summaries_for_llm}
---

**Instructions & Rules:**
1.  **Compare Summaries:** Read pairs of summaries.
2.  **Identify Relationships:** State if any pair seems to:
    * **Confirm:** Say similar things. List the Info IDs (e.g., "I## confirms I##").
    * **Contradict:** Say opposite things. List the Info IDs (e.g., "I## contradicts I##").
    * **Nuance:** Offer different perspectives on the same topic. List the Info IDs (e.g., "I## adds nuance to I##").
3.  **List Findings:** Output findings as a simple list. Do not explain deeply.

**Identified Relationships:**
* [LLM lists relationships]
"""
llm_relationship_findings = llm_generate(prompt_3_find_relationships_simple)
# Example output:
# * I03 adds nuance to I01
# * I05 presents a different angle (concerns) compared to I01/I03 (outcomes)

# --- CRITICAL HUMAN STEP: Formulate Analysis Points (A##) ---
# The human analyst takes the original info points (I##), their *own* quality assessments,
# and the LLM's simple relationship findings (if helpful) to write the actual analysis.
# The LLM is likely unable to do this reliably.
# Analyst writes A1, A2, A3... citing I## appropriately, considering source quality.
human_written_q1_analysis = """
A1: Large pilot studies suggest overall productivity often remains stable or slightly improves (I01), although potential source bias in S01 warrants caution.
A2: Specific tech-focused research indicates a possible shift from quantity to quality (e.g., fewer bugs despite lower code volume) (I03), offering a more nuanced view than aggregate data. Small sample size for I03 is a limitation.
A3: Managerial concerns about collaboration present a potential risk to productivity maintenance, even if measured outcomes haven't consistently shown declines (I05 reflects perception).
"""
# Store human analysis
step3_report['Analysis for Q1'] = human_written_q1_analysis
# Update a_id_counter

# --- Repeat analysis process (Human-centric) for Q2 ---
# ...

# 4. Simplified Prompt 3.3 (Identify Frequent Themes - Simpler than 'Insights')
all_analysis_sections_text = "\n\n".join(step3_report.values()) # Contains human-written A## sections
prompt_3_themes_simple = f"""
Read the following analysis sections.

Analysis Sections for All Questions:
---
{all_analysis_sections_text}
---

**Instructions & Rules:**
1.  **Scan for Keywords:** Identify frequently recurring concepts or keywords across all the analysis sections.
2.  **List Themes:** List the 3-5 most prominent themes found. Use simple terms.

**Prominent Themes Found:**
* [LLM lists themes, e.g., Well-being Improvement, Productivity Nuance, Implementation Challenges]
"""
key_themes_draft = llm_generate(prompt_3_themes_simple)
# --- HUMAN REVIEWS/REFINES themes into actual insights ---
step3_report['Key Insights & Patterns'] = "[HUMAN REVIEWS themes and writes meaningful insights based on them and the A## points]"

# 5. Human Adds Limitations, Confidence, Assumptions (Crucial human judgment)
# step3_report['Limitations & Confidence (Preliminary)'] = "[HUMAN WRITES...]"
# step3_report['Analyst Assumptions (During Analysis & Synthesis)'] = "[HUMAN WRITES...]"
# step3_report['Next Step Reference'] = "Consolidate analysis into clear answers and summary. Output: 'Conclusion & Findings Summary'."
Enhanced & Simplified Step 4 Prompts (SIRP for Smaller LLM)

LLM Role: Draft sections based very strictly on human-curated Step 3 inputs (Insights, Answers derived from human-written A##).
Human Role: Write/finalize A## points; write/finalize key insights; review all LLM drafts heavily; provide final confidence assessment.
Python

# --- Use outputs stored in step3_report and step1_doc ---
# Crucially, step3_report now contains HUMAN-WRITTEN/VALIDATED Analysis Points (A##) and Key Insights.

# 1. Enhanced Prompt 4.1 (Draft Findings Summary - Simpler Input)
prompt_4_findings_simple = f"""
Draft a 'Summary of Key Findings' using *only* the points listed below.

Key Insights & Patterns (Human Curated from Step 3):
---
{step3_report['Key Insights & Patterns']}
---
**Instructions & Rules:**
1.  **Use Only Input:** Summarize using *only* the provided insights.
2.  **Simple List:** Use bullet points for the summary.
3.  **Direct Copy/Rephrase:** You can directly use or slightly rephrase the input points for clarity.

**Summary of Key Findings:**
* [LLM generates bulleted list]
"""
findings_summary_draft = llm_generate(prompt_4_findings_simple)
# --- HUMAN REVIEWS/EDITS ---
# step4_summary['Summary of Key Findings'] = final_findings_summary

# 2. Enhanced Prompt 4.2 (Draft Answers - Relies Heavily on Human-Written A##)
# Example for Q1
prompt_4_answer_q1_simple = f"""
Draft a direct answer to the Research Question using *only* the provided supporting Analysis Points (A##).

Research Question (Q1): "{step1_doc['Key Research Question(s)']['Q1']}"

Supporting Analysis Points (A##) from Step 3 for Q1 (Human Written/Validated):
---
{step3_report['Analysis for Q1']}
---
**Instructions & Rules:**
1.  **Direct Answer:** Create 1-2 sentences that directly answer the question.
2.  **Use ONLY Provided A##:** Base the answer strictly on the findings stated in the A## points.
3.  **Cite A##:** Include the relevant (A##) citations provided in the input text.
4.  **Simple Language:** Use clear and simple language.

**Answer to Question [Q1]:**
"""
q1_answer_draft = llm_generate(prompt_4_answer_q1_simple)
# --- HUMAN REVIEWS/EDITS and assigns C# IDs ---
# step4_summary['Answer to Q1'] = final_q1_answer
# Human assigns C# based on the conclusion points (e.g., C1, C2...)

# --- Repeat for Q2 ---
# ...

# 3. Enhanced Prompt 4.3 (Draft Overall Conclusion - Simple Synthesis)
all_answers_text = f"Answer to Q1: {step4_summary['Answer to Q1']}\n\nAnswer to Q2: {step4_summary['Answer to Q2']}"
prompt_4_conclusion_simple = f"""
Combine the Answers below into a brief overall conclusion related to the Research Objective.

Answers to Key Research Questions:
---
{all_answers_text}
---
Research Objective (from Step 1): "{step1_doc['Research Objective/Purpose']}"

**Instructions & Rules:**
1.  **Combine Answers:** Create 1-2 sentences that summarize the main points from the provided Answers.
2.  **Link to Objective:** Briefly state how these answers relate to the Research Objective.
3.  **Use ONLY Input:** Do not add interpretations not present in the Answers.

**Overall Conclusion(s):**
"""
overall_conclusion_draft = llm_generate(prompt_4_conclusion_simple)
# --- HUMAN REVIEWS/EDITS ---
# step4_summary['Overall Conclusion(s)'] = final_overall_conclusion

# 4. Human Adds Final Limitations, Confidence, Recommendations (MANDATORY Human Judgment)
# step4_summary['Limitations & Confidence'] = "[HUMAN WRITES final assessment...]"
# step4_summary['Recommendations or Implications (Optional)'] = "[HUMAN WRITES...]"
# step4_summary['Supporting Documents Reference'] = "..."

# --- Final Output: step4_summary contains the structured report elements ---
These highly explicit and simplified prompts for the SIRP framework, current as of Friday, April 18, 2025 at 7:15 PM EDT in Richmond, Virginia, are tailored for a smaller LLM. They break tasks into smaller pieces, provide very direct instructions, and clearly delineate where essential human analysis, judgment, and validation are required, especially in the critical steps of evidence assessment, synthesis (formulating A## points), and determining confidence.