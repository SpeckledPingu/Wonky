from dataclasses import dataclass, field

@dataclass
class SearchDocument:
    run_id: str
    result_id: str
    title: str
    summary: str
    source_file: str
    start_index: int
    end_index: int
    chunk_id: str
    id: str
    type: str
    typeId: str
    active: bool
    source: str
    topics: list
    version_id: str
    date: str
    _distance: float
    grounding: str = ""

@dataclass
class Insight:
    run_id: str
    result_id: str
    insight_type: str
    insight_name: str
    insight_synopsis: str
    related_citations: list
    citation: str
    insight_text: str = ''
    insight_data: list = field(default_factory=list)

@dataclass
class ResearchPath:
    run_id: str
    query: str
    run_time: str
    name: str = 'default_research'
    description: str = 'the default research description'

@dataclass
class Policy:
    run_id: str
    result_id: str
    source_document_id: str
    citation: str
    policy_name: str
    policy_type: str
    primary_objective: str
    mechanism_of_action: str
    policy_details: str
    key_stakeholders: dict
    authors_apparent_stance: str
    specific_evidence: str
    policy_text: str = ''
    arguments_in_favor: list = field(default_factory=list)
    arguments_against: list = field(default_factory=list)
    locations_in_source: list = field(default_factory=list)