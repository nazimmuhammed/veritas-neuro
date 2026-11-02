from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# app/config.py -> parents[0]=app, [1]=backend, [2]=repo root (where .env lives)
ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    neo4j_user: str = "neo4j"
    neo4j_password: str
    neo4j_host: str = "localhost"
    neo4j_bolt_port: int = 7687

    qdrant_host: str = "localhost"
    qdrant_http_port: int = 6333

    redis_host: str = "localhost"
    redis_port: int = 6379

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def neo4j_uri(self) -> str:
        return f"bolt://{self.neo4j_host}:{self.neo4j_bolt_port}"


settings = Settings()
