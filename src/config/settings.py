import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_username: str = os.getenv("DATABASE_USERNAME")
    database_password: str = os.getenv("DATABASE_PASSWORD")
    database_host: str = os.getenv("DATABASE_HOST")
    database_port: str = os.getenv("DATABASE_PORT")
    database_name: str = os.getenv("DATABASE_NAME")


settings = Settings()
