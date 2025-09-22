"""
Módulo de segurança simplificado para desktop
Usando hash simples temporariamente para resolver problemas com bcrypt
"""

import hashlib


def hash_password(password: str) -> str:
    """Hash simples da senha usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha usando hash simples."""
    return hash_password(plain) == hashed