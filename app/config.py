from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = 8080
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "password"
    db_name: str = "sns_camp"
    jwt_secret: str = "your-secret-key-change-in-production"
    allowed_origins: str = "http://localhost:3000"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            "?charset=utf8mb4"
        )

    @property
    def database_url_without_db(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}"
            "?charset=utf8mb4"
        )


settings = Settings()
