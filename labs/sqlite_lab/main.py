from labs.sqlite_lab.database import (
    DATABASE_PATH,
    create_connection,
    initialize_db
)
from labs.sqlite_lab.models import KnowledgeChunk
from labs.sqlite_lab.repository import KnowledgeChunkRepository
from labs.sqlite_lab.service import KnowledgeChunkService

def main():
    conn = create_connection()
    try:
        initialize_db(conn)

        repository = KnowledgeChunkRepository(conn)

        chunks = repository.find_by_section("不存在的章节")

        for chunk in chunks:
            print(
                f"ID：{chunk.id}，"
                f"内容：{chunk.content}"
            )

    finally:
        conn.close()


if __name__ == '__main__':
    main()