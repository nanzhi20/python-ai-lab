import json
from pathlib import Path
from statistics import mean

from rag.embedding_service import EmbeddingService
from rag.vector_retriever import retrieve_by_vector
from rag.vector_store import (
    create_chroma_client,
    get_knowledge_collection
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_PATH = PROJECT_ROOT / "data" / "eval_questions.json"


def load_evaluation_questions(
        path: Path
) -> list[dict]:
    with path.open(
        mode="r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    # 同时兼容两种JSON结构：
    # 1. 直接使用数组
    # 2. {"questions": [...]}
    if isinstance(data, dict):
        data = data["questions"]

    if not isinstance(data, list):
        raise ValueError("评估题文件格式错误")

    return data


def print_distance_summary(
        name: str,
        distances: list[float]
) -> None:
    if not distances:
        print(f"{name}：暂无数据")
        return

    print(
        f"{name}："
        f"最小值={min(distances):.4f}，"
        f"最大值={max(distances):.4f}，"
        f"平均值={mean(distances):.4f}"
    )


def print_threshold_evaluation(
        answerable_distances: list[float],
        unanswerable_distances: list[float]
) -> None:
    thresholds = [
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70
    ]

    print("\n候选阈值评估：")

    for threshold in thresholds:
        accepted_answerable = sum(
            distance <= threshold
            for distance in answerable_distances
        )

        rejected_answerable = sum(
            distance > threshold
            for distance in answerable_distances
        )

        rejected_unanswerable = sum(
            distance > threshold
            for distance in unanswerable_distances
        )

        accepted_unanswerable = sum(
            distance <= threshold
            for distance in unanswerable_distances
        )

        correct_count = (
            accepted_answerable
            + rejected_unanswerable
        )

        total_count = (
            len(answerable_distances)
            + len(unanswerable_distances)
        )

        accuracy = correct_count / total_count

        print(
            f"阈值={threshold:.2f}，"
            f"正常接受={accepted_answerable}，"
            f"正常误拒={rejected_answerable}，"
            f"库外拒绝={rejected_unanswerable}，"
            f"库外误收={accepted_unanswerable}，"
            f"区分准确率={accuracy:.2%}"
        )


def evaluate() -> None:
    questions = load_evaluation_questions(
        EVALUATION_PATH
    )

    client = create_chroma_client()
    collection = get_knowledge_collection(client)
    embedding_service = EmbeddingService()

    answerable_count = 0
    hit_at_1_count = 0
    hit_at_2_count = 0
    unanswerable_count = 0

    answerable_top1_distances: list[float] = []
    unanswerable_top1_distances: list[float] = []

    for question_number, item in enumerate(
            questions,
            start=1
    ):
        question = item["question"]
        expected_section = item.get(
            "expected_section"
        )

        results = retrieve_by_vector(
            question=question,
            collection=collection,
            embedding_service=embedding_service,
            top_k=2,
            max_distance=None
        )

        print(
            f"\n{'=' * 20}"
            f"问题{question_number}"
            f"{'=' * 20}"
        )
        print(f"问题：{question}")
        print(f"预期章节：{expected_section}")

        for result_number, result in enumerate(
                results,
                start=1
        ):
            print(
                f"检索结果{result_number}："
                f"章节={result.section}，"
                f"距离={result.distance:.4f}"
            )

        if expected_section:
            answerable_count += 1

            hit_at_1 = (
                len(results) >= 1
                and results[0].section
                == expected_section
            )

            hit_at_2 = any(
                result.section == expected_section
                for result in results[:2]
            )

            if hit_at_1:
                hit_at_1_count += 1

            if hit_at_2:
                hit_at_2_count += 1

            if results:
                answerable_top1_distances.append(
                    results[0].distance
                )

            print(f"是否命中Hit@1：{hit_at_1}")
            print(f"是否命中Hit@2：{hit_at_2}")

        else:
            unanswerable_count += 1

            if results:
                unanswerable_top1_distances.append(
                    results[0].distance
                )

            print("该问题属于知识库外问题")

    print("\n")
    print("=" * 20 + "评估结果" + "=" * 20)

    print(f"可回答问题数量：{answerable_count}")

    if answerable_count > 0:
        hit_at_1_rate = (
            hit_at_1_count
            / answerable_count
        )
        hit_at_2_rate = (
            hit_at_2_count
            / answerable_count
        )

        print(
            f"Hit@1："
            f"{hit_at_1_count}/{answerable_count}"
            f"={hit_at_1_rate:.2%}"
        )

        print(
            f"Hit@2："
            f"{hit_at_2_count}/{answerable_count}"
            f"={hit_at_2_rate:.2%}"
        )

    print(
        f"知识库外问题数量："
        f"{unanswerable_count}"
    )

    print_distance_summary(
        name="可回答问题Top-1距离",
        distances=answerable_top1_distances
    )

    print_distance_summary(
        name="知识库外问题Top-1距离",
        distances=unanswerable_top1_distances
    )

    print_threshold_evaluation(
        answerable_distances=answerable_top1_distances,
        unanswerable_distances=unanswerable_top1_distances
    )


def main() -> None:
    evaluate()


if __name__ == "__main__":
    main()