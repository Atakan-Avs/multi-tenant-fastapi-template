from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "TaskEngine"
    env: str = "dev"
    database_url: str  # .envden gelcek
    
    jwt_secret_key: str = "CHANGE_ME_DEV_ONLY"
    jwt_algorithm: str = "HS256"
    jwt_access_token_exp_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()