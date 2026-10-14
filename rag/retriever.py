from dataclasses import dataclass

import jieba


STOP_WORDS = {
    "lanshare",
    "项目",
    "知识库",
    "什么",
    "如何",
    "可以",
    "这个",
    "一个",
    "以及",
    "使用"
}

@dataclass(frozen=True)
class RetrievalResult:
    chunk: str
    score: int


def _tokenize(text: str) -> set[str]:
    tokens: set[str] = set()
    for token in jieba.lcut(text):
        normalized = token.strip().casefold()

        if len(normalized) <= 1:
            continue

        if normalized in STOP_WORDS:
            continue

        tokens.add(normalized)
    return tokens


def retrieve(
        question: str,
        chunks: list[str],
        top_k: int = 2
) -> list[RetrievalResult]:
    if not question or not question.strip():
        raise ValueError("检索问题不能为空")

    if not chunks:
        raise ValueError("知识片段不能为空")

    if top_k <= 0:
        raise ValueError("top_k必须大于0")

    question_tokens = _tokenize(question)
    results: list[RetrievalResult] = []

    for chunk in chunks:
        chunk_tokens = _tokenize(chunk)

        common_tokens = chunk_tokens & question_tokens
        score = len(common_tokens)

        if score > 0:
            results.append(
                RetrievalResult(
                    chunk,
                    score)
            )
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]