

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

