from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class HTTPConfig(BaseSettings):
    host: str = Field(default="localhost", alias="RETROWOT_HTTP_SERVER_HOST")
    port: int = Field(default=8000, alias="RETROWOT_HTTP_SERVER_PORT")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )
    http_server: HTTPConfig = Field(default_factory=HTTPConfig)


settings = Settings()

if __name__ == "__main__":
    settings = Settings()
    print(settings)
