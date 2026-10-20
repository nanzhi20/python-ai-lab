from labs.chroma_lab.main import get_collection


def main():
    collection = get_collection()

    print(f"Collection名称:{collection.name}")
    print(f"已有记录数:{collection.count()}")

    results = collection.get(
        include=[
            'documents',
            'metadatas'
        ]
    )

    ids = results['ids']
    documents = results['documents']
    metadatas = results['metadatas']

    for record_id, document, metadata in zip(ids, documents, metadatas, strict=True):
        print("---------------------")
        print(f"ID: {record_id}")
        print(f"文档: {document}")
        print(f"章节:{metadata['section']}")


if __name__ == "__main__":
    main()
