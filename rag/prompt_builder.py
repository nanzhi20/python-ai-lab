def build_rag_prompt(
        question: str,
        context_chunks: list[str]
) -> str:
    if not question or not question.strip():
        raise ValueError('问题不能为空!')

    valid_chunks = [
        chunk.strip()
        for chunk in context_chunks
        if chunk and chunk.strip()
    ]

    if not valid_chunks:
        raise ValueError("参考资料不能为空")

    context = "\n\n---\n\n".join(valid_chunks)

    return f"""你是一个基于资料回答问题的助手。
    请遵守以下规则：
    1. 仅根据提供的资料回答问题。
    2. 不要自行补充资料中不存在的事实。
    3. 如果资料不足，请明确回答“根据现有资料无法确定”。
    4. 回答应当简洁、清晰。
    <资料>
    {context}
    </资料>
    <问题>
    {question.strip()}
    </问题>
    """