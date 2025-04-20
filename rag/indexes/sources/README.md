### Sources

- Sources are specific to a specific source (obviously)
- Not so obvious are the specific parsing and representation of the documents.
- Often, there are re-used on-the-fly chunking strategies that are common across multiple workflows using the sources.

Examples of this are:
- Creating citations
- Using chunking min and max positions to pull all intermediate chunks into the grounding
- Expanding a single chunk to include above and below chunks
- Repeated extractions on a source.

### Why decouple this from ingestions?
Because ***Indexes are NOT databases***

An index being used as an index is often fine for development, but terrible for production.
- The reason for decoupling this from the index is that indexing is a time consuming process for most index technologies.
- Once a field is added, most modern indexes require re-ingestion
- Indexes do not allow for relationships, joins, or any other SQL/NoSQL processes
- While some indexes say that they have some level of SQL allowed, this does not mean it's a database.
  - All it means is that there is a common syntax that a data scientist/engineer can use for familiar processes

