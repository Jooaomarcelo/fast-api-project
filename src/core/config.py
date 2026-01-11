from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str
    port: int
    env: str
    jwt_secret: str
    jwt_expiration: str

    class Config:
        env_file = ".env"


settings = Settings()
