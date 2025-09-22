"""
Módulo de integração simples para as telas desktop.
"""

from dataclasses import dataclass
from typing import Optional


# ===================== Exceptions ===================== #
class BackendError(Exception):
    """Erro geral de comunicação com backend"""
    pass


class ValidationError(BackendError):
    """Erro de validação dos dados"""
    pass


class ConflictError(BackendError):
    """Erro de conflito (ex: CPF duplicado)"""
    pass


# ===================== Models ===================== #
@dataclass
class Paciente:
    id: Optional[int] = None
    nome: str = ""
    cpf: str = ""
    data_nascimento: str = ""
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None


# ===================== Mock Functions ===================== #
def test_connection() -> bool:
    """Testa conexão com o backend"""
    return True


def criar_paciente_sync(nome: str, cpf: str, data_nascimento: str, **kwargs) -> Paciente:
    """
    Simula criação de paciente (versão mock para desenvolvimento)
    """
    # Validações básicas
    if not nome.strip():
        raise ValidationError("Nome é obrigatório")
    
    if not cpf.strip():
        raise ValidationError("CPF é obrigatório")
    
    if not data_nascimento.strip():
        raise ValidationError("Data de nascimento é obrigatória")
    
    # Simular criação bem-sucedida
    import random
    paciente = Paciente(
        id=random.randint(1000, 9999),
        nome=nome,
        cpf=cpf,
        data_nascimento=data_nascimento,
        **kwargs
    )
    
    return paciente