# Wonky
Human centric public policy research platform supported by generative ai and agents.

***Wonky's golden rule:*** If a person would not create an agent's output in their workflow, it should not be in a workflow.

## What is Wonky?
Wonky is an app that is aimed at people who need to understand the impacts of new policy, or researching new avenues for policy development.
The goal is to build a platform for government officials, public policy researchers, and those who are just curious in exploring the world of policy research.

The initial sources for this are CRS Reports and Wikipedia. CRS Reports are of very high quality analysis and providing 
lots of contextual information. Wikipedia is useful for further exploration or filling in gaps, but hardly an authoritative source.
Combining the two, and maintaining clear distinctions between the sources (and any additional sources), can provide both 
intuitive trust in the system by clearly defining the sources of information.

https://www.everycrsreport.com/

## What are Yargs?
There are so many gen ai products aimed at chatting with documents and creating personal RAGs off of your 
existing documents that it might seem that we don't need Yet-Another-RAG (Yargs) or Chat-With-My-Documents.

Most Yargs are single turn chat systems. You upload your documents, ask questions about them, and quickly they run into the same problems.
While this is absolutely essential to research systems, it remains constrained to ad-hoc interactions.
Worse, reuse of great chats is next to impossible unless you reload the entire chat.

When working with token counts *and* worrying about maintaining accuracy, these systems just don't cut it.
Newer approaches by Anthropic, Google, and others, introduced the idea of Artifacts. This introduction of break points in
a interrogative workflow is often underrated as a new development when news is dominated by SOTA developments.

Furthermore, the advent of providing citations improves a fundamental process that improves trust in the system. It allows
the user to check the information, or follow up in new pathways.

## What Wonky focuses on:
#### Wonky approaches the use of LLMs from the perspective that users need clear, intuitive, and repeatable processes in their workflow. Researchers especially need citations, long chain information tracking, and non-prose documents that represent the information they need.
With the current citation and artifact approach, you are still bound to the LLM interpreting your chats correctly to initiate the creation of a document.
They also do not allow for customization of what a citation represents in a document, or for clear processes to be developed
for automated fact checking, reviewing, and other common human processes during research.

##### For a deep research system to work:
 - A platform must preserve documents across multiple sessions
 - These documents must be composable into new documents
 - Processes need to be repeatable and intuitive
 - Intermediate documents must be created within complex workflows for both: 
   - Human reviewable checks on the workflow's process
   - Providing branching points for researchers to start from for new research without rerunning an entire workflow
- Tasks that agents perform should represent the translation of knowledge and information from one source to another, not a cognitive process or "thinking" done by an LLM since these cannot be verified as being related at all to the final output.
- Citations cannot be arbitrary
  - Citations that are arbitrary sections can be helpful for tracing the source of information, but releasing the control of citations means being locked into chunking strategies within an index, the whim of an llm, and a single universal structure for all information (this is just patently false). 

### To do this we must think of workflows and documents as structured documents, not prose
Key to this concept is that a workflow does not necessarily terminate in the final document.
When drafting an executive summary, multiple sources are used to compose the final draft.
In most agentic systems, like Langchain, LangGraph, and many more, these documents are either:
- Hidden from the user after completion
- May not represent anything resembling what a person might provide
- Inconsistent between different runs

Designing agentic systems should focus on these documents first.
Because they represent a collection of information from multiple documents, these **must** represent something that a person might develop.
If a user cannot easily review the supporting documents, they waste time that could be spent on ideation or deeper manual research.

##### How can we do this? Structuring intermediate documents.
If these documents do not follow any sort of structured approach with definable fields and what goes into those fields and/or excluded (just prose), 
the output of the system is much more likely to vary. Prose centric information is difficult to define with rules and llms often have their own voice in writing this.
Structuring intermediate documents means providing definable fields **that only relate to the information within the document**.
These fields are far more easily defined by rules around what information is valuable and structuring them as lists provides
the user with a much faster fact checking process. They can also use parts of the document for future work,
or if one of the sections is incorrect, the rest might be of high value and still usable.

This is called a fast-rejection time.

This fast rejection time is central to most information retrieval systems with a focus on relevance at a top-n.
A person can quickly scan the first 3 or 5 results from a search and before even being able to fully read the snippets and titles,
they're able to roughly determine relevance. If no relevant documents are there, the turnaround to a new query is fast.

Prose based systems do not have this quality because they have a high level of uniqueness per document.

This also prevents the accumulation of skill in using a tool.

Even if a structured document's fields do not always perfectly align with what a user might want, they can leverage the format
to develop scanning skills to identify what information they truly need, or is missing from the final document.
Building skill with a tool is difficult with the high variance of llm outputs and constant drift in prompt engineering.
If you can't use yesterday's methods today, then you are always being reset to zero.

Agent based systems suffer from that yesterday is not today problem.
- Each update to a model will shift its output.
- Each modification to an orchestrator will have significant downstream impacts.
- Processes that worked for one orchestration system might never work again or be permanently degraded in quality.


### Wonky is focused on agents that align with human-centric processes
There's so much more to Wonky than just structuring documents and creating intermediate documents.
However, every part of a workflow is driven by Wonky's golden rule. This means that there are multiple intermediate documents
of direct use to the user, even if the final output is incorrect or of limited use. Often, in 
research flows, the value of the research is in the notes as much as the report. In fact, in almost all workflows people 
undertake, we naturally learn to do them by first writing out the information we need and then compiling it 
into the final document. As we get better, we no longer need to take as many notes, or we get better at note taking.
But a workflow can, and should, be represented in this way.

Agentic systems that try to model a person's cognitive processes will always suffer from the fact that LLMs do not reason 
and cannot replicate what a person's internal process is. Worse yet, everyone has a different process.

Agentic systems that focus on the intermediate documents as human-centric and being of intermediate value helps solve this.
All that is needed is to map the structure of information in a source to a structure in the output.
This is still difficult, relies on domain knowledge, and can take a significant amount of time. However, 
it is much easier to deconstruct a workflow into these intermediate documents, get SME feedback on an alignment to what they expect to see, 
and follows the other principle of: ***LLMs need sufficient context to work well***


