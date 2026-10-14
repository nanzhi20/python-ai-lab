from pathlib import Path


def load_document(file_path: str | Path) -> str:
    path = Path(file_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(f"知识文档不存在:{path}")

    content = path.read_text(encoding="utf-8").strip()

    if(not content):
        raise ValueError(f"知识文档为空:{path}")

    return content