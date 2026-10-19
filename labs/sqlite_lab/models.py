from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeChunk:
    id: int
    content: str
    source: str
    section: str
    created_at: str
