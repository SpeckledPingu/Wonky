### Connectors Overview

- Connectors are the lowest level of interfacing with a corpus of documents that have been indexed.
- These are the interfaces with different index technologies, such as:
  - LanceDB
  - Elastic
  - Solr
  - Typesense

- There are several concepts to be mindful of:
  1. Index connectors are what handle the actual query formatting
  2. Filters are independent and are functionally oriented. These should be designed so that they can be assembled to create more complex sequences of filters.
  3. Filters can be both index specific (such as solr's "filter" field), and python based.
     - Index specific filters handle the actual query text.
     - Python specific filters add functionality post-search to improve the functionality of a search over that of just the native search capabilities.
