from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI

from ..core.config import get_settings


class LLMBase:
    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            timeout: Optional[int] = None,
            **kwargs
    ):
        setting = get_settings()
        self.model = model or setting.llm_model
        self.temperature = temperature or setting.temperature
        self.max_tokens = max_tokens or setting.max_tokens
        self.timeout = timeout or setting.llm_timeout
        self.kwargs = kwargs
        self.api_key = api_key or setting.llm_api_key
        self.base_url = base_url or setting.llm_base_url
        self.client = self.__create_client()

    def __create_client(self) -> BaseChatModel:
        return ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )

