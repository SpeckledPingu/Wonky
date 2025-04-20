## Search Patterns

Search patterns is a slightly different concept than most search.

#### What is a search pattern?
- A search pattern is a *strategy*.
- The strategy is to retrieve information in such a way that it's predictable and allows interactions between content sources.
- Search patterns often arise from developing workflows as a means to get the required information.

#### Why have search patterns as their own thing?
- Search patterns arise from workflows, but they are not necessarily unique to that workflow.
- While some search patterns are, and forever will be, unique to that workflow, ones that can be reused should be isolated.
  - This reduces the main problem of glue code existing inside of workflows
  - This formalizes glue code as a means to retrieve data that can be done independently of a workflow.
  - Just makes it easier to build on top of previous work.