from langchain_ollama import OllamaEmbeddings

from ..core.config import get_settings


class EmbeddingModelBase:
    def __init__(self):
        settings = get_settings()
        self.embedding_model = settings.embedding_model
        self.embedding_api_key = settings.embedding_api_key
        self.embedding_base_url = settings.embedding_base_url
        self.embedding_type = settings.embedding_type

    def get_model(self):
        if self.embedding_type == "ollama":
            return OllamaEmbeddings(base_url=self.embedding_base_url, model=self.embedding_model)
