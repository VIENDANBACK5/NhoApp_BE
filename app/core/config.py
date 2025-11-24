import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from keycloak.keycloak_openid import KeycloakOpenID


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
    # Core settings
    PROJECT_NAME: str = "FASTAPI_BASE"
    SECRET_KEY: str
    API_PREFIX: str = "/api"
    API_VERSIONS: str = ""
    API_VERSION: str = "v1"
    BACKEND_CORS_ORIGINS: str = '["*"]'
    DEBUG: bool = False
    
    # Database settings - PostgreSQL (commented - not using)
    # POSTGRES_USER: str = "postgres"
    # POSTGRES_PASSWORD: str = "postgres"
    # POSTGRES_HOST: str = "db"
    # POSTGRES_PORT: int = 5432
    # POSTGRES_DB: str = "postgres"
    
    # Oracle Cloud settings
    ORACLE_USER: str = "APP_USER"
    ORACLE_PASSWORD: str = "MatKhauManh2025!!"
    ORACLE_DSN: str = "db1_high"
    ORACLE_WALLET_DIR: str = ""
    ORACLE_WALLET_PASSWORD: str = "MatKhauManh2025!!"
    
    # Security settings
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # Token expired after 7 days
    SECURITY_ALGORITHM: str = "HS256"
    LOGGING_CONFIG_FILE: str = os.path.join(BASE_DIR, "logging.ini")
    
    # Keycloak settings
    KEYCLOAK_SERVER_URL: Optional[str] = None
    KEYCLOAK_REALM: Optional[str] = None
    KEYCLOAK_CLIENT_ID: Optional[str] = None
    KEYCLOAK_CLIENT_SECRET: Optional[str] = None
    KEYCLOAK_VERIFY: bool = False
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    
    @property
    def DATABASE_URL(self) -> str:
        # PostgreSQL (commented - not using)
        # return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
        # Oracle Cloud
        return (
            f"oracle+oracledb://{self.ORACLE_USER}:{self.ORACLE_PASSWORD}@{self.ORACLE_DSN}"
            f"?config_dir={self.ORACLE_WALLET_DIR}&wallet_location={self.ORACLE_WALLET_DIR}&wallet_password={self.ORACLE_WALLET_PASSWORD}"
        )


settings = Settings()

if (
    settings.KEYCLOAK_SERVER_URL != None
    and settings.KEYCLOAK_REALM != None
    and settings.KEYCLOAK_CLIENT_ID != None
    and settings.KEYCLOAK_CLIENT_SECRET != None
    and settings.KEYCLOAK_VERIFY != None
):
    keycloak_openid = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER_URL,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        verify=settings.KEYCLOAK_VERIFY,
    )
else:
    keycloak_openid = None


def get_openid_config():
    if keycloak_openid == None:
        return {}
    return keycloak_openid.well_known()
