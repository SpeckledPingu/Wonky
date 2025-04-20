

trend_report_prompt = """Task: I have a write up on the topic: {topic} with a primary focus on: {focus}. I need you to identify the overall trends that concern:
- Evolving states of the status quo
- Challenges faced historically and/or currently
- Initiatives and solutions to challenges
- Outlook
- Drivers of change, challenges, and/or solutions.

Organize your trend analysis by each trend being a section with the name of the trend formatted as a markdown header '##' and sub-points as a markdown numbered, or bullet pointed, list.

Your analysis should provide the citations from the source material for the different statements providing information about the trend, or claims about the trend. The citation format can be found in the report text and in the sources in the format of '(report_name(section_number))'.

I have provided the report and the sources of information for the report. Make sure you only use information that is directly corroborated by the sources of information.

Do not introduce your trend analysis or provide a conclusion or outro. Just provide the requested analysis.

***Report:***
{report}

***Sources for the report:***
{sources}

Trends:
"""

follow_up_prompt = """Task: I have a trend analysis report and a broader report on the topic: {topic} and a focus on: {focus}.

-----
## Report:
{report}

## Trend Analysis:
{trend_analysis}

-----

Based on the information in the report, and the trends identified in the trend analysis, identify the specific context needed to give contextual information on historical conditions, drivers of trends, status quo, outlook for the future, challenges being faced, and initiatives.

Provide the phrases that I can use in wikipedia to find the relevant contextual articles. These should be in a bullet point list and organized by what contextual information they correspond to.

Do not introduce your response or provide a conclusion or outro. Just provide the requested list.

## Historical Conditions:

## Status Quo:

## Drivers of Trends:

## Challenges faced historically and/or currently:

## Initiatives and solutions to challenges:

## Outlook:

"""

extract_context_information_prompt = """
Task: I have a trend analysis based on a topic: {topic} with a primary focus driven by: {focus}. I also have a set of areas of interest for additional facts and context. It is absolutely critical that you do not introduce yourself, your response, or provide a conclusion or outro. Just provide the extracted information.

# Areas of Interest:
{areas_of_interest}

# Trend Analysis:
{trend_analysis}

-----

To give context, I've provided sections from different articles that may have relevant information. They might not have relevant information, or the information may be incomplete. That is okay. Only use what is available to extract the necessary context. Extract the key details that provide relevant context and information in the scope of the areas of interest or are relevant context to the trend analysis. At the end of each section, you will find the citation for that section in the form of (page_title|section_number|subsection_number). For each piece of information you extract, provide the source citation for it. This is an absolute must.

When extracting multiple pieces of information from the same section, condense them into a single bullet point unless they relate to distinct areas in areas of interest.

# Articles:
{articles}

-----

# Extracted Information:
"""

trend_interpolation_prompt = """I have a trend report that captures the general trends about the topic: {topic} with the focus being: {focus}. I also have a set of notes on relevant information to the trend report.

Task: The current trend analysis provides only partial information about the topic and the focus. Using just the relevant information from the notes I have provided, I need you to write an additional trend report based on the notes provided. Do not use the material in the existing trend report for writing this new analysis, unless the new information from the notes directly relates to a claim or statement in it. When using information from the existing trend analysis you must provide the citation of the claim or statement from the existing trend analysis.

Do not provide opinions, interpretation, introduction, conclusion, or any sort of introduction to your response. It is imperative that you only write a new report.

Structure the new report to use the same sections and section headers as the provided trend analysis. If there is no information to add to an existing section of the trend analysis, write that no new information was found.

The information you use to write the new the trend report *must* only come from the notes. Do not add any information that has not been provided in the notes or the trend analysis. Add as much contextual information as is available to your report with a focus on completeness of information over brevity. It's vital that I have a thorough report based on facts.

Next, you must add a section at the end with any case studies that are in the notes. Separate these by a title for each case study and provide the current conditions, situation of the case study, and how it relates to a specific trend in the trend report. Clearly label this in a separate section for each trend with the header "## Case Studies:" Only include case studies that have information on what was the problem, solution, and outcome for the case study.

# Trend Analysis:
{trend_analysis}

# Notes:
{notes}

# Trend Report:
"""

merged_trend_report_prompt = """ I have two trend reports that come from different sources. One is the initial trend report, that is a high quality report and I need all the information from that to be preserved. The second is one that has some additional context that is relevant, but not all of it might be on topic. The topic of my trend reports is: {topic}, with a focus on: {focus}. They have their citations in the format of (source_name(section_number)(subsection_number)).

Task: I need you to keep the information from the initial and add in the relevant information from the additional trend report.

It is absolutely vital that you preserve the citations of the statements when merging the trend reports so that I can keep track of the information.

You are also required to keep all the information from the initial report in the final report with no omissions.

# Initial Report:
{initial_report}

# Additional Report:
{additional_report}

# Merged Report:
"""

executive_summary_prompt = """I have an exhaustive trend report and analysis report on topic: {topic} with a focus on: {focus}

Write a executive summary of the most important issues facing Rural Broadband in America with details on the historical conditions, current situation, challenges faced in the status quo, impediments to solutions, and solutions. Use provided case studies if they are both present and relevant.

Your report should be thorough and professional. You must not use information from anywhere else. All the information should come from the trend analysis and analysis report.

# Trend Analysis:
{trend_report}

# Analysis Report:
{report}"""


follow_up_query_prompt = """I have an article that I'm reading and I want to follow up on it with reading through some wikipedia articles. I'm not sure what to search on wikipedia, so please provide me 2 or 3 short queries that I can put into their search. Provide them as just a list of the queries that I can run.

The queries should cover specific sections of the article AND have topical phrases that are about the entire document that must be in every query. The topical phrases can be inferred from the title of the document.

Do not introduce your response or provide any follow up questions or conclusion. The list should be a numbered list:

Here is the article I'm reading:

{article}"""