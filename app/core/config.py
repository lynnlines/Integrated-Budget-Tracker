from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    app_port: int = 8000
    enable_docs: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    trusted_hosts: str = "*"
    https_redirect: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")

    @property
    def docs_url_final(self) -> Optional[str]:
        return self.docs_url if self.enable_docs else None

    @property
    def redoc_url_final(self) -> Optional[str]:
        return self.redoc_url if self.enable_docs else None

    @property
    def openapi_url_final(self) -> Optional[str]:
        return self.openapi_url if self.enable_docs else None

    @property
    def allowed_hosts(self) -> Optional[List[str]]:
        if self.trusted_hosts == "*" or not self.trusted_hosts.strip():
            return None
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]


settings = Settings()
