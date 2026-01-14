from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str
    port: int
    env: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_expiration_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
