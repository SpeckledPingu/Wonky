extraction_prompt = """
Task: Identify the relevant sections to the topic, question, and focus I have provided. The topic that the question relates to is {topic} and the focus of my interest is {focus}. The only thing I want you to provide are a list of the citations. The different documents begin with the report number and the title of the report. This report number is the report_id in the citation pattern.

The title is only to provide context for what the report is about. You must not reference it.

Question: {question}

Documents:
{documents}

Instructions:
- Identify only the sections that provide useful information for answering the provided question.
- The citation pattern follows the pattern '([report_id]([section_number]))' as provided in the citation field of the documents. Do not use the brackets in your response, those are only there to indicate what values are in the citation.
- If no relevant sections are found for a question, indicate "No relevant sections found."
- Once the relevant sections are found, provide the citation pattern in a comma separated list.
- Do not introduce your answer, ask follow up questions, or provide a summary or outro. Only provide the list.
- Citations for relevant information must be provided with both the report_id and section_number where the information is from.
- A citation for a section can refer to multiple passages above it. Do not create new citations just because a paragraph or passage does not have a citation immediately after the passage. It'll be found at the end of the section.

Relevant Sections:
"""

query_expansion_prompt = """Task: I have a question about {topic}. I am focusing my research on finding information related the question: {question}. The general direction of this research is based on my focus that I have set forth for broader research: {focus}.

Instructions:
- Write at most two paragraphs that provides an answer to my question in the context of my topic and focus.
- Provide both general terminology and any specific, domain relevant, terms in your answer. This will help me understand the topic and focus on both a high level communicable level and details that provide crucial examples.
- Your answer should not be long. This is meant to get me started, not be a final answer on the subject.

Response Instructions:
- Do not introduce your response or provide a conclusion or summary. Just provide the answer.

Answer: """

search_expansion_prompt = """
Task: Generate 3 focused search questions for me to begin my research with.

Topic: {topic}
Focus: {focus}

Instructions:
- Create 3 questions that address the issues that I should begin my research with.
- Questions should directly address the intersection of the Topic and Focus.
- Prioritize questions that can be answered with factual information by Congressional Research Services reports.
- Do not add color, explanation, intros, outros, justification, or conclusion. Just provide the questions.

Questions:
1.
2.
3.
"""

report_prompt = """Task: I have a topic and a focus for my research that I am writing a report on. My topic is {topic}, and the focus of my research is {focus}. From my initial research, I have compiled a list of relevant sections from different sources.

I need you to extract the relevant information from my sources and organize it into a well structured report that provides all the relevant details, context for the details, all the scenarios and situations discussed in my sources (if there are any).

Instructions:
- First and foremost, you must not add any information, details, or hypotheticals to the report unless they are explicitly discussed in my sources.
- Carefully analyze what the major themes, topics, and situations of the sources are and which are relevant to the focus of my research on my topic.
- It is critical that you do not invent sources.
- It is critical that you provide the citation for each statement, fact, and scenario that you write about in your report.
- Work hierarchically for structuring your report. The main structure of your report should be organized into main sections by theme, followed by subsections containing the important facts, scenarios, any discussion from the sources about that topic, and a final summarization.
- Be thorough and avoid simplification. These are complex topics that I am researching and I need to have all the information available to me.

Sources:
{sources}

Report:
"""



parsing_prompt = """I have a document that's written in markdown. I want to split it into the main sections so that I can organize the different sections, and have a summary for the whole document that I can reference later on. I need you to provide the text that I can split the document on. That text should be the title or beginning of each major section.
If a section is the title of the document, prefix the string with "DOCUMENT TITLE:" so that I know it's not a section title. If it is a major section, prefix it with "SECTION #:" where the section number is a number that increments up from 1 to number the sections. If the document has an overall summary or conclusion for the entire document, provide that as an additional section.
If there is no summary, then the summary you write should be a paragraph or two at most and capture the main points about the document.

Structure your response with the following sections and formatting:

DOCUMENT_TITLE: [document title]
SECTION #:
SECTION #:
...
SUMMARY:

Here is my document:
{report}"""

