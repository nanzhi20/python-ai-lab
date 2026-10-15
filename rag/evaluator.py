import json
from pathlib import Path

from document_loader import load_document
from text_splitter import split_markdown_sections
from retriever import retrieve

def load_eval_questions(file_path: str | Path) -> list[dict]:
    path = Path(file_path).resolve()
    content = path.read_text(encoding="utf-8")
    return json.loads(content)

def extract_section_title(chunk: str) -> str:
    for line in chunk.splitlines():
        if line.startswith("##"):
            return line.removeprefix("## ").strip()

    return "未知章节";

def main():
    answerable_count = 0
    hit_at_1_count = 0
    hit_at_2_count = 0

    unanswerable_count = 0
    correct_rejection_count = 0


    document = load_document("../data/knowledge.md")
    chunks = split_markdown_sections(document)

    eval_questions = load_eval_questions("../data/eval_questions.json")

    for index, eval_question in enumerate(eval_questions, start=1):
        question = eval_question["question"]
        expected_section = eval_question["expected_section"]

        results = retrieve(question, chunks)

        actual_sections = [
            extract_section_title(result.chunk)
            for result in results
        ]

        if expected_section is None:
            unanswerable_count += 1
            if not results:
                correct_rejection_count += 1
            continue

        answerable_count += 1

        if expected_section in actual_sections[:1]:
            hit_at_1_count += 1

        if expected_section in actual_sections[:2]:
            hit_at_2_count += 1

        print(f"================问题{index}==================")
        print(f"问题:{question}")
        print(f"预期章节:{expected_section}")

        if not results:
            print("检索结果:无")
            continue
        for rank, actual_section in enumerate(actual_sections, start=1):

            print(
                f"检索结果{rank}:{actual_section}，"
                f"分数:{results[rank-1].score}"
            )
            print(f"是否命中：{actual_section == expected_section}")


    hit_at_1 = hit_at_1_count / answerable_count
    hit_at_2 = hit_at_2_count / answerable_count

    print("\n=============评估结果=============")
    print(f"可回答问题数量:{answerable_count}")
    print(f"Hit@1: {hit_at_1_count}/{answerable_count}={hit_at_1:.2%}")
    print(f"Hit@2: {hit_at_2_count}/{answerable_count}={hit_at_2:.2%}")

    print(f"知识库外问题数量:{unanswerable_count}")
    print(
        f"正确拒绝数："
        f"{correct_rejection_count}/{unanswerable_count}"
    )


if __name__ == "__main__":
    main()
