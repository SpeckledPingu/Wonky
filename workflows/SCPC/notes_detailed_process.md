Okay, absolutely. Let's apply that same enhanced level of detail to the prompts for the Structured Position Critique Protocol (SPCP). This version will provide highly explicit, rule-based instructions for the LLM, guiding it through the process of systematically critiquing a position while ensuring clarity and traceability.

Citation Pattern Used:

POS-P#: Position Point/Claim/Plan Element ID
POS-A#: Position's Assumption ID
POS-E#: Position's Supporting Evidence ID
CR-C#: Critique Point/Challenge ID
CR-E##: Critique's Supporting Evidence ID
CR-A##: Critique Analysis Point ID (Implicit in Step 3, referenced in Step 4)
CR-R#: Critique Recommendation/Impact Point ID
Enhanced Step 1 Prompts: Position Definition & Critique Scope

LLM Role: Assist in objectively summarizing the position under review, identifying key points (POS-P#).
Human Role: Define the position document, critique objective, and scope; review/finalize LLM summary.
Python

# --- HUMAN INPUTS (as before) ---
critique_title = 'Critical Analysis: "Program X Review Report" Recommendation to Eliminate Project Flourish'
date_initiated = '2025-04-18' # Use current date
analyst_names = 'Analyst C'
position_document_reference = '"Internal Audit Report: Program X Review - Project Flourish Assessment", V1.0, Dated 2025-04-10'
critique_objective = "To rigorously assess the validity of the recommendation (POS-P1) and the supporting argument (POS-P2) presented in the 'Program X Review Report', focusing on the interpretation of evidence, underlying assumptions, and consideration of potential alternative evidence or benefits."
# ... (Define scope, constraints, assumptions as Python variables/structures) ...

# --- Enhanced Prompt 1.1 (Summarize Position & Identify Key Points) ---
baseline_summary_text_input = """
[Human pastes the relevant summary section or key points from the 'Program X Review Report' document here. Example:
The report recommends eliminating Project Flourish for cost savings. It argues benefits are intangible/unproven, citing low workshop participation (Sec 3.1) and lack of a formal ROI analysis (Sec 4.2).]
"""

prompt_1_summarize_position_enhanced = f"""
Review the provided text summarizing the 'Position Under Review'.

Position Text:
---
{baseline_summary_text_input}
---

**Instructions & Rules for Summary and Point Identification:**
1.  **Objective Summary:** Draft a concise, neutral summary of the core position, argument, or proposal described in the text.
2.  **Identify Key Elements:** Extract the main claims, recommendations, or conclusions presented. Label these sequentially starting with **POS-P1**.
3.  **Reference Evidence Mentioned:** If the summary text mentions specific evidence supporting these points, note that briefly alongside the POS-P# label (we will analyze the evidence itself in Step 2).
4.  **Accuracy & Neutrality:** Ensure the summary accurately reflects the source text *without* introducing critique or external information.
5.  **Format:** Present the summary clearly, incorporating the POS-P# labels inline or as annotations.

**Draft Summary of Position Under Review (with POS-P# labels):**
"""
position_summary_draft = llm_generate(prompt_1_summarize_position_enhanced)
# --- HUMAN REVIEWS/EDITS position_summary_draft, confirms POS-P# labels ---
# final_position_summary = reviewed draft with POS-P#

# --- Compile Step 1 Document Data (Human curates the outputs) ---
# step1_doc = { ... populated with human inputs and final_position_summary ... }
# step1_doc['Next Step Reference'] = "Systematically review the 'Position Under Review' within scope, identifying assumptions, logic, evidence, and points for scrutiny. Output: 'Assumption & Logic Review / Scrutiny Point Identification'."
Enhanced Step 2 Prompts: Assumption & Logic Review / Scrutiny Point Identification

LLM Role: Help identify stated/unstated assumptions (POS-A#), map logic, list cited evidence (POS-E#), and crucially, brainstorm specific points for scrutiny (CR-C#) based on analytical checks.
Human Role: Guide analysis by providing text sections, review/validate LLM outputs, select and refine the final CR-C# points that warrant further investigation in Step 3.
Python

# --- Process each 'Area In Scope' from Step 1 ---
# Example: Reviewing Argument on Benefits (POS-P2) based on Evidence POS-E1 & POS-E2

# 1. Provide relevant text section from the Position Document
position_text_section_benefits = """
[Human pastes the relevant section from the 'Program X Review Report' arguing benefits are unproven (POS-P2) based on low workshop participation (POS-E1) and lack of ROI (POS-E2).]
"""

# 2. Enhanced Prompt 2.1 (Identify Assumptions & Brainstorm Scrutiny Points - More Detailed Rules)
prompt_2_identify_assumptions_enhanced = f"""
Analyze the provided text section to identify underlying assumptions and brainstorm points for critical scrutiny.

Text Section:
---
{position_text_section_benefits}
---

**Instructions & Rules for Assumption Identification & Scrutiny:**
1.  **Identify Assumptions (POS-A#):**
    * List all significant assumptions necessary for the argument in the text to be valid. Label sequentially POS-A{next_pos_a_id}.
    * **Rule:** Include both explicitly stated assumptions and *unstated* (implicit/inferred) ones. To find unstated assumptions, ask: "What must be true for this claim/conclusion to follow from the premise/evidence?"
    * Indicate if each assumption is Stated or Unstated.
2.  **Brainstorm Scrutiny Points (CR-C#):**
    * For *each* identified assumption (POS-A#), generate specific points suggesting *why* it needs scrutiny (label sequentially CR-C{next_cr_c_id}). Frame as critical questions or statements of potential weakness.
    * **Rule:** Apply critical thinking checks:
        * *Support:* Is the assumption backed by any evidence *within this text section* or elsewhere in the (assumed) full document? Note lack of support.
        * *Plausibility:* Is the assumption reasonable on its face? Could it be overly optimistic/pessimistic?
        * *Alternatives:* Are there plausible alternative assumptions that would lead to a different conclusion?
        * *Impact:* How critical is this assumption? What happens to the argument if it's false?
    * **Rule:** Phrase scrutiny points clearly (e.g., "CR-C1: Scrutinize POS-A1 validity - Assumption lacks direct evidence and ignores other program components.").
3.  **Output Format:** List each Assumption (POS-A#) followed immediately by the brainstormed Scrutiny Point(s) (CR-C#) related to it.

**Identified Assumptions & Potential Scrutiny Points:**
"""
assumptions_and_scrutiny_draft = llm_generate(prompt_2_identify_assumptions_enhanced)
# --- HUMAN REVIEWS/EDITS, selects/refines final POS-A# and CR-C# ---
# final_assumptions_and_critiques = reviewed output... update next_pos_a_id, next_cr_c_id

# 3. Enhanced Prompt 2.2 (Identify Logic/Evidence & Brainstorm Scrutiny Points - More Detailed Rules)
prompt_2_identify_logic_evidence_enhanced = f"""
Analyze the provided text section focusing on its logical structure and the evidence used.

Text Section:
---
{position_text_section_benefits} # Same text as before
---

**Instructions & Rules for Logic/Evidence Identification & Scrutiny:**
1.  **Outline Logic:** Break down the argument into its key logical steps (Premise -> Inference -> Conclusion). How does the text connect the evidence to the conclusion?
2.  **Identify Cited Evidence (POS-E#):**
    * List specific evidence cited *in this text section*. Label sequentially POS-E{next_pos_e_id}.
    * Include a brief description and the source *as cited in the text*.
3.  **Brainstorm Scrutiny Points - Logic (CR-C#):**
    * Based on the outlined logic, identify potential weaknesses (label sequentially CR-C{next_cr_c_id}).
    * **Rule:** Check for:
        * *Fallacies:* Any common logical errors (e.g., hasty generalization, false dichotomy, correlation/causation confusion)?
        * *Gaps:* Are there missing steps or unsupported leaps in reasoning?
        * *Sufficiency:* Does the evidence logically *justify* the strength or scope of the conclusion drawn?
        * *Clarity:* Is the reasoning ambiguous or potentially misleading?
    * **Rule:** Phrase scrutiny points clearly (e.g., "CR-C3: Scrutinize logical leap - Argument infers absence of *all* value from absence of *one* specific metric (ROI).").
4.  **Brainstorm Scrutiny Points - Evidence (CR-C#):**
    * For *each* piece of cited evidence (POS-E#), identify points for scrutiny (label sequentially CR-C{next_cr_c_id}).
    * **Rule:** Apply these checks based *only on the information presented*:
        * *Relevance:* How directly does POS-E# support the specific claim being made? Is it tangential?
        * *Interpretation:* Does the text interpret POS-E# reasonably, or are there plausible alternative interpretations ignored?
        * *Context:* Is sufficient context provided for POS-E# (e.g., for participation data POS-E1, is base size, frequency, comparison points provided)? Note missing context.
        * *Sufficiency:* Is this piece of evidence, even if valid, *enough* to support the claim?
        * *Potential Omissions:* Does the reliance on POS-E# seem to ignore other readily available or expected types of evidence (potential critique point)?
    * **Rule:** Phrase scrutiny points clearly (e.g., "CR-C4: Scrutinize POS-E1 interpretation - Data lacks context (benchmarks, reasons for low participation) making its link to 'low value' weak.").
5.  **Output Format:** Present findings clearly: Outline Logic, then list Evidence (POS-E#), then list brainstormed Scrutiny Points (CR-C#) related to Logic and Evidence.

**Identified Logic, Evidence, & Potential Scrutiny Points:**
"""
logic_evidence_and_scrutiny_draft = llm_generate(prompt_2_identify_logic_evidence_enhanced)
# --- HUMAN REVIEWS/EDITS, selects/refines final POS-E# and CR-C# ---
# final_logic_evidence_critiques = reviewed output... update next_pos_e_id, next_cr_c_id

# --- Compile Step 2 Document Data (Human curates the refined outputs) ---
# step2_doc = { ... populated with curated findings, clearly listing final CR-C# points ... }
# step2_doc['Next Step Reference'] = "Formulate structured critiques based on Scrutiny Points (CR-C#...) and gather supporting evidence. Output: 'Critique Formulation & Substantiation'."
Enhanced Step 3 Prompts: Critique Formulation & Substantiation

LLM Role: Help structure critique arguments; use RAG to find contradictory or alternative evidence (CR-E##); summarize found evidence.
Human Role: Define critique angle; guide RAG search for challenging information; evaluate CR-E## quality; write final substantiated critique; assess strength.
Python

# --- Process each selected Scrutiny Point (CR-C#) from Step 2 ---
# Example: Developing critique for CR-C1 (Challenge POS-A1 validity)

scrutiny_point_id = 'CR-C1'
scrutiny_point_text = "Scrutinize POS-A1 validity - Assumption lacks direct evidence and ignores other program components."
position_assumption_text = "POS-A1: Low workshop participation accurately reflects low overall program value/engagement."

# 1. Enhanced Prompt 3.1 (Structure Critique Argument & ID Evidence Needs - More Detail)
prompt_3_structure_critique_enhanced = f"""
Based on the Scrutiny Point below, formulate a structured critical argument against the associated Position Assumption. Also, identify specific evidence needed to support this critique.

Scrutiny Point: ({scrutiny_point_id}) {scrutiny_point_text}
Relevant Assumption from Position Being Challenged: {position_assumption_text}

**Instructions & Rules for Formulating Critique & Identifying Evidence Needs:**
1.  **Formulate Critique:** State the core argument *challenging* the assumption (POS-A1). Explain *why* it's likely flawed based on the scrutiny point (e.g., logical error like hasty generalization, ignoring components).
2.  **Structure Argument:** Briefly outline the logical steps of the critique (e.g., "Premise 1: Program X has multiple components beyond workshops. Premise 2: Workshop participation doesn't measure engagement with other components. Conclusion: Therefore, using workshop data alone (POS-E1) to judge overall program value (POS-A1) is logically flawed/insufficient.").
3.  **Identify Evidence Needs for Substantiation:** Specify precisely what kind of external or alternative internal evidence would be needed to *prove* the critique's premises or *disprove* the original assumption (POS-A1). Frame these as specific search goals. (e.g., "Need data on usage rates for Project Flourish app/website," "Need data on EAP referrals originating from Project Flourish," "Need benchmarks for participation in different components of corporate wellness programs").

**Draft Formulated Critique & Evidence Needs for {scrutiny_point_id}:**
"""
critique_formulation_draft = llm_generate(prompt_3_structure_critique_enhanced)
# --- HUMAN REVIEWS/EDITS critique_formulation_draft and confirms evidence needs ---
# final_formulated_critique = reviewed draft
# evidence_needs_list = list of specific needs identified

# 2. Gather Supporting Critique Evidence (CR-E##) (Human uses needs list to guide RAG/Search)
# Example: Human searches for "usage data Project Flourish app", "EAP referral data Project Flourish"
# RAG or manual search finds CR-E01 (app data), CR-E02 (EAP data).
# Human logs these CR-E## with source details and quality assessment (similar to Step 2 log process but for *critique* evidence).

# 3. Enhanced Prompt 3.2 (Draft Substantiated Critique Section - More Detail)
formulated_critique_text = final_formulated_critique # Reviewed output from Prompt 3.1
critique_evidence_text = """
- CR-E01: Project Flourish web analytics (Jan-Dec 2024) show ~45% employee access to online resources quarterly. (Source: Internal Analytics Dashboard. Quality: High reliability system data).
- CR-E02: EAP provider aggregate data indicates 15% utilization rate of counseling referred via Flourish portal in 2024. (Source: EAP Q4 Report. Quality: Reliable provider data, aggregated/anonymized).
""" # Human provides logged CR-E## details relevant to CR-C1

prompt_3_substantiate_enhanced = f"""
Combine the Formulated Critique with its Supporting Evidence (CR-E##) below into a single, substantiated critical argument.

Formulated Critique for {scrutiny_point_id}:
---
{formulated_critique_text}
---
Supporting Evidence Gathered for Critique (CR-E## with Quality Assessment):
---
{critique_evidence_text}
---

**Instructions & Rules for Substantiation:**
1.  **Integrate & Argue:** Weave the 'Supporting Evidence' (CR-E##) into the 'Formulated Critique' to construct a persuasive argument demonstrating the flaw in the original position's assumption/logic. Explicitly state *how* CR-E01, CR-E02 contradict or weaken POS-A1.
2.  **Mandatory Citation:** *Must* cite the specific Critique Evidence ID(s) (CR-E01, CR-E02...) directly within the text where they support the critique's claims.
3.  **Leverage Quality Assessment:** Mention the assessed quality of CR-E## where it strengthens the critique (e.g., "Reliable internal data (CR-E01) shows...").
4.  **Logical Flow:** Ensure the final text presents a clear, logical argument from the critique's premises (supported by CR-E##) to its conclusion (challenging the original position).
5.  **Assess & Justify Strength:** Conclude with an explicit assessment ('High', 'Medium', 'Low') of this substantiated critique's overall strength. **Rule:** Justify this strength rating based *specifically* on the quality, relevance, and directness of the supporting evidence (CR-E##) presented.

**Draft Substantiated Critique Section for {scrutiny_point_id} (including Strength Assessment):**
"""
substantiated_critique_draft = llm_generate(prompt_3_substantiate_enhanced)
# --- HUMAN REVIEWS/EDITS substantiated_critique_draft, ensuring logical argument and accurate strength assessment ---
# final_substantiated_critique_section = reviewed output

# --- Repeat process for other selected CR-C# points ---

# --- Compile Step 3 Document Data ---
# step3_doc = { ... populated with final substantiated critique sections ... }
# step3_doc['Next Step Reference'] = "Consolidate critiques and assess overall impact. Output: 'Critical Analysis Report & Impact Assessment'."
Enhanced Step 4 Prompts: Critical Analysis Report & Impact Assessment

LLM Role: Draft summaries, initial impact assessment, and potential recommendations based strictly on the substantiated critiques from Step 3.
Human Role: Final verification, determining overall impact severity and confidence, finalizing recommendations.
Python

# --- Use outputs stored in step3_doc and step1_doc ---

# 1. Enhanced Prompt 4.1 (Draft Executive Summary - More Detail)
# Human provides summary of critiques assessed as High/Medium strength in Step 3
strongest_critiques_summary = "[Human summarizes the critiques with High/Medium strength, e.g., 'Critique CR-C1 (High Strength) shows reliance on workshop data is flawed due to significant other resource usage (CR-E01, CR-E02). Critique CR-C3/C5 (Medium-High Strength) highlights dismissal of non-ROI benefits lacks justification and contradicts available data (CR-E03, CR-E04)...']"

prompt_4_exec_summary_enhanced = f"""
Draft an Executive Summary for the Critical Analysis Report based *only* on the provided summary of the strongest critiques.

Summary/Highlights of Strongest Critiques:
---
{strongest_critiques_summary}
---

**Instructions & Rules for Drafting Executive Summary:**
1.  **Focus on Strongest Critiques:** Summarize *only* the most significant issues identified (those highlighted in the input).
2.  **State Key Flaw(s):** Clearly articulate the core weakness(es) found in the original Position Under Review (e.g., "relies on flawed assumptions," "interprets evidence narrowly," "ignores key data").
3.  **Hint at Impact:** Briefly indicate the implication of these flaws (e.g., "casting doubt on the conclusion," "suggesting the recommendation is premature/unsupported").
4.  **Conciseness & Neutrality:** Be brief (3-5 sentences) and maintain an objective tone.

**Draft Executive Summary of Critique:**
"""
exec_summary_draft = llm_generate(prompt_4_exec_summary_enhanced)
# --- HUMAN REVIEWS/EDITS ---
# step4_doc = {'Executive Summary of Critique': reviewed_exec_summary}

# 2. Enhanced Prompt 4.2 (Draft Summary of Key Critiques - More Detail)
full_critique_sections_input = "\n\n".join([str(section) for section in step3_doc['Critique Development Sections']])

prompt_4_summarize_critiques_enhanced = f"""
Draft a summary of the key critique points based on the detailed substantiated critiques provided below.

Detailed Substantiated Critiques (including CR-C#, CR-E## citations, and Strength Assessment):
---
{full_critique_sections_input}
---

**Instructions & Rules for Summarizing Critiques:**
1.  **Focus on Key Issues:** Summarize the *main argument* of each significant critique (especially those rated Medium or High strength in the input). Reference the Critique ID (CR-C#).
2.  **Mention Core Evidence:** Briefly state the *type* or *source* of the key supporting evidence (referencing CR-E##) used to substantiate that critique point.
3.  **Reflect Assessed Strength:** Optionally, briefly mention the assessed strength where it adds context (e.g., "A high-strength critique (CR-C1)...").
4.  **Logical Grouping:** Organize related critiques thematically if helpful (e.g., critiques about assumptions, critiques about evidence).
5.  **Clarity:** Ensure the summary accurately reflects the core challenges raised in Step 3.

**Draft Summary of Key Critique Points & Substantiation:**
"""
key_critiques_summary_draft = llm_generate(prompt_4_summarize_critiques_enhanced)
# --- HUMAN REVIEWS/EDITS ---
# step4_doc['Summary of Key Critique Points & Substantiation'] = reviewed_key_critiques_summary

# 3. Enhanced Prompt 4.3 (Draft Impact Assessment - More Detail)
prompt_4_impact_assessment_enhanced = f"""
Draft an assessment of the overall impact of the critiques on the original 'Position Under Review', based *only* on the provided summary.

Summary of Key Critique Points:
---
{step4_doc['Summary of Key Critique Points & Substantiation']} # Use reviewed version
---
Original Position Being Reviewed (Summary from Step 1): {step1_doc['Summary of Position Under Review']}

**Instructions & Rules for Drafting Impact Assessment:**
1.  **Assess Collective Impact:** Evaluate how the *combination* of key critiques affects the core elements (POS-P#, POS-A#) of the original Position Under Review.
2.  **Judge Severity & Justify:** Make a judgment on the overall impact severity (e.g., "Critiques fundamentally undermine POS-P2," "Critiques suggest POS-P1 requires significant reassessment," "Critiques highlight risks but don't invalidate the core proposal"). **Rule:** *Must* justify this judgment by explicitly linking *how* the summarized critiques challenge specific assumptions (POS-A#) or conclusions (POS-P#) of the original position. Label key impact points CR-R1, CR-R2...
3.  **Clarity:** State the assessed impact clearly.

**Draft Assessment of Overall Impact on Position Under Review (with CR-R# labels):**
"""
impact_assessment_draft = llm_generate(prompt_4_impact_assessment_enhanced)
# --- HUMAN REVIEWS/EDITS finalizes impact assessment ---
# step4_doc['Assessment of Overall Impact on Position Under Review'] = reviewed_impact_assessment

# 4. Enhanced Prompt 4.4 (Draft Recommendations - More Detail)
prompt_4_recommendations_enhanced = f"""
Based on the key critiques and their assessed impact, brainstorm actionable recommendations for the authors/decision-makers of the original 'Position Under Review'.

Summary of Key Critique Points:
---
{step4_doc['Summary of Key Critique Points & Substantiation']}
---
Assessed Overall Impact:
---
{step4_doc['Assessment of Overall Impact on Position Under Review']}
---

**Instructions & Rules for Drafting Recommendations:**
1.  **Directly Address Critiques:** Each recommendation should clearly aim to resolve, mitigate, or investigate further a specific weakness identified in the 'Summary of Key Critique Points'. Reference the relevant CR-C# or CR-R# impact point.
2.  **Actionable & Specific:** Phrase recommendations as concrete actions (e.g., "Conduct analysis X using data Y," "Revise assumption Z based on evidence W," "Gather stakeholder feedback on topic V"). Label recommendations sequentially CR-R{next_cr_r_id}...
3.  **Constructive Framing:** Focus on improving the decision-making process or the robustness of the position.
4.  **Avoid Prescribing *The* Answer:** Focus on *how* to improve the analysis or address risks, not dictating the final decision itself (unless the critique definitively disproves the position).

**Draft Recommendations for Consideration (with CR-R# labels):**
"""
recommendations_draft = llm_generate(prompt_4_recommendations_enhanced)
# --- HUMAN REVIEWS/EDITS finalizes recommendations ---
# step4_doc['Recommendations for Consideration'] = reviewed_recommendations

# 5. Human Adds Final Limitations, References etc. to compile Step 4 Document
# ...
These enhanced SPCP prompts, current as of Friday, April 18, 2025 at 7:10 PM EDT in Richmond, Virginia, provide detailed, rule-based guidance for using an LLM within a structured critique framework. They focus the LLM on specific sub-tasks like identifying assumptions, brainstorming scrutiny points based on analytical principles, structuring counter-arguments, summarizing evidence, and drafting impact assessments and recommendations, always requiring human oversight for critical judgment, evidence gathering/validation, and final synthesis.