from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import String, Integer, DateTime, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.database import Base
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .atendimento import Atendimento
    from .prontuario import Prontuario


class Paciente(Base):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    dataNascimento: Mapped[date] = mapped_column(Date, nullable=False)
    statusAtendimento: Mapped[str] = mapped_column(String(50), nullable=False, default="Aguardando Triagem", server_default="Aguardando Triagem")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relacionamentos conforme diagrama
    atendimentos: Mapped[List["Atendimento"]] = relationship("Atendimento", back_populates="paciente")
    prontuario: Mapped[Optional["Prontuario"]] = relationship("Prontuario", back_populates="paciente", uselist=False)