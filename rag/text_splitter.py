from rag.knowledge_chunk import KnowledgeChunk, create_knowledge_chunk

def split_markdown_chunks(
        text: str,
        source: str
) -> list[KnowledgeChunk]:
    if not text or not text.strip():
        raise ValueError("待切分文本不能为空")

    parts = text.strip().split("\n## ")
    if len(parts) <= 1:
        return []

    title = parts[0].removeprefix("# ").strip()
    chunks: list[KnowledgeChunk] = []

    for section in parts[1:]:
        section = section.strip()

        if not section:
            continue

        section_name, _, section_content = section.partition("\n")
        if not section_name:
            continue

        content = f"# {title}\n## {section_name}"
        if section_content:
            content += f"\n{section_content}"

        chunk = create_knowledge_chunk(source=source, section=section_name,content=content)
        chunks.append(chunk)
    return chunks


