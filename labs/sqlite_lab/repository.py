import sqlite3
from labs.sqlite_lab.models import KnowledgeChunk


class KnowledgeChunkRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    @staticmethod
    def _row_to_chunk(
            row: sqlite3.Row,
    ) -> KnowledgeChunk:
        return KnowledgeChunk(
            id=row['id'],
            content=row['content'],
            source=row['source'],
            section=row['section'],
            created_at=row['created_at']
        )


    def find_all(self) -> list[KnowledgeChunk]:
        cursor = self._conn.execute(
            """
            SELECT
                id,
                content,
                source,
                section,
                created_at
            FROM
                knowledge_chunks
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        return [
            self._row_to_chunk(row)
            for row in rows
        ]


    def find_by_id(self, chunk_id: int) -> KnowledgeChunk:
        cursor = self._conn.execute(
            """
            SELECT
                id,
                content,
                source,
                section,
                created_at
            FROM
                knowledge_chunks
            WHERE id = ?
            """,
            (chunk_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_chunk(row)



    def insert(self,content: str, source: str, section: str) -> KnowledgeChunk:
        cursor = self._conn.execute(
            """
            INSERT INTO knowledge_chunks (
                content,
                source,
                section)
            VALUES
                (?, ?, ?)
            """,
            (content, source, section)
        )

        generated_id = cursor.lastrowid

        if generated_id is None:
            raise RuntimeError(f"数据库没有返回新纪录ID")

        chunk = self.find_by_id(generated_id)

        if chunk is None:
            raise RuntimeError(f"插入成功后无法查询到新纪录")

        return chunk

    def find_by_section(self, section: str) -> list[KnowledgeChunk]:
        cursor = self._conn.execute(
            """
            SELECT 
                id,
                content,
                source, 
                section, 
                created_at
            FROM
                knowledge_chunks
            WHERE section = ?
            ORDER BY id ASC
            """,
            (section,)
        )
        rows = cursor.fetchall()
        return [
            self._row_to_chunk(row)
            for row in rows
        ]