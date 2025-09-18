"""Configuração para integração com backend FastAPI.

Este módulo centraliza as configurações de URL e outras opções
para facilitar modificações futuras.
"""

# URL base do backend FastAPI
BACKEND_BASE_URL = "http://localhost:8000/uc-admin"

# URL para testar conexão (docs)
BACKEND_DOCS_URL = "http://localhost:8000/uc-admin/docs"

# Timeout para requisições HTTP (segundos)
HTTP_TIMEOUT = 30

# Headers padrão
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Para autenticação futura (token JWT)
AUTH_TOKEN = None

def get_auth_headers():
    """Retorna headers com autenticação se disponível."""
    headers = DEFAULT_HEADERS.copy()
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    return headers