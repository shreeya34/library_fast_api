from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_username: str
    database_password: SecretStr
    database_name: str

    class Config:
        env_file = ".env"


settings = Settings()
