def split_markdown_sections(text: str) -> list[str]:
    if not text or not text.strip():
        raise ValueError("待切分文本不能为空！")

    parts = text.strip().split("\n## ")

    if(len(parts) <= 1):
        return [text.strip()]

    title = parts[0].removeprefix("# ").strip()
    chunks: list[str] = []

    for section in parts[1:]:
        section = section.strip()

        if not section:
            continue
        chunk = f"文档:{title}\n## {section}"
        chunks.append(chunk)

    return chunks