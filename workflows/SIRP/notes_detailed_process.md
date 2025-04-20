Okay, let's infuse the prompts for the Simplified Investigative Research Protocol (SIRP) framework with the same level of detail, explicit rules, and clear linkages you liked in the enhanced SDAP prompts. This will provide much clearer guidance for leveraging an LLM effectively within the SIRP workflow.

Citation Pattern Used:

Q#: Key Research Question ID (from Step 1)
N#: Information Need ID (from Step 1 Plan)
S##: Source ID (from Step 2 Log)
I##: Information Point ID (from Step 2 Log, linked to a Source S##)
A##: Analysis Point ID (from Step 3 Report, linked to Q# and I##)
C#: Conclusion ID (from Step 4 Summary, linked to A##)
Enhanced Step 1 Prompts: Research Framing & Plan Document

LLM Role: Optional brainstorming assist; drafting/formatting the final document based on structured human input.
Human Role: Define the core topic, objective, questions (Q#), scope, initial needs (N#), sources, assumptions, and constraints. This step remains primarily human-directed.
Python

# --- HUMAN INPUTS (as before) ---
research_topic = "Potential Impact of 4-Day Work Week (4DWW) on Employee Productivity and Well-being"
research_focus = "Focus on mid-sized (100-1000 employees) US technology companies, evidence from 2018-2025."
research_objective = "To inform a leadership decision on whether to pilot a 4DWW program by summarizing existing research on its effects."
# ... (Define Q1, Q2, Scope, N1, N2, N3, Assumptions, Constraints as Python variables/structures) ...

# --- (Optional) Enhanced Prompt 1.1 (Brainstorming Assist - Example for Questions) ---
prompt_1_brainstorm_q = f"""
Given the following research objective and focus, brainstorm potential Key Research Questions.

Research Objective: "{research_objective}"
Research Focus: "{research_focus}"

**Instructions & Rules for Brainstorming Questions:**
1.  **Relevance:** Questions must directly relate to the objective and focus.
2.  **Specificity:** Questions should be specific enough to guide research (avoid overly broad questions).
3.  **Answerability:** Questions should be potentially answerable through research (avoid purely speculative questions).
4.  **Categorization:** Consider questions related to different facets mentioned in the objective/focus (e.g., specific productivity metrics, different well-being aspects).
5.  **Format:** List potential questions clearly.

**Brainstormed Key Research Questions:**
"""
# brainstormed_questions = llm_generate(prompt_1_brainstorm_q)
# --- HUMAN REVIEWS and selects/refines final Q1, Q2... ---

# --- (Optional) Enhanced Prompt 1.2 (Drafting Assist) ---
# Create the structured step1_doc dictionary with all human-defined content first (Q#, N#, Scope etc.)
# step1_doc = { ... filled with human inputs and selected Q#/N# ... }

prompt_1_format_enhanced = f"""
Draft the 'Research Framing & Plan Document' using the structured information below. Follow the specified fields precisely.

Structured Information:
---
{step1_doc} # Pass the complete dictionary
---

**Instructions & Rules for Drafting Document:**
1.  **Use Provided Fields:** Structure the output using *exactly* these fields: 'Research Topic/Title', 'Date Initiated', 'Prepared By', 'Research Objective/Purpose', 'Key Research Question(s)' (listing Q# and text), 'Scope of Research' (with 'In Scope' and 'Out of Scope' sub-sections), 'Initial Information Needs & Potential Sources (Research Plan)' (listing N#, Category, Sources), 'Assumptions & Constraints' (with 'Assumptions' and 'Constraints' sub-sections), 'Next Step Reference'.
2.  **Populate Accurately:** Fill each field using the corresponding data from the 'Structured Information' provided above.
3.  **Clarity:** Present the information clearly and professionally.

**Drafted Research Framing & Plan Document:**
"""
# formatted_step1_doc = llm_generate(prompt_1_format_enhanced)
# --- HUMAN REVIEWS/FINALIZES step1_doc ---
Enhanced Step 2 Prompts: Information Gathering Log & Source Assessment

LLM/RAG Role: Retrieve relevant information chunks; extract specific information points based on strict rules; draft log entries following a precise format.
Human Role: Formulate effective RAG queries; review/validate LLM extractions; assign relevance (Q#); provide critical source assessment notes and assumptions for each information point (I##).
Python

# (Query formulation and RAG execution remain the same)
# retrieved_chunks = rag_query(query_for_q1)

# Process each chunk:
# for chunk_text, chunk_metadata in retrieved_chunks:
    # ... (Assume chunk_text_example, chunk_metadata_example defined)
    # research_question_or_need = The specific Q# or N# this query targeted

    # Enhanced Prompt 2.2 (Information Extraction - More Detailed Rules)
    prompt_2_extract_enhanced = f"""
    Analyze the following Source Document Chunk regarding the Research Question/Information Need context.

    Research Question/Information Need Context: "{research_question_or_need}"

    Source Document Chunk:
    ---
    {chunk_text_example}
    ---
    Source Metadata: {chunk_metadata_example}

    **Instructions & Rules for Extraction:**
    1.  **Strict Relevance:** Extract information *only* if it directly and substantively addresses the specified 'Research Question/Information Need Context'. Discard marginally relevant or background information.
    2.  **Extract Facts/Data/Quotes:** Focus on extracting specific, verifiable facts, quantitative data points, key findings reported by the source, or direct, concise quotes that capture a crucial point.
    3.  **Objectivity & Accuracy:** Extract information exactly as presented. Do *not* paraphrase in a way that changes meaning. Do *not* insert external knowledge or analyst interpretation. Ensure accuracy if transcribing quotes or data.
    4.  **Attribute Clearly:** If the source attributes a finding to a specific study or entity mentioned within the chunk, include that attribution.
    5.  **Handle Multiple Points:** List distinct relevant points separately (e.g., using bullet points).
    6.  **Explicit 'No Info' Handling:** If *no* information meeting the above criteria is found, state *exactly*: "No specific relevant information found in this chunk addressing the research context."
    7.  **Conciseness:** Keep extracted points brief but complete enough to be understood standalone.

    **Extracted Information:**
    """
    extracted_info = llm_generate(prompt_2_extract_enhanced)
    # --- HUMAN REVIEWS extracted_info for accuracy and relevance ---

    # Human determines relevance
    relevant_q_ids = ['Q1'] # Example

    # Enhanced Prompt 2.3 (Draft Log Entry - More Detailed Rules)
    prompt_2_draft_log_enhanced = f"""
    Draft a structured Information Log entry using the provided components. Adhere strictly to the specified format and rules.

    Extracted Information Point(s):
    ---
    {extracted_info} # Reviewed output from Prompt 2.2
    ---
    Source Metadata: {chunk_metadata_example}
    Relevant Research Question(s) (Analyst Assigned): {relevant_q_ids}
    Next Available Info ID: I{i_id_counter}
    Next Available Source ID: S{s_id_counter} # Assuming new source for simplicity

    **Instructions & Rules for Log Entry Drafting:**
    1.  **Use Assigned IDs:** Use the provided 'Next Available Info ID' (I{i_id_counter}) and 'Next Available Source ID' (S{s_id_counter}).
    2.  **Date Field:** Use today's date: [Insert Today's Date YYYY-MM-DD].
    3.  **Information Field:** Populate 'Information/Data Point' precisely with the 'Extracted Information Point(s)'.
    4.  **Source Details Field:** Create the citation using 'Source Metadata'. Format: "S{s_id_counter} - [Source Name/Title from metadata], [Date from metadata, if available]". Ensure Source ID S{s_id_counter} is included.
    5.  **Relevance Field:** Populate 'Relevance to Research Question(s)' with the exact list provided (e.g., ['Q1', 'Q2']).
    6.  **Assessment Field:** Include the field 'Source Assessment & Analyst Notes' but leave its content as *exactly*: "[HUMAN INPUT REQUIRED: Assess source credibility, bias, timeliness; note assumptions made interpreting this info.]". This field requires mandatory human input later.
    7.  **Output Format:** Generate the output using *only* the following field labels and structure:
        - Info ID: [ID]
        - Date Found: [Date]
        - Information/Data Point: [Content]
        - Source Details: [Content]
        - Relevance to Research Question(s): [Content]
        - Source Assessment & Analyst Notes: [Placeholder Text]

    **Formatted Log Entry Draft:**
    """
    log_entry_draft = llm_generate(prompt_2_draft_log_enhanced)

    # --- HUMAN FINALIZES log_entry_draft (adds assessment) ---
    # final_log_entry = ... (structure defined above, with human assessment added)
    # step2_log.append(final_log_entry)
    # i_id_counter += 1
    # s_id_counter += 1
Enhanced Step 3 Prompts: Analysis & Synthesis Report

LLM Role: Perform analysis guided by stricter rules, focusing on evidence quality, patterns, and rigorous citation.
Human Role: Validate groupings, guide focus, critically review LLM's logic, identify ultimate insights, add limitations/assumptions.
Python

# (Assume Step 1 defined Q1, Q2; Step 2 populated step2_log)

# --- Perform analysis for each question ---
# Example for Q1

# 1. Identify & Prepare Relevant Information Text (Human task)
q1_relevant_info_ids = [entry['Info ID'] for entry in step2_log if 'Q1' in entry['Relevance to Research Question(s)'] ]
q1_relevant_info_entries_text = "" # Populate with full text of relevant I## entries, crucially including the 'Source Assessment & Analyst Notes' field content for each.

# 2. Enhanced Prompt 3.2 (Synthesize & Draft Analysis - More Detailed Rules)
prompt_3_synthesize_q1_enhanced = f"""
Analyze the provided information points to answer the Research Question below. Follow all instructions carefully.

Research Question (Q1): "{step1_doc['Key Research Question(s)']['Q1']}"

Relevant Information Points (Info ID, Info Content, Source Details, Source Assessment Notes):
---
{q1_relevant_info_entries_text} # Includes human assessment notes
---
**Instructions & Rules for Analysis & Synthesis:**
1.  **Address Question Directly:** Your entire analysis must focus on answering Research Question Q1 using *only* the provided information points.
2.  **Integrate Source Assessment:** Explicitly reference the 'Source Assessment & Analyst Notes' for Info IDs (I##) when discussing their contribution. Explain *how* the assessment (e.g., bias, reliability, subjectivity) affects the weight or interpretation of that information in your analysis. Down-weight information assessed as weak or biased.
3.  **Identify Specific Patterns:** Analyze the relationships between information points. Explicitly identify and describe:
    * **Confirmations:** Where different sources/data points support the same finding.
    * **Contradictions:** Where sources/data points disagree. Analyze potential reasons for contradiction based on source assessments.
    * **Trends/Nuances:** Patterns emerging from the data (e.g., consistent finding across different contexts, differing results based on methodology).
4.  **Formulate Analytical Points (A##):** Synthesize findings into distinct, concise analytical points (label sequentially starting A{a_id_counter}). Each A## should represent a significant conclusion *derived from the analysis*, not just a summary of one piece of info.
5.  **Mandatory Citation:** *Every* substantive claim, finding, or interpretation within each Analysis Point (A##) *must* be followed immediately by citation of the supporting Info ID(s) in parentheses, like this: (I01, I03). Claims without direct citation to the provided I## are not allowed.
6.  **Acknowledge Internal Limitations:** Explicitly mention limitations *arising directly from the provided information itself* – e.g., "Conflicting findings between I01 (high credibility) and I05 (lower credibility) create uncertainty," or "Lack of quantitative data on [specific aspect] prevents a firm conclusion here."
7.  **Output Structure:** Organize the output clearly under the heading "Analysis & Synthesis for Question [Q1]:". Ensure Analysis Points (A##) are distinct and citations (I##) are correctly placed.

**Analysis & Synthesis for Question [Q1]:**
"""
q1_analysis_section_draft = llm_generate(prompt_3_synthesize_q1_enhanced)
# --- HUMAN REVIEWS/EDITS q1_analysis_section_draft for logical soundness, citation accuracy, insight depth ---
# step3_report['Analysis for Q1'] = reviewed_q1_analysis_section
# Update a_id_counter

# --- Repeat analysis process for Q2 ---
# ...

# 3. Enhanced Prompt 3.3 (Draft Key Insights - More Detailed Rules)
all_analysis_sections_text = "\n\n".join(step3_report.values())
prompt_3_insights_enhanced = f"""
Review the following Analysis Sections derived from the research. Identify overarching insights relevant to the Research Objective.

Analysis Sections for All Questions:
---
{all_analysis_sections_text}
---
Research Objective (from Step 1): "{step1_doc['Research Objective/Purpose']}"

**Instructions & Rules for Identifying Key Insights:**
1.  **Synthesize Across Analysis:** Identify insights emerging from the *combination* of findings across *all* analysis sections (for Q1, Q2, etc.). Do not simply repeat individual A## points.
2.  **Relevance to Objective:** Insights must be directly relevant to informing the overall 'Research Objective'.
3.  **Significance & Novelty:** Focus on the 3-5 *most important* or potentially *non-obvious* takeaways revealed by the research as a whole. What patterns or conclusions stand out when looking at the bigger picture?
4.  **Conciseness:** State insights clearly and briefly.

**Key Insights & Patterns:**
"""
key_insights_draft = llm_generate(prompt_3_insights_enhanced)
# --- HUMAN REVIEWS/EDITS key_insights_draft ---
# step3_report['Key Insights & Patterns'] = final_key_insights

# 4. Human Adds Overall Limitations, Confidence, Assumptions (as before)
# ... step3_report['Limitations & Confidence (Preliminary)'] = "[HUMAN WRITES...]" etc.
Enhanced Step 4 Prompts: Conclusion & Findings Summary

LLM Role: Draft sections based strictly on curated Step 3 outputs, maintaining traceability through citations (A##).
Human Role: Final verification, writing the crucial overall confidence assessment and limitations summary.
Python

# --- Use outputs stored in step3_report and step1_doc ---

# 1. Enhanced Prompt 4.1 (Draft Findings Summary - More Detailed Rules)
prompt_4_findings_enhanced = f"""
Draft the 'Summary of Key Findings' section using *only* the 'Key Insights & Patterns' provided below.

Key Insights & Patterns (from Step 3 Analysis):
---
{step3_report['Key Insights & Patterns']} # Use the final, reviewed version
---
**Instructions & Rules for Drafting Findings Summary:**
1.  **Strict Adherence:** Base the summary *exclusively* on the provided 'Key Insights & Patterns'. Do not add information or interpretations from earlier analysis steps unless they are reflected in these insights.
2.  **Conciseness:** Summarize each key insight briefly and clearly. Bullet points are preferred.
3.  **Focus on Importance:** Ensure the summary reflects the most significant takeaways relevant to the overall research objective.

**Summary of Key Findings:**
"""
findings_summary_draft = llm_generate(prompt_4_findings_enhanced)
# --- HUMAN REVIEWS/EDITS ---
# step4_summary['Summary of Key Findings'] = final_findings_summary

# 2. Enhanced Prompt 4.2 (Draft Answers to Questions - More Detailed Rules)
# Example for Q1
prompt_4_answer_q1_enhanced = f"""
Draft a direct answer to the Research Question below, using *only* the provided supporting Analysis Points (A##).

Research Question (Q1): "{step1_doc['Key Research Question(s)']['Q1']}"

Supporting Analysis Points (A##) from Step 3 for Q1:
---
{step3_report['Analysis for Q1']} # Use the final, reviewed version
---
**Instructions & Rules for Drafting Answer:**
1.  **Direct Answer:** Formulate a clear, concise answer that *directly* addresses the Research Question Q1.
2.  **Based ONLY on Analysis Points:** The answer must be solely derived from the findings presented in the provided 'Supporting Analysis Points (A##)'. Do not introduce external information.
3.  **Mandatory Citation:** *Must* cite the specific Analysis Point ID(s) (e.g., A1, A2) that support each part of the answer, like this: (A1, A3).
4.  **Reflect Nuance:** If the supporting A## points indicated nuance, conflict, or uncertainty, the answer must briefly reflect this.
5.  **Conciseness:** Avoid lengthy explanations; summarize the core finding relevant to the question.

**Answer to Question [Q1]:**
"""
q1_answer_draft = llm_generate(prompt_4_answer_q1_enhanced)
# --- HUMAN REVIEWS/EDITS and assigns C# IDs ---
# step4_summary['Answer to Q1'] = final_q1_answer
# Assign C# IDs like C1, C2... based on key conclusions within the answer.

# --- Repeat for Q2 ---
# ...

# 3. Enhanced Prompt 4.3 (Draft Overall Conclusion - More Detailed Rules)
all_answers_text = f"Answer to Q1: {step4_summary['Answer to Q1']}\n\nAnswer to Q2: {step4_summary['Answer to Q2']}"
prompt_4_conclusion_enhanced = f"""
Draft an overarching conclusion by synthesizing the findings and answers in relation to the Research Objective.

Summary of Key Findings:
---
{step4_summary['Summary of Key Findings']}
---
Answers to Key Research Questions:
---
{all_answers_text}
---
Research Objective (from Step 1): "{step1_doc['Research Objective/Purpose']}"

**Instructions & Rules for Drafting Conclusion:**
1.  **Synthesize Input:** Combine the essence of the 'Summary of Key Findings' and the 'Answers to Key Research Questions' into a cohesive concluding statement.
2.  **Address Objective Directly:** The conclusion *must* explicitly relate back to the 'Research Objective'. What is the final implication or answer relevant to that objective?
3.  **Based ONLY on Input:** Do not introduce new findings, analysis, or recommendations not present in the provided input sections.
4.  **Brevity & Impact:** State the main conclusion(s) briefly and clearly – the "so what?" of the research.

**Overall Conclusion(s):**
"""
overall_conclusion_draft = llm_generate(prompt_4_conclusion_enhanced)
# --- HUMAN REVIEWS/EDITS ---
# step4_summary['Overall Conclusion(s)'] = final_overall_conclusion

# 4. Human Adds Final Limitations, Confidence, Recommendations (as before)
# step4_summary['Limitations & Confidence'] = "[HUMAN WRITES final assessment, synthesizing limitations from Step 3 and overall confidence based on entire process...]"
# step4_summary['Recommendations or Implications (Optional)'] = "[HUMAN WRITES based on conclusions...]"
# step4_summary['Supporting Documents Reference'] = "..."
These significantly more detailed prompts for the SIRP framework, current as of Friday, April 18, 2025 at 7:08 PM EDT in Richmond, Virginia, provide stricter guidance for the LLM at each stage. They emphasize adherence to rules, explicit citation (I##, A##), consideration of source quality (via human notes), logical synthesis, and focusing outputs strictly on the provided inputs from previous steps. This should help ensure the LLM contributes more effectively to generating the structured SIRP documentation while keeping the human analyst firmly in control of critical judgment and final outputs.