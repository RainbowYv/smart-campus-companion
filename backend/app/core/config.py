"""配置管理模块"""
from pathlib import Path
from typing import List

from pydantic import computed_field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # 应用基本配置
    app_name: str = "smart-campus-companion"
    app_version: str = "1.0.0"
    debug: bool = False

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM配置 (从环境变量读取)
    llm_api_key: str = ""
    llm_base_url: str = "https://api-inference.modelscope.cn/v1/"
    llm_model: str = "Qwen/Qwen2.5-32B-Instruct"
    llm_timeout: int = 60
    max_tokens: int = 4096
    temperature: float = 0.7

    # 嵌入模型
    embedding_model: str = "nomic-embed-text"
    embedding_base_url: str = "http://localhost:11434"
    embedding_type: str = "ollama"
    embedding_api_key: str

    # LangSmit配置
    langchain_api_key: str = ""
    langchain_tracing_v2: bool = True
    langchain_project: str = "smart-campus-companion"

    # Mysql配置
    mysql_name: str = "root"
    mysql_password: str
    mysql_port: int = 3306
    database_name: str = "smart_campus_companion"

    # Redis配置
    redis_password: str = None
    redis_cache_expire: int = 3600
    redis_port: int = 6379

    # Qdrant配置
    qdrant_port: int = 6333
    qdrant_api_key: str

    # CORS配置 - 使用字符串,在代码中分割
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    def get_cors_origins_list(self) -> List[str]:
        """获取CORS origins列表"""
        return [origin.strip() for origin in self.cors_origins.split(',')]

    @computed_field
    @property
    def mysql_url(self) -> str:
        return f"mysql+aiomysql://{self.mysql_name}:{self.mysql_password}@localhost:{self.mysql_port}/{self.database_name}"

    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://localhost:{self.redis_port}"

    @computed_field
    @property
    def qdrant_url(self) -> str:
        return f"http://localhost:{self.qdrant_port}"

    # 日志配置
    log_level: str = "INFO"

    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


_settings = None


def get_settings() -> Settings:
    """获取配置实例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
