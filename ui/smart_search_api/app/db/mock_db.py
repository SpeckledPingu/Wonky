# This file simulates a database for demonstration purposes.
from typing import Dict, List
from app.schemas import Document, Report, Extraction
import datetime

MOCK_DOCUMENTS: Dict[str, Document] = {
  'doc-001': Document(
    id='doc-001',
    title='The Impact of AI on Scientific Research',
    content='# The Impact of AI on Scientific Research\n\nThis document explores how Artificial Intelligence is revolutionizing scientific methodologies, from data analysis to hypothesis generation.\n\n- **Data Analysis**: AI algorithms can process vast datasets orders of magnitude faster than traditional methods.\n- **Pattern Recognition**: Machine learning models excel at identifying subtle patterns that may be missed by human researchers.',
    tags=['AI', 'Research', 'Technology'],
    color='blue'
  ),
  'doc-002': Document(
    id='doc-002',
    title='Climate Change Policies: A Global Overview',
    content='# Climate Change Policies\n\nA comprehensive review of international policies aimed at combating climate change, focusing on the Paris Agreement and subsequent national commitments.\n\nKey areas include:\n1. Carbon Pricing Mechanisms\n2. Renewable Energy Subsidies\n3. International Cooperation',
    tags=['Climate', 'Policy', 'Environment'],
    color='green'
  ),
  'doc-003': Document(
    id='doc-003',
    title='Advances in Quantum Computing',
    content='# Advances in Quantum Computing\n\nThis paper discusses the latest breakthroughs in quantum computing, including the development of more stable qubits and novel quantum algorithms. The potential impact on cryptography and materials science is immense.',
    tags=['Quantum', 'Computing', 'Physics'],
    color='purple'
  )
}

# --- Mock Extractions Data ---
MOCK_EXTRACTIONS: Dict[str, Extraction] = {
    "ext-001": Extraction(
        id="ext-001",
        sourceDocId="doc-001",
        type="insight",
        stance="pro",
        content="AI-driven data analysis is the most significant factor in accelerating genomic research."
    ),
    "ext-002": Extraction(
        id="ext-002",
        sourceDocId="doc-002",
        type="policy",
        stance="pro",
        content="A global carbon tax is proposed as the most effective policy for reducing emissions."
    ),
    "ext-003": Extraction(
        id="ext-003",
        sourceDocId="doc-002",
        type="insight",
        stance="con",
        content="National interests frequently undermine international cooperation on climate agreements."
    ),
    "ext-004": Extraction(
        id="ext-004",
        sourceDocId="doc-003",
        type="case_study",
        stance="pro",
        content="Case Study: A 53-qubit quantum processor successfully demonstrated supremacy over classical supercomputers in a specific computational task."
    )
}


# --- Mock Reports Data ---
MOCK_REPORTS: Dict[str, Report] = {
    "report-pre-001": Report(
        id="report-pre-001",
        title="Analysis of AI and Climate Documents",
        content="## Combined Analysis Report\n\nThis report synthesizes findings from documents on **Artificial Intelligence** and **Climate Policy**. A key takeaway is the potential for AI-driven climate modeling to significantly improve prediction accuracy. However, policy frameworks struggle to keep pace with technological advancement.",
        sourceDocuments=["doc-001", "doc-002"],
        analysis="compare_contrast",
        generatedAt=datetime.datetime.now() - datetime.timedelta(days=1)
    ),
    "report-pre-002": Report(
        id="report-pre-002",
        title="Key Themes in Quantum Computing",
        content="## Thematic Extraction: Quantum Computing\n\nThe primary theme identified is the race for **quantum supremacy**. The document highlights the critical role of qubit stability and error correction in achieving this milestone. The secondary theme is the disruptive potential for cryptography.",
        sourceDocuments=["doc-003"],
        analysis="extract_themes",
        generatedAt=datetime.datetime.now() - datetime.timedelta(hours=4)
    ),
    # --- NEW MOCK REPORT ---
    "report-pre-003": Report(
        id="report-pre-003",
        title="Summary of Climate Policies",
        content="## Summary Report: Climate Policy\n\nThis is a processed summary focusing on the core tenets of global climate policy. The main points are carbon pricing and international cooperation, which are frequently discussed but difficult to implement.",
        sourceDocuments=["doc-002"],
        analysis="summarize",
        generatedAt=datetime.datetime.now() - datetime.timedelta(hours=1)
    )
}

# --- Mock Processing Bucket Data ---
# Pre-populating the bucket with a document ID.
PROCESSING_BUCKET: List[str] = ["doc-002"]

db = {
    "documents": MOCK_DOCUMENTS,
    "reports": MOCK_REPORTS,
    "extractions": MOCK_EXTRACTIONS,
    "processing_bucket": PROCESSING_BUCKET
}
