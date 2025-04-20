## What is a workflow?

A workflow is just a sequence of steps to produce an output.

But, workflows can become very complex with a lot of interactions.
Encapsulating a workflow as a single system limits its reuse.
Instead, it tends to promote copy-pasting entire workflows and making adjustments to them.

While this is okay with a few workflows, it degrades the reuse.

Worse yet, the representation of data is only maintained ***within the entire workflow***.
Representation of data and text within a workflow should not be a system of inputs and outputs to different agents.
Instead, the representation should represent a task that a person would do that has a definable input if it was done by hand with an infinite amount of time by a user/SME.
These become instrumented and reusable documents that represent a state of knowledge within the system.

If you want to reuse a part of a workflow, your documentation and representation of these intermediate steps is easily explained and understood by a knowledge state.
You can think of this like object oriented programming.
- The knowledge state is the class variables.
- The encapsulated functions are the steps within a workflow.

### Pitfalls to avoid when designing a workflow.

The #1 mistake that can be made is to rely too much on object oriented programming and encapsulating data representations with individual functions.
The representation of the information is maintained ***in the system*** and ***in the inputs/outputs of the steps.***

If you go down the route of manipulating data within a class, future use of that class requires knowledge of:
- The system state
- What the input data is
- What the output data is
- In the case of search results, what the source information looks like
- How the class represents the data
- How the class is transforming the data

In short, to understand the code, you need to become a master of the system.
You also rely on the level of skill and knowledge of the initial developer/data scientist.
Part of this is whether the system has good documentation (we all know this fails about the midpoint of a project and you need to meet deadlines)

Documentation becomes easier by using plain english to describe the inputs, the outputs, and the task that is being emulated.

## Agent Design in Workflows

This is perhaps the most important confusion to clear up.

***Agents should not represent a mental state of a person***

***Agents should represent the transformation of knowledge from a starting point to an end point***
- The relationships inside of cognitive processes that a person goes through to solve a problem are extremely, if not impossible, to actually capture.
  - Even experts (and often experts) provide incorrect information when describing what they are doing.
  - This is because most cognitive processes an expert uses have become mental muscle memory. They're working backwards to explain something they intuit.
  - An expert walking you through their workflow is invaluable, but it does not necessarily translate to a semi-deterministic agent process.
- Identifying key structures and relationships in sources, and what structures and relationships exist in the resulting document is easier for an SME to provide.
- This is also easier to represent using LLMs.
  - Think of LLMs as a translation of english-to-english.
  - Key grammatical and syntactic structures from one language to another are what an llms provide as a service.
  - The semantic information, the utility of the initial sentences is preserved when translating to a new language.
  - English-to-english translation is the mapping of key structures that represent useful information/knowledge from:
    - Verbose to simplified language (summary)
    - Multiple sources to a single document (extraction)
    - A single source to multiple documents (expansion, such as search)
- Reuse is much easier with this task design.
  - When modeling cognitive processes, these are often highly specific to a task.
    - Powerful LLMs can do better at this task with less effort. However, that does not mean they are reusable agents.
    - If a cognitive process differs between workflows (which invariably it does), the agent develops brittleness
      - This brittleness often results in endless prompt engineering to tweak it to a new mental process.
  - When modeling a process as information mapping, if you need that knowledge-to-knowledge **relationship**, then your system is much more reusable.

##### Example:

Let's model a paper grader:

With cognitive modeling by an agent, this gets represented when a use case is identified. Let's say it's a Shakespeare course.
- The processes by which a identifies and reasons about information will be different based on whether they are using the final information in a certain way.
- The system might have an agent for analyzing poetry vs prose vs plays.
- It might have criteria for different key points that a student needs to provide that map back to sources.
- Finally, based on the initial type of paper, the relevant sources are compared to the final paper and a score is given along multiple dimensions of a rubric.

The complexity of modeling all these intents and processes involves significant process development and prompt engineering.

However, if you are grading a paper by hand, you often go about this differently.
- First, you'd figure out what the paper was about by its topic and thesis.
- Then you'd go paragraph by paragraph and identify the claims and their relationship to the thesis.
  - You would take notes on these two things.
  - These sorts of claims in an English paper tend to fall along language, history, context, and several more.
  - This creates the ***Note Structure***
  - This structure is reused over and over again.
  - This is Passage-to-Note
- With a **structured note** you would compare its set of fields to the source, and search for related content to achieve **sufficient context**.
  - Sufficient context is crucial. Without enough context, or context is not clearly defined, llms will go with their best guess at what is relevant.
  - We want to eliminate as much "hoping the LLM figures it out" as possible because errors compound in this type of system.
  - With a hub and spoke orchestrator agent system, things can go off the rails fast.
- Finally, you'll tally each Note-to-Score and the final grade is the summing up of deducted points.

Now if you want to modify the system, you might only need to specify specific rules for the Passage-to-Note for specific information.
Or, you might modify the structured note to a point deduction to handle new/unique text with a well defined rubric for each type of source.

The key thing is that the intermediate documents are reusable AND, most importantly, can be better instrumented.
The Passage-to-Note can be assessed solely on the quality of the note.
The Note-to-Score can be aligned by numerical alignment.
Both are reusable in similar tasks out of the box.

In this system, the need for an orchestrating model is significantly reduced by mapping activities to an information-to-information translation.
What an agent does is discrete and independently assessable. An orchestrator defining dynamic pathways based on intent can vary wildly based on initial inputs and intermediate agents making choices.

## In short, minimize the need for orchestration by developing intermediate documents that represent what a person would do if they could perform a task as rigorously as possible while tracking information.