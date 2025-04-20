Okay, let's adapt the Structured Position Critique Protocol (SPCP) prompts for a smaller LLM (like a hypothetical "Gemma 3 4B"), incorporating that higher level of detail in the instructions but simplifying the tasks and increasing reliance on human review and judgment.

Key Focus: Breaking down complex reasoning, using very explicit rules, simple output formats, and clearly marking mandatory human intervention points.

Citation Pattern Remains: POS-P#, POS-A#, POS-E#, CR-C#, CR-E##, CR-A## (implicitly), CR-R#

Enhanced & Simplified Step 1 Prompts (SPCP for Smaller LLM)

LLM Role: Minimal assist with summarizing/formatting human-defined content.
Human Role: Defines position, objective, scope; identifies key points (POS-P#).
Python

# --- HUMAN INPUTS (Define all Step 1 fields) ---
# critique_title, date_initiated, analyst_names, position_document_reference,
# critique_objective, in_scope_details, out_of_scope_details, constraints_assumptions
# Human reads the position document and provides the summary text input below.

# --- Enhanced Prompt 1.1 (Summarize Position & Identify Key Points - Simple) ---
baseline_summary_text_input = """
[Human pastes relevant summary/key sections from the Position Document Under Review.]
"""

prompt_1_summarize_position_simple = f"""
Read the Position Text below. Summarize its main point(s) and proposal(s).

Position Text:
---
{baseline_summary_text_input}
---

**Instructions & Rules for Summary:**
1.  **Identify Main Idea:** What is the core recommendation or conclusion?
2.  **Identify Key Supporting Points:** What are the main reasons or components mentioned in the text?
3.  **Label Points:** Label these key points starting with POS-P1, POS-P2...
4.  **Summarize Simply:** Write a brief summary including these POS-P# labels. Use simple sentences.
5.  **Be Objective:** Only use information from the text. Do not add opinions or critique.

**Draft Summary of Position Under Review (with POS-P# labels):**
"""
position_summary_draft = llm_generate(prompt_1_summarize_position_simple)
# --- CRITICAL HUMAN REVIEW: Analyst verifies summary accuracy and POS-P# assignment ---
# final_position_summary = reviewed draft

# --- Compile Step 1 Document Data (Human curates) ---
# step1_doc = { ... populated with human inputs and final_position_summary ... }
# step1_doc['Next Step Reference'] = "Review position within scope; identify assumptions, logic, evidence; flag points for scrutiny. Output: 'Assumption & Logic Review / Scrutiny Point Identification'."
Enhanced & Simplified Step 2 Prompts (SPCP for Smaller LLM)

LLM Role: Help scan text for potential assumptions/logic keywords; list cited evidence; brainstorm generic critique questions.
Human Role: Critically read position; identify specific POS-A#, POS-E#; map the actual logic; formulate specific CR-C# scrutiny points using LLM suggestions as a checklist.
Python

# --- Process each 'Area In Scope' from Step 1 ---
# Example: Reviewing Argument on Benefits (POS-P2) based on POS-E1 & POS-E2

# 1. Provide relevant text section
position_text_section_benefits = """
[Human pastes the relevant section from the Position Document.]
"""

# 2. Enhanced Prompt 2.1 (Scan for Assumptions & Generate Generic Checks - Simplified)
prompt_2_scan_assumptions_simple = f"""
Read the Text Section below. Help identify potential assumptions and suggest checks.

Text Section:
---
{position_text_section_benefits}
---

**Instructions & Rules:**
1.  **Find Assumption Keywords:** List phrases in the text that *might* indicate an assumption (e.g., "based on," "assuming," "likely," "therefore suggests," "we believe").
2.  **Suggest Generic Checks for Assumptions:** List these standard questions an analyst should ask about *any* potential assumption:
    * Is this assumption explicitly stated or hidden (unstated)?
    * Is there direct evidence provided *for this specific assumption* in the text?
    * Could this assumption be wrong? What might make it wrong?
    * How important is this assumption to the main conclusion?
3.  **Output Format:** List found keywords/phrases first, then list the generic check questions.

**Potential Assumption Indicators & Standard Checks:**
"""
assumption_scan_output = llm_generate(prompt_2_scan_assumptions_simple)
# --- CRITICAL HUMAN STEP: Use the output as a guide ONLY ---
# Analyst reads the text section carefully. Uses the keyword list and generic checks
# to identify the *actual* specific assumptions (POS-A1, POS-A2...)
# and formulate *specific* scrutiny points (CR-C1, CR-C2...) explaining the potential issue.
# Example Human Output:
# POS-A1: Low workshop participation reflects low overall program value (Unstated).
# CR-C1: Scrutinize POS-A1 - Fails check 'Is assumption supported by evidence?' Ignores other program parts.
# POS-A2: Lack of direct ROI metric = lack of significant benefit (Unstated).
# CR-C2: Scrutinize POS-A2 - Fails check 'Are there alternatives?'. Ignores non-ROI value types.

# 3. Enhanced Prompt 2.2 (Scan Logic/Evidence & Generate Generic Checks - Simplified)
prompt_2_scan_logic_evidence_simple = f"""
Read the Text Section below. Help identify logic steps, cited evidence, and suggest checks.

Text Section:
---
{position_text_section_benefits} # Same text
---

**Instructions & Rules:**
1.  **List Connective Phrases:** Identify words or phrases showing connection between ideas (e.g., "therefore," "because," "based on," "leads to," "proves that").
2.  **List Cited Evidence:** List specific data points, reports, or sources mentioned *in this text section* as support. Assign temporary labels like [Evidence A], [Evidence B].
3.  **Suggest Generic Checks for Logic:** List standard critical questions for logic:
    * Is the connection between points clear?
    * Could there be other causes or factors? (Correlation vs. Causation)
    * Is the conclusion too strong for the evidence? (Hasty Generalization)
    * Are there any gaps in the reasoning?
4.  **Suggest Generic Checks for Evidence:** List standard critical questions for evidence:
    * Is the source described? Is it likely credible?
    * Is the evidence directly relevant to the point it supports?
    * Is the evidence timely/up-to-date?
    * Could the evidence be interpreted differently?
    * Is any expected evidence missing?
5.  **Output Format:** List Connective Phrases, then Cited Evidence, then Generic Logic Checks, then Generic Evidence Checks.

**Logic/Evidence Scan & Standard Checks:**
"""
logic_evidence_scan_output = llm_generate(prompt_2_scan_logic_evidence_simple)
# --- CRITICAL HUMAN STEP: Use the output as a guide ONLY ---
# Analyst maps the actual logic flow. Identifies specific evidence cited (POS-E1, POS-E2...).
# Uses the generic checks to formulate *specific* scrutiny points (CR-C3, CR-C4, CR-C5, CR-C6...)
# related to the actual logic and evidence identified.
# Example Human Output:
# Logic: POS-E1 + POS-E2 -> POS-P2 -> POS-P1
# POS-E1: Workshop attendance data (Source: Training System)
# POS-E2: Lack of ROI report (Source: Absence of report)
# CR-C3: Scrutinize Logic - Fails check 'Is conclusion too strong?'. Infers lack of *all* value (POS-P2) from lack of *one* metric (POS-E2).
# CR-C4: Scrutinize Evidence POS-E1 - Fails checks 'Is context provided?' and 'Other interpretations?'. Needs benchmarks/reasons.
# CR-C5: Scrutinize Evidence POS-E2 - Fails check 'Is absence evidence sufficient?'. Argument from absence.

# --- Compile Step 2 Document Data (Human curates final POS-A#, POS-E#, CR-C#) ---
# step2_doc = { ... populated with human-derived findings ... }
# step2_doc['Next Step Reference'] = "Formulate structured critiques for Scrutiny Points (CR-C#...) and find supporting evidence. Output: 'Critique Formulation & Substantiation'."
Enhanced & Simplified Step 3 Prompts (SPCP for Smaller LLM)

LLM Role: Help rephrase scrutiny points into critique statements; brainstorm types of counter-evidence needed; summarize gathered counter-evidence (CR-E##); perform simple matching of evidence to critique.
Human Role: Formulate the final critique argument; guide the search for challenging evidence (CR-E##); critically evaluate the quality and relevance of CR-E##; write the substantiated critique assessing strength.
Python

# --- Process each selected Scrutiny Point (CR-C#) from Step 2 ---
# Example: Developing critique for CR-C1 (Challenge POS-A1 validity)

scrutiny_point_id = 'CR-C1'
scrutiny_point_text = "Scrutinize POS-A1 validity - Assumption lacks direct evidence and ignores other program components."

# 1. Enhanced Prompt 3.1 (Rephrase Scrutiny & Brainstorm Evidence Needs - Simple)
prompt_3_rephrase_critique_simple = f"""
Rephrase the Scrutiny Point below into a simple statement of critique. Then, list *types* of evidence that could support this critique.

Scrutiny Point: ({scrutiny_point_id}) {scrutiny_point_text}

**Instructions & Rules:**
1.  **Rephrase as Critique:** Turn the scrutiny point into a direct statement challenging the original position (e.g., "The position wrongly assumes...").
2.  **Brainstorm Evidence Types:** Based on the critique statement, list general categories or specific examples of data/information that would help *prove* the critique is valid. Think: What would show the original assumption/logic is flawed?
3.  **Output Format:** Provide 'Draft Critique Statement' then 'Potential Supporting Evidence Types'.

**Draft Critique Statement & Evidence Needs for {scrutiny_point_id}:**
"""
critique_rephrase_draft = llm_generate(prompt_3_rephrase_critique_simple)
# --- HUMAN REVIEWS/EDITS, finalizes critique statement and evidence search plan ---
# final_critique_statement = "The position's assumption (POS-A1) that workshop attendance represents overall program value is likely flawed because it ignores other key components."
# evidence_needs_list = ["Data on usage of program app/website", "Data on EAP referrals via program", "Benchmarks for component usage"]

# 2. Gather Supporting Critique Evidence (CR-E##) (Human uses needs list to guide RAG/Search)
# Human finds CR-E01 (app data), CR-E02 (EAP data), CR-E06 (benchmark data).
# Human logs these CR-E## with source details and quality assessment.

# 3. Enhanced Prompt 3.2a (Summarize Critique Evidence - Simple)
critique_evidence_log_entries = """
- CR-E01: Project Flourish web analytics (Jan-Dec 2024) show ~45% employee access to online resources quarterly. (Source: Internal Analytics Dashboard. Quality: High reliability system data).
- CR-E02: EAP provider aggregate data indicates 15% utilization rate of counseling referred via Flourish portal in 2024. (Source: EAP Q4 Report. Quality: Reliable provider data, aggregated/anonymized).
- CR-E06: Industry benchmark data suggests participation rates of 5-15% for optional wellness workshops are common. (Source: WELCOA summaries. Quality: Reputable source, general benchmark).
""" # Human provides logged CR-E## details relevant to CR-C1

prompt_3_summarize_cre_simple = f"""
Briefly summarize the main point of each piece of Critique Evidence listed below.

Critique Evidence Log Entries (CR-E##):
---
{critique_evidence_log_entries}
---

**Instructions & Rules:**
1.  **Summarize Each:** For each CR-E## entry, write one sentence stating its core finding.
2.  **Include ID:** Start each summary with its ID (e.g., "CR-E01 Summary: ...").

**Critique Evidence Summaries:**
"""
critique_evidence_summaries = llm_generate(prompt_3_summarize_cre_simple)

# 4. Enhanced Prompt 3.2b (Simple Linking of Evidence to Critique)
prompt_3_link_evidence_simple = f"""
Does the evidence summarized below support the Draft Critique Statement? Answer Yes/No/Partially for each piece of evidence.

Draft Critique Statement for {scrutiny_point_id}: "{final_critique_statement}"

Critique Evidence Summaries:
---
{critique_evidence_summaries}
---
Evidence Quality Notes (Human Provided Summary):
CR-E01: High reliability. CR-E02: Reliable. CR-E06: Reputable benchmark, general.
---

**Instructions & Rules:**
1.  **Compare:** Read the critique statement and each evidence summary.
2.  **Assess Support:** Does the evidence summary seem to directly support the critique statement?
3.  **Output Format:** List each Evidence ID (CR-E##) and state Yes, No, or Partially.

**Evidence Support Assessment:**
* CR-E01 supports critique: [Yes/No/Partially]
* CR-E02 supports critique: [Yes/No/Partially]
* CR-E06 supports critique: [Yes/No/Partially]
"""
evidence_support_assessment = llm_generate(prompt_3_link_evidence_simple)

# --- CRITICAL HUMAN STEP: Write Substantiated Critique & Assess Strength ---
# The human analyst takes the final_critique_statement, the original CR-E## entries (with full context and quality assessment),
# the LLM's summaries (if helpful), and the LLM's simple support assessment (if helpful).
# The human then *writes* the well-reasoned, substantiated critique, weaving in the CR-E## evidence correctly,
# considering evidence quality, and making the argument. The human also assigns the final Strength Assessment.
# Example Human Output:
# Substantiated Critique for CR-C1: The position's assumption (POS-A1)... is flawed. Reliable internal data shows significant engagement with online resources (~45% access - CR-E01) and EAP referrals (15% utilization - CR-E02), demonstrating value beyond workshops. Relying solely on workshop data (POS-E1) provides an incomplete picture. Strength Assessment: High (Based on direct internal usage data CR-E01, CR-E02).
# Store this human-written section in step3_doc['Critique Development Sections']

# --- Repeat for other CR-C# points ---

# --- Compile Step 3 Document Data ---
# step3_doc = { ... populated with final human-written substantiated critiques ... }
# step3_doc['Next Step Reference'] = "Consolidate critiques and assess overall impact. Output: 'Critical Analysis Report & Impact Assessment'."
Enhanced & Simplified Step 4 Prompts (SPCP for Smaller LLM)

LLM Role: Draft simple summaries and lists based strictly on human-validated Step 3 inputs. Cannot reliably assess impact severity.
Human Role: Final verification of summaries; determining overall impact assessment; writing final recommendations.
Python

# --- Use outputs stored in step3_doc (containing human-written critiques & strength) and step1_doc ---

# 1. Enhanced Prompt 4.1 (Draft Executive Summary - Simple List of Issues)
# Human provides summary of HIGH/MEDIUM strength critiques identified in Step 3.
strongest_critiques_summary = "[Human lists the main points of the strongest critiques, e.g., Flawed value proxy (CR-C1, High Strength), Dismissal of non-ROI benefits (CR-C3/C5, Med-High Strength)]"

prompt_4_exec_summary_simple = f"""
List the main issues identified in the critique summary below.

Summary of Strongest Critiques:
---
{strongest_critiques_summary}
---
**Instructions & Rules:**
1.  **List Issues:** Use bullet points to list the core problems identified in the input summary.
2.  **Simple Terms:** Use clear, simple language.
3.  **Do Not Elaborate:** Just list the issues mentioned.

**Draft List of Key Issues Identified:**
* [LLM generates list]
"""
exec_summary_draft_list = llm_generate(prompt_4_exec_summary_simple)
# --- HUMAN REVIEWS list and writes the actual narrative Executive Summary ---
# step4_doc = {'Executive Summary of Critique': "[Human writes based on the list and Step 3]"}

# 2. Enhanced Prompt 4.2 (Draft Summary of Key Critiques - Simple Extraction)
# Human provides the final substantiated critique sections from Step 3
full_critique_sections_input = "[Human pastes final substantiated critique sections for CR-C1, CR-C3/C5, etc.]"

prompt_4_summarize_critiques_simple = f"""
For each critique section below, extract the Critique ID (CR-C#), the main critique statement, and the key supporting Evidence IDs (CR-E##) cited.

Detailed Substantiated Critiques:
---
{full_critique_sections_input}
---
**Instructions & Rules:**
1.  **Extract Key Info:** For each critique described, pull out:
    * Its CR-C# label.
    * A brief summary (1 sentence) of the critique's main point.
    * The CR-E## labels cited as key support within that section.
2.  **List Format:** Present as a list, e.g., "CR-C1: [Critique Summary], supported by [CR-E01, CR-E02]".

**Draft Summary List of Key Critiques & Evidence:**
"""
key_critiques_summary_list = llm_generate(prompt_4_summarize_critiques_simple)
# --- HUMAN REVIEWS/EDITS list for accuracy and writes narrative section ---
# step4_doc['Summary of Key Critique Points & Substantiation'] = "[Human writes narrative summary based on the list]"

# 3. Enhanced Prompt 4.3 (Brainstorm *Potential* Impacts - Simple)
prompt_4_potential_impacts_simple = f"""
For each critique listed below, suggest potential negative impacts it might have on the original position's conclusion or plan, if the critique is valid.

Key Critiques Summary List:
---
{key_critiques_summary_list} # Use reviewed list from previous prompt
---
Original Position Summary (from Step 1): {step1_doc['Summary of Position Under Review']}

**Instructions & Rules:**
1.  **Consider Each Critique:** For each CR-C# listed, think about how it might weaken the original position (POS-P#, POS-A#).
2.  **List Potential Impacts:** State potential impacts clearly (e.g., "CR-C1 might mean the program's value (related to POS-P2) is underestimated," "CR-C3 might mean the cost savings from cutting the program (POS-P1) are less beneficial than stated if retention suffers").
3.  **Do Not Judge Severity:** Just list *potential* consequences.

**Potential Impacts of Critiques on Original Position:**
* Impact related to CR-C1: [LLM suggests impact]
* Impact related to CR-C#: [LLM suggests impact]
* ...
"""
potential_impacts_list = llm_generate(prompt_4_potential_impacts_simple)
# --- CRITICAL HUMAN STEP: Assess Overall Impact ---
# Human reviews the potential impacts list, considers the strength ratings from Step 3,
# and makes the definitive judgment on the overall impact severity, writing the
# 'Assessment of Overall Impact' section and assigning CR-R# labels.
# step4_doc['Assessment of Overall Impact on Position Under Review'] = "[HUMAN WRITES final assessment, e.g., CR-R1: High risk recommendation POS-P1 is based on flawed analysis...]"

# 4. Enhanced Prompt 4.4 (Brainstorm Recommendation *Types* - Simple)
prompt_4_recommendation_types_simple = f"""
Based on the types of critiques listed below, suggest general *types* of actions or recommendations that might address them.

Key Critiques Summary List:
---
{key_critiques_summary_list} # Use reviewed list
---

**Instructions & Rules:**
1.  **Match Action to Critique Type:** For common critique types (e.g., flawed assumption, misinterpreted evidence, missing data, overlooked risk), suggest a generic corrective action type.
2.  **Generic Examples:**
    * If assumption questioned -> Suggest: "Gather data to test assumption" or "Re-evaluate using alternative assumption".
    * If evidence misinterpreted -> Suggest: "Re-analyze evidence" or "Seek expert interpretation".
    * If data missing -> Suggest: "Gather the missing data".
    * If risk overlooked -> Suggest: "Assess the overlooked risk".
3.  **List Format:** List pairs of (Critique Type Example -> Generic Recommendation Type).

**Generic Recommendation Types based on Critique Types:**
* [LLM lists pairs]
"""
recommendation_types_list = llm_generate(prompt_4_recommendation_types_simple)
# --- CRITICAL HUMAN STEP: Formulate Specific Recommendations ---
# Human reviews the generic suggestions, considers the specific context of the critique (CR-C#)
# and impact assessment (CR-R1, R2...), and writes specific, actionable recommendations (CR-R3, R4...),
# possibly using the LLM suggestions as a checklist.
# step4_doc['Recommendations for Consideration'] = "[HUMAN WRITES specific, actionable CR-R# recommendations]"

# 5. Human Adds Final Limitations, References etc.
# ...
These highly detailed yet simplified SPCP prompts, current as of Friday, April 18, 2025 at 7:20 PM EDT in Richmond, Virginia, are designed for use with smaller LLMs. They break complex critical tasks into manageable sub-steps, use very explicit instructions, and rely heavily on the human analyst for the core judgment, synthesis, evidence evaluation, and final formulation of critiques and recommendations, while using the LLM primarily for structured brainstorming, simple comparisons, and formatting assistance.