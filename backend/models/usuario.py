from __future__ import annotations

import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.database import Base


class UsuarioSistema(Base):
    """
    Classe abstrata base para todos os usuários do sistema.
    """
    __tablename__ = "usuarios_sistema"
    
    def __new__(cls, *args, **kwargs):
        if cls is UsuarioSistema:
            raise TypeError(f"Cannot instantiate abstract class {cls.__name__}")
        return super().__new__(cls)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)  # CPF obrigatório conforme diagrama
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Discriminador para herança
    tipo_usuario: Mapped[str] = mapped_column(String(50), nullable=False)
    
    __mapper_args__ = {
        "polymorphic_on": tipo_usuario,
        "polymorphic_identity": "usuario_base"
    }
