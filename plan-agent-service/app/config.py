from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    agent_port: int = 8090
    spring_api_base: str = "http://localhost:8080"
    openai_api_key: str = ""
    openai_model: str = "deepseek-chat"
    openai_api_base: str = "https://api.deepseek.com"
    redis_url: str = "redis://localhost:6380/0"
    plan_max_revisions: int = 2
settings = Settings()
