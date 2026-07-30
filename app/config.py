from pydantic_settings import BaseSettings
 
 
class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/jobmatch"
    jwt_secret: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours
 
    class Config:
        env_file = ".env"
 
 
settings = Settings()