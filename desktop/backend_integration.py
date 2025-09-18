"""Integração com Backend FastAPI.

Este módulo fornece funções síncronas que fazem chamadas HTTP
para o backend FastAPI, encapsulando a complexidade assíncrona
para uso nas interfaces Tkinter.
"""
from __future__ import annotations

import json
import requests
import threading
from datetime import date, datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .config import BACKEND_BASE_URL, HTTP_TIMEOUT, get_auth_headers


# ===================== Exceções ===================== #
class BackendError(Exception):
    """Erro genérico do backend."""
    pass


class ValidationError(BackendError):
    """Erro de validação de dados."""
    pass


class AuthenticationError(BackendError):
    """Erro de autenticação."""
    pass


class ConflictError(BackendError):
    """Erro de conflito (ex: CPF duplicado)."""
    pass


# ===================== Data Classes ===================== #
@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    perfil: str
    ativo: bool = True
    created_at: Optional[str] = None


@dataclass
class Paciente:
    id: int
    nome: str
    cpf: str
    data_nascimento: str  # Como string para simplificar UI
    status_atendimento: str
    created_at: Optional[str] = None


# ===================== Cliente HTTP ===================== #
class BackendClient:
    """Cliente HTTP para comunicação com o backend FastAPI."""
    
    def __init__(self, base_url: str = BACKEND_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = HTTP_TIMEOUT
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Faz requisição HTTP e trata erros comuns."""
        url = f"{self.base_url}{endpoint}"
        headers = get_auth_headers()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            # Trata códigos de erro HTTP
            if response.status_code == 400:
                error_detail = response.json().get('detail', 'Erro de validação')
                raise ValidationError(error_detail)
            elif response.status_code == 401:
                raise AuthenticationError("Não autorizado")
            elif response.status_code == 403:
                raise AuthenticationError("Acesso negado")
            elif response.status_code == 409:
                error_detail = response.json().get('detail', 'Conflito')
                raise ConflictError(error_detail)
            elif response.status_code >= 400:
                error_detail = response.json().get('detail', f'Erro HTTP {response.status_code}')
                raise BackendError(f"Erro do servidor: {error_detail}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise BackendError("Não foi possível conectar ao servidor. Verifique se o backend está rodando.")
        except requests.exceptions.Timeout:
            raise BackendError("Timeout na requisição.")
        except requests.exceptions.RequestException as e:
            raise BackendError(f"Erro na requisição: {str(e)}")
    
    # =============== Métodos de Usuários =============== #
    def criar_usuario(self, nome: str, email: str, senha: str, perfil: str) -> Usuario:
        """Cria um novo usuário."""
        data = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "perfil": perfil
        }
        
        response = self._make_request("POST", "/usuarios/", json=data)
        user_data = response["data"]
        
        return Usuario(
            id=user_data["id"],
            nome=user_data["nome"],
            email=user_data["email"],
            perfil=user_data["perfil"],
            ativo=user_data.get("ativo", True),
            created_at=user_data.get("created_at")
        )
    
    def listar_usuarios(self, skip: int = 0, limit: int = 50, perfil: Optional[str] = None) -> List[Usuario]:
        """Lista usuários com filtros opcionais."""
        params = {"skip": skip, "limit": limit}
        if perfil:
            params["perfil"] = perfil
        
        response = self._make_request("GET", "/usuarios/", params=params)
        users_data = response["data"]
        
        return [
            Usuario(
                id=user["id"],
                nome=user["nome"],
                email=user["email"],
                perfil=user["perfil"],
                ativo=user.get("ativo", True),
                created_at=user.get("created_at")
            )
            for user in users_data
        ]
    
    # =============== Métodos de Pacientes =============== #
    def criar_paciente(self, nome: str, cpf: str, data_nascimento: str) -> Paciente:
        """Cria um novo paciente na fila de triagem usando endpoint público."""
        # Converte data string DD/MM/AAAA para formato ISO (AAAA-MM-DD)
        try:
            day, month, year = data_nascimento.split('/')
            iso_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except ValueError:
            raise ValidationError("Data deve estar no formato DD/MM/AAAA")
        
        data = {
            "nome": nome,
            "cpf": cpf,
            "dataNascimento": iso_date
        }
        
        response = self._make_request("POST", "/pacientes/publico", json=data)
        patient_data = response["data"]
        
        # Converte data de volta para formato brasileiro
        iso_date = patient_data["dataNascimento"]
        br_date = datetime.fromisoformat(iso_date).strftime("%d/%m/%Y")
        
        return Paciente(
            id=patient_data["id"],
            nome=patient_data["nome"],
            cpf=patient_data["cpf"],
            data_nascimento=br_date,
            status_atendimento=patient_data["statusAtendimento"],
            created_at=patient_data.get("created_at")
        )
    
    def listar_fila_triagem(self, skip: int = 0, limit: int = 50) -> List[Paciente]:
        """Lista pacientes na fila de triagem."""
        params = {"skip": skip, "limit": limit}
        
        response = self._make_request("GET", "/pacientes/fila-triagem", params=params)
        patients_data = response["data"]
        
        result = []
        for patient in patients_data:
            # Converte data para formato brasileiro
            iso_date = patient["dataNascimento"]
            br_date = datetime.fromisoformat(iso_date).strftime("%d/%m/%Y")
            
            result.append(Paciente(
                id=patient["id"],
                nome=patient["nome"],
                cpf=patient["cpf"],
                data_nascimento=br_date,
                status_atendimento=patient["statusAtendimento"],
                created_at=patient.get("created_at")
            ))
        
        return result


# ===================== Instância Global ===================== #
# Cliente singleton para reutilização
_client = BackendClient()


# ===================== Funções de Alto Nível ===================== #
def sync_call(func, *args, **kwargs):
    """Executa função em thread separada para não bloquear a UI."""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join()
    
    if exception[0]:
        raise exception[0]
    
    return result[0]


# =============== API Simplificada para UI =============== #
def criar_usuario_sync(nome: str, email: str, senha: str, perfil: str) -> Usuario:
    """Versão síncrona para criar usuário."""
    return sync_call(_client.criar_usuario, nome, email, senha, perfil)


def listar_usuarios_sync(skip: int = 0, limit: int = 50, perfil: Optional[str] = None) -> List[Usuario]:
    """Versão síncrona para listar usuários."""
    return sync_call(_client.listar_usuarios, skip, limit, perfil)


def criar_paciente_sync(nome: str, cpf: str, data_nascimento: str) -> Paciente:
    """Versão síncrona para criar paciente."""
    return sync_call(_client.criar_paciente, nome, cpf, data_nascimento)


def listar_fila_triagem_sync(skip: int = 0, limit: int = 50) -> List[Paciente]:
    """Versão síncrona para listar fila de triagem."""
    return sync_call(_client.listar_fila_triagem, skip, limit)


# =============== Utilitários =============== #
def test_connection() -> bool:
    """Testa se o backend está respondendo."""
    try:
        from .config import BACKEND_DOCS_URL
        response = requests.get(BACKEND_DOCS_URL, timeout=5)
        return response.status_code == 200
    except:
        try:
            # Fallback para testar diretamente
            response = requests.get(f"http://localhost:8000/uc-admin/docs", timeout=5)
            return response.status_code == 200
        except:
            return False