from pathlib import Path
import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_ROOT / 'data' / 'chroma_demo'

COLLECTION_NAME = "knowledge_demo"


def get_collection():
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=None
    )
    return collection


def add_demo_records(collection):
    if collection.count() > 0:
        print("Collection已有数据, 跳过初始化")
        return
    collection.add(
        ids=[
            "chunk-file",
            "chunk-text",
            "chunk-security"
        ],
        documents=[
            "同名文件不会相互覆盖。",
            "共享文字会保存在服务端。",
            "系统不适合直接暴露到公网。"
        ],
        metadatas=[
            {
                "source": "lanshare.md",
                "section": "文件共享"
            },
            {
                "source": "lanshare.md",
                "section": "文字共享"
            },
            {
                "source": "lanshare.md",
                "section": "安全与性能限制"
            }
        ],
        embeddings=[
            [1.0, 0.0, 0.0],
            [0.8, 0.2, 0.0],
            [0.0, 0.0, 1.0]
        ]
    )
    print("示例数据添加完成")


def query_demo(collection):
    results = collection.query(
        query_embeddings=[
            [0.0, 0.1, 0.9]
        ],
        n_results=2,
        include=[
            'documents',
            'metadatas',
            'distances'
        ]
    )

    ids = results['ids'][0]
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]

    for rank, (
        record_id,
        document,
        metadata,
        distance,
    ) in enumerate(
        zip(
            ids,
            documents,
            metadatas,
            distances
        ),
        start=1
    ):
        print("--------------------")
        print(f"排名:{rank}")
        print(f"ID: {record_id}")
        print(f"文档: {document}")
        print(f"章节:{metadata['section']}")
        print(f"距离:{distance}")


def print_record_by_id(
        collection,
        record_id: str
) -> None:
    result = collection.get(
        ids=[record_id],
        include=[
            'documents',
            'metadatas',
            'embeddings'
        ]
    )
    if not result['ids']:
        print(f"没有找到记录:{record_id}")
        return

    print("--------------------------")
    print(f"ID: {result['ids'][0]}")
    print(f"文档:{result['documents'][0]}")
    print(f"元数据:{result['metadatas'][0]}")
    print(f"向量:{result['embeddings'][0]}")


def run_crud_demo(collection):
    print(f"\n1.新增临时记录")
    collection.upsert(
        ids=["chunk-access"],
        documents=[
            "手机通过局域网地址访问系统。"
        ],
        metadatas=[
            {
                "source": "lanshare.md",
                "section": "访问方式"
            }
        ],
        embeddings=[
            [0.2, 0.7, 0.1]
        ]
    )

    print(f"新增后数量:{collection.count()}")

    print_record_by_id(collection, "chunk-access")

    print(f"\n2.更新同一条记录")
    collection.upsert(
        ids=["chunk-access"],
        documents=[
            "手机通过局域网IP和端口访问系统。"
        ],
        metadatas=[
            {
                "source": "lanshare.md",
                "section": "访问方式",
                "updated": True
            }
        ],
        embeddings=[
            [0.1, 0.8, 0.1]
        ]
    )

    print(f"更新后数量：{collection.count()}")

    print_record_by_id(
        collection,
        "chunk-access"
    )

    print(f"\n3.删除临时记录")

    collection.delete(
        ids=["chunk-access"],
    )

    print(f"删除后数量:{collection.count()}")

    print_record_by_id(collection, "chunk-access")


def query_relevant_records(
        collection,
        query_embedding: list[float],
        top_k,
        max_distance,
        section: str | None = None
) -> list[dict]:
    where = None if not section else {
        'section': section
    }
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            'documents',
            'metadatas',
            'distances'
        ],
        where=where
    )
    #错误写法if not results:(空results示例:{"ids":[[]],...})
    if not results['ids']:
        return []
    ids = results['ids'][0]
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    records = [
        dict(id=record_id, document=document, metadata=metadata, distance=distance)
        for record_id, document, metadata, distance in zip(ids, documents, metadatas, distances, strict=True)
        if distance <= max_distance
    ]
    return records


def main():
    collection = get_collection()
    add_demo_records(collection)
    records = query_relevant_records(collection, query_embedding=[1.0, 0.8, 0.1], top_k=3, max_distance=2, section="文件共享")
    print(records)


if __name__ == "__main__":
    main()