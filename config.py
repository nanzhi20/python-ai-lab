import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

@dataclass(frozen=True)
class DeepSeekSettings:
    api_key: str = field(repr=False)
    base_url: str
    model: str

def load_settings() -> DeepSeekSettings:
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if api_key is None or not api_key.strip() :
        raise ValueError("未配置DEEPSEEK_API_KEY")

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()

    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash").strip()

    return DeepSeekSettings(
        api_key = api_key,
        base_url = base_url,
        model = model
    )