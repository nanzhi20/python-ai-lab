import sqlite3
from pathlib import Path

DATABASE_PATH = Path("../data/sqlite_demo.db")

def create_table():
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS knowledge_chunks(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    section TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """
        )

        conn.commit()
    finally:
        conn.close()


def insert_chunk(
        content: str,
        source: str,
        section: str
) -> int:
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO knowledge_chunks
            (
                content,source,section
            )
                VALUES (?, ?, ?)
            """,
            (
                content,
                source,
                section
            )
        )

        conn.commit()
        generated_id = cursor.lastrowid
        return generated_id

    finally:
        conn.close()


def find_all_chunks() -> list[tuple]:
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                id,
                content, 
                source, 
                section, 
                created_at 
            FROM knowledge_chunks
            ORDER BY id
            """
        )
        chunks = cursor.fetchall()
        return chunks
    finally:
        conn.close()


def find_chunk_by_id(chunk_id: int) -> sqlite3.Row | None:
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id, content, source, section, created_at 
            FROM knowledge_chunks
            WHERE id = ?
            """,
            (chunk_id,)
        )

        row = cursor.fetchone()
        return row

    finally:
        conn.close()


def update_chunk_content(
        chunk_id: int,
        new_content: str
) -> bool:
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
                UPDATE knowledge_chunks
                SET content = ?
                WHERE id = ?
            """,
            (new_content, chunk_id)
        )
        conn.commit()
        return cursor.rowcount > 0;


    finally:
        conn.close()


def delete_chunk_by_id(
        chunk_id: int
) -> bool:
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM knowledge_chunks
            WHERE id = ?
            """,
            (chunk_id,)
        )

        conn.commit()

        return cursor.rowcount > 0
    finally:
        conn.close()


def insert_two_chunks(
        simulate_error: bool = False
) -> None:
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO knowledge_chunks
                (content, source, section)
                VALUES (?, ?, ?)
            """,
            (
                "文件保存在服务端本地目录中。",
                "knowledge.md",
                "文件共享"
            )
        )
        if simulate_error:
            raise RuntimeError("模拟第二次插入前发生异常")

        cursor.execute(
            """
            INSERT INTO knowledge_chunks
                (content, source, section)
                VALUES (?, ?, ?)
            """,
            (
                "二维码中保存的是访问地址。",
                "knowledge.md",
                "访问方式"
            )
        )
        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def find_chunks_by_section(
        section: str
) -> list[sqlite3.Row]:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
            id, content, source, section, created_at 
            FROM knowledge_chunks
            WHERE section = ?
            """,
            (section,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def main():
    create_table()

    chunks = find_all_chunks()
    print(f"当前记录数量:{len(chunks)}")

    for chunk in chunks:
        print(
            f"ID:{chunk[0]},"
            f"内容:{chunk[1]}"
        )


if __name__ == "__main__":
    main()
