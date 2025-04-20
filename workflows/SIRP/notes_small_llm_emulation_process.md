Okay, I understand you want prompts that attempt to automate or assist with the steps previously marked for human review and input within the simplified SIRP framework, tailored for a smaller LLM.

❗ Important Caveat: Replacing critical human judgment (like source assessment, nuanced analysis, confidence determination) with prompts, especially for smaller LLMs (like a hypothetical "Gemma 3 4B"), carries significant risks. Smaller models have limitations in reasoning, world knowledge, and detecting subtle bias or complex relationships. The prompts below are designed to simulate or assist these steps, but their outputs MUST be critically reviewed, validated, and likely edited or rewritten by a human analyst. Do not rely on these outputs blindly. They are intended as drafts or starting points for human judgment, not replacements for it.

Here are adapted prompts for the previously identified human steps within the simplified SIRP workflow, designed with very explicit instructions for a smaller LLM:

Adapting Step 2: Information Gathering Log & Source Assessment

Human Step to Automate/Assist: Writing the 'Source Assessment & Analyst Notes' for each log entry (I##).
Python

# (After Prompt 2.3 drafts the basic log entry including the placeholder for assessment)
# Assume log_entry_draft is the output, human_selected_info, chunk_metadata_example exist

# Enhanced Prompt 2.4 (Attempt Preliminary Source Assessment - VERY Experimental)
prompt_2_assess_source_simple = f"""
Review the Source Metadata and the Extracted Information below. Provide a *preliminary* assessment based *only* on patterns you can detect.

Source Metadata: {chunk_metadata_example} # e.g., {'source_name': 'GameDev Insights Report', 'date': '2023'}
Extracted Information Point(s):
---
{human_selected_info} # The specific text extracted
---

**Instructions & Rules for Preliminary Assessment:**
1.  **Source Type Guess:** Based on the 'source_name' in the metadata, guess the likely source type (e.g., News Article, Blog Post, Academic Paper, Company Report, Forum Post, Official Statistics). State the guessed type.
2.  **Look for Opinion Keywords:** Read the 'Extracted Information Point(s)'. Does the text contain strong opinion words (e.g., "clearly shows", "obviously", "best", "worst", "should")? State YES or NO.
3.  **Look for Data Keywords:** Does the text mention specific numbers, percentages, survey results, or data analysis? State YES or NO.
4.  **Check Date:** Look at the 'date' in the metadata. Is the year recent (e.g., within the last 3 years)? State YES or NO.
5.  **Output Format:** Provide answers *only* in this exact format:
    * Guessed Source Type: [Your guess]
    * Contains Opinion Keywords: [YES/NO]
    * Contains Data Keywords: [YES/NO]
    * Source Year Recent (<= 3 years): [YES/NO]
    * **Analyst Note:** [Add this exact text: "PRELIMINARY ASSESSMENT ONLY. HUMAN MUST VERIFY CREDIBILITY, BIAS, AND CONTEXT."]

**Preliminary Assessment Notes:**
"""
preliminary_assessment_notes = llm_generate(prompt_2_assess_source_simple)

# --- CRITICAL HUMAN STEP ---
# The analyst takes 'preliminary_assessment_notes' as input but performs their *own* thorough assessment,
# considering actual source reputation, author expertise, methodology (if known), potential conflicts of interest,
# consistency with other sources, and adds their own assumptions. The LLM output is just a very basic check.
# The human writes the final 'Source Assessment & Analyst Notes' field in the step2_log entry.
final_assessment_notes = f"""
{preliminary_assessment_notes}
[HUMAN ADDS:] GameDev Insights is a known industry analysis firm (Medium-High Credibility). Report likely aims for objectivity but may focus on positive trends. Data point I01 is quantitative but aggregated. Requires comparison with other sources. Assumption: 'Active users' definition is consistent.
"""
# Update the final_log_entry with these notes before appending to step2_log
Adapting Step 3: Analysis & Synthesis Report

Human Steps to Automate/Assist:
Formulating the actual Analysis Points (A##) after reviewing LLM relationship findings.
Refining LLM-generated themes into meaningful Key Insights.
Writing the Limitations/Confidence/Assumptions section.
Python

# (Assume Step 3 proceeds up to generating 'llm_relationship_findings' using Prompt 3.2a)
# llm_relationship_findings = "* I03 adds nuance to I01\n* I05 presents a different angle (concerns) compared to I01/I03 (outcomes)" # Example output
# Assume q1_relevant_info_entries_text contains the I## summaries and HUMAN assessments

# Enhanced Prompt 3.2b (Attempt Drafting Analysis Point based on *One* Relationship - Experimental)
# This prompt is run *per identified relationship* or *per theme* the human wants to explore.
relationship_to_explore = "I03 adds nuance to I01" # Human identifies this from llm_relationship_findings

prompt_3_draft_A_point_simple = f"""
Draft one Analysis Point (A##) based on the specified relationship between information points. Use the provided summaries and assessments.

Relationship to Analyze: "{relationship_to_explore}"

Information Summaries & Assessments:
---
{q1_relevant_info_entries_text} # Contains I01, I03 summaries and human assessments
---

**Instructions & Rules for Drafting Analysis Point:**
1.  **Focus on Relationship:** Explain the relationship identified (e.g., how I03 provides nuance to I01).
2.  **Incorporate Assessment:** Briefly mention the source quality/bias noted in the assessments for the involved Info IDs (I01, I03) to contextualize the relationship (e.g., "While I01 suggests X, the more objective I03 indicates Y...").
3.  **Cite IDs:** *Must* cite the Info IDs (I01, I03) involved.
4.  **Label Output:** Start the output with the next available Analysis Point ID (e.g., A{a_id_counter}).
5.  **Keep it Simple:** Focus only on describing the finding based on the identified relationship. Do not make broad conclusions yet.
6.  **Acknowledge Limits:** If assessments indicate low quality data, mention that limitation.

**Draft Analysis Point [A{a_id_counter}]:**
"""
draft_A_point = llm_generate(prompt_3_draft_A_point_simple)
# --- CRITICAL HUMAN STEP ---
# Analyst *heavily reviews* draft_A_point. Checks logic, ensures quality assessments are considered correctly, verifies citations.
# Analyst likely needs to rewrite or significantly edit this draft to create a valid A## point.
# The human analyst remains responsible for the *actual synthesis and analytical judgment* to create the final A## points.
# Store the HUMAN-VALIDATED A## points in step3_report['Analysis for Q1'] etc.
# Update a_id_counter

# --- (After HUMAN has created all A## points for all Questions) ---

# Enhanced Prompt 3.3 (Refine Themes into Insights - Guided Brainstorming)
# Assume key_themes_draft = "* Well-being Improvement\n* Productivity Nuance\n* Implementation Challenges" # Output from simplified theme prompt

prompt_3_refine_insights_simple = f"""
Refine the following themes into potential Key Insights relevant to the research objective.

Identified Themes:
---
{key_themes_draft}
---
Research Objective: "{step1_doc['Research Objective/Purpose']}"

**Instructions & Rules for Refining Insights:**
1.  **Connect to Objective:** For each theme, rephrase it as a brief statement (1-2 sentences) that directly relates to the 'Research Objective'.
2.  **Focus on "So What?":** What is the implication or main takeaway of each theme for the objective?
3.  **Simple Language:** Keep the statements clear and concise.
4.  **Label as Potential:** Frame these as 'Potential Key Insights' as human judgment is needed for final selection.

**Potential Key Insights:**
* [LLM attempts to rephrase themes]
"""
potential_insights_draft = llm_generate(prompt_3_refine_insights_simple)
# --- CRITICAL HUMAN STEP ---
# Analyst reviews the potential insights, selects the most significant ones, refines wording,
# and ensures they accurately reflect the underlying A## points.
# The human writes the final 'Key Insights & Patterns' section in step3_report.

# --- Human still writes Limitations/Confidence/Assumptions for Step 3 ---
# This requires judgment based on the whole process, which the LLM lacks.
# step3_report['Limitations & Confidence (Preliminary)'] = "[HUMAN WRITES...]"
# step3_report['Analyst Assumptions (During Analysis & Synthesis)'] = "[HUMAN WRITES...]"
Enhanced Step 4 Prompts: Conclusion & Findings Summary

LLM Role: Draft sections based strictly on human-validated Step 3 inputs (Insights, Answers derived from human-validated A##).
Human Role: Final verification of all drafts; writing the final confidence assessment and limitations summary.
Python

# --- Use outputs stored in step3_report (containing human-validated insights & A##) ---
# --- And step4_summary (containing human-validated answers with C# assigned) ---

# (Prompts 4.1, 4.2, 4.3 remain largely the same as the previous 'enhanced' version,
# as they primarily rely on summarizing human-validated inputs from Step 3.
# Ensure inputs like step3_report['Key Insights & Patterns'] and step3_report['Analysis for QX']
# used in these prompts are the HUMAN-VALIDATED versions.)

# Example: Enhanced Prompt 4.2 (Draft Answers - Emphasizing reliance on human A##)
prompt_4_answer_q1_reemphasized = f"""
Draft a direct answer to the Research Question below, using *only* the provided supporting Analysis Points (A##), which have been validated by the analyst.

Research Question (Q1): "{step1_doc['Key Research Question(s)']['Q1']}"

Supporting Analysis Points (A##) from Step 3 for Q1 (Analyst Validated):
---
{step3_report['Analysis for Q1']} # Contains final A1, A2, A3...
---
**Instructions & Rules for Drafting Answer:**
1.  **Direct Answer:** Create 1-2 clear sentences answering Q1.
2.  **Based ONLY on Provided A##:** Base the answer strictly on the findings stated in the A## points. Do *not* infer or add external info.
3.  **Mandatory Citation:** *Must* cite the relevant Analysis Point ID(s) (A1, A2...) supporting the answer.
4.  **Reflect Nuance from A##:** If the A## points indicated nuance or conflict, briefly reflect this.
5.  **Simple Language:** Use clear language.

**Answer to Question [Q1]:**
"""
# q1_answer_draft = llm_generate(prompt_4_answer_q1_reemphasized)
# --- HUMAN REVIEWS/EDITS and assigns C# IDs ---

# --- Human Adds Final Limitations & Confidence ---
# Enhanced Prompt 4.4 (Brainstorm Factors for Limitations/Confidence - LLM Assist Only)
prompt_4_brainstorm_confidence_factors = f"""
Review the analysis process artifacts below. List factors that *might* influence the confidence in the final conclusions. Do *not* assign a confidence level.

Analysis Summary (Key Critiques / Answers):
---
{step4_summary['Summary of Key Findings']}
{step4_summary['Answer to Q1']}
{step4_summary['Answer to Q2']}
---
Source Assessment Notes Summary (Themes from Step 2 Human Inputs):
---
[Human provides a brief summary of common issues noted in Step 2 assessments, e.g., "Some key sources had potential bias (S01)", "Sample sizes small in some studies (S02)", "Reliance on self-reported data noted for I01, I02"]
---
Identified Information Gaps (From Step 3 Limitations):
---
[Human provides list of gaps noted in Step 3, e.g., "Lack of direct ROI data", "Limited data on long-term effects"]
---

**Instructions & Rules:**
1.  **List Factors:** Based *only* on the input text, list potential factors that could INCREASE confidence (e.g., consistency across multiple credible sources, strong data).
2.  **List Factors:** Also list potential factors that could DECREASE confidence (e.g., source bias, data gaps, contradictions, reliance on subjective data).
3.  **Do NOT Assess:** Do *not* assign an overall confidence level (High/Medium/Low). Just list the influencing factors.
4.  **Format:** Use bullet points for factors increasing confidence and factors decreasing confidence.

**Potential Factors Influencing Confidence:**
* Factors potentially increasing confidence:
    * [LLM lists points]
* Factors potentially decreasing confidence:
    * [LLM lists points]
"""
confidence_factors_list = llm_generate(prompt_4_brainstorm_confidence_factors)

# --- CRITICAL HUMAN STEP ---
# The human analyst reviews 'confidence_factors_list', considers the entire research process,
# and makes the *final judgment* on the overall confidence level and writes the definitive
# 'Limitations & Confidence' section for the Step 4 report, potentially using the LLM list as a checklist.
# step4_summary['Limitations & Confidence'] = "[HUMAN WRITES the final assessment, e.g., 'Confidence is Moderate because... citing specific factors like data gaps and source bias identified...']"

# --- (Optional) Enhanced Prompt 4.5 (Brainstorm Recommendations based on Limitations) ---
# Similar structure to 4.4, asking LLM to suggest actions based *only* on identified limitations or negative findings. Human selects/refines.
Summary of Changes for Smaller LLM:

Tasks like synthesis (creating A## points) and source assessment are shifted primarily to the human, with the LLM providing only preliminary analysis (like relationship identification) or basic checks (like keyword presence).
Prompts explicitly instruct the LLM to rely only on provided inputs and avoid interpretation or complex reasoning.
Output formats are simplified (often lists).
Human review and validation steps are marked as even more critical.
Confidence assessment remains a purely human judgment, though the LLM can help brainstorm influencing factors.
These adapted prompts for the SIRP framework, current as of Friday, April 18, 2025 at 7:18 PM EDT in Richmond, Virginia, reflect the need for more scaffolding and reduced complexity when working with less capable LLMs, ensuring the human analyst remains central to the critical thinking process.