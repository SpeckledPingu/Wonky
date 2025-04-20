

prompt_1_brainstorm_q = """
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

prompt_1_format_enhanced = """
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

prompt_2_extract_enhanced = """
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

prompt_2_draft_log_enhanced = """
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

prompt_3_synthesize_q1_enhanced = """
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

prompt_3_insights_enhanced = """
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

prompt_4_findings_enhanced = """
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

prompt_4_answer_q1_enhanced = """
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


prompt_4_conclusion_enhanced = """
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

