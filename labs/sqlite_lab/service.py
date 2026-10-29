import sqlite3

from labs.sqlite_lab.models import KnowledgeChunk
from labs.sqlite_lab.repository import KnowledgeChunkRepository


class KnowledgeChunkService:
    def __init__(
            self,
            conn: sqlite3.Connection,
            repository: KnowledgeChunkRepository,
    ):
        self._conn = conn
        self._repository = repository

    def create_demo_chunks(self, simulate_error: bool=False) -> tuple[KnowledgeChunk, KnowledgeChunk]:
        try:
            first_chunk = self._repository.insert(
                content="文件保存在服务端本地目录中。",
                source="lanshare.md",
                section="文件共享",
            )

            if simulate_error:
                raise RuntimeError("模拟第二条记录插入前发生异常")

            second_chunk = self._repository.insert(
                content="二维码中保存的是访问地址。",
                source="lanshare.md",
                section="访问方式",
            )

            self._conn.commit()
            return first_chunk, second_chunk
        except Exception as e:
            self._conn.rollback()
            raise



