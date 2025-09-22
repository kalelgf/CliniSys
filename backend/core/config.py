from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    app_name: str = "INE5608_CliniSys"
    secret_key: str = "chave-misteriosa-troca-ja"
    access_token_expire_minutes: int = 30
    
    # URL do banco configurável - usando caminho absoluto baseado na localização do arquivo
    @property
    def database_url(self) -> str:
        # De backend/core/config.py subir 3 níveis para chegar a CliniSys/
        config_dir = os.path.dirname(os.path.abspath(__file__))  # backend/core
        backend_dir = os.path.dirname(config_dir)  # backend
        clinisys_dir = os.path.dirname(backend_dir)  # CliniSys
        db_path = os.path.join(clinisys_dir, "desktop", "clinisys_uc_admin.db")
        return f"sqlite+aiosqlite:///{db_path.replace(chr(92), '/')}"
    
    admin_email: str = "admin@clinisys.com"
    admin_password: str = "admin123"
    admin_cpf: str = "00000000000"  # CPF do admin padrão

    class Config:
        env_prefix = "APP_"
        case_sensitive = False


settings = Settings()
