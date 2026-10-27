from dataclasses import dataclass

import hashlib

@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    source: str
    content: str
    section: str
    content_hash: str


def calculate_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def create_knowledge_chunk(source: str, section: str, content: str) -> KnowledgeChunk:
    chunk_id = calculate_hash(source + "\n" + section)
    content_hash = calculate_hash(content)
    return KnowledgeChunk(id=chunk_id, source=source, content=content, section=section, content_hash=content_hash)

