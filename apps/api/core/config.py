from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql+asyncpg://kp:devpassword@localhost:5432/kindlepreneur'
    REDIS_URL: str = 'redis://localhost:6379'
    CLERK_SECRET_KEY: str = ''
    CLERK_PUBLISHABLE_KEY: str = ''
    LLM_PROVIDER: str = 'gemini'
    GEMINI_API_KEY: str = ''
    OPENAI_API_KEY: str = ''
    ANTHROPIC_API_KEY: str = ''
    STORAGE_BACKEND: str = 'local'
    LOCAL_STORAGE_PATH: str = './storage'
    S3_BUCKET: str = ''
    S3_ENDPOINT: str = ''
    AWS_ACCESS_KEY_ID: str = ''
    AWS_SECRET_ACCESS_KEY: str = ''
    FRONTEND_URL: str = 'http://localhost:3000'
    ENVIRONMENT: str = 'development'
    LOG_LEVEL: str = 'INFO'
    MAX_UPLOAD_SIZE_MB: int = 50
    DEFAULT_TOKEN_BUDGET: int = 100000
    DEFAULT_COST_BUDGET_USD: float = 5.0
    DEMO_MODE: bool = True  # if True and no Clerk key, use fixed tenant
    DEMO_TENANT_ID: str = 'demo-tenant-00000000'
    DEMO_USER_ID: str = 'demo-user-00000000'
    
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
