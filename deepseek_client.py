from dataclasses import dataclass
from openai import OpenAI
from config import DeepSeekSettings


@dataclass(frozen=True)
class ChatResult:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class DeepSeekClient:
    _client: OpenAI
    _model: str
    def __init__(self, settings: DeepSeekSettings):
        self._client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=30.0
        )
        self._model = settings.model


    def chat(self, question: str) -> ChatResult:
        if not question or not question.strip():
            raise ValueError("问题不能为空!")
        question = question.strip()
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {'role': 'user', 'content': question}
            ])
        return ChatResult(
            content=response.choices[0].message.content,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens
        )