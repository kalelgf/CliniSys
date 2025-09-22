
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .aluno import Aluno
    from .paciente import Paciente


class Atendimento(Base):
    """
    Modelo para Atendimento.
    """
    __tablename__ = "atendimentos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataHora: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relacionamentos
    aluno_id: Mapped[int] = mapped_column(Integer, ForeignKey("alunos.id"), nullable=False)
    aluno: Mapped["Aluno"] = relationship("Aluno", back_populates="atendimentos")
    
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), nullable=False)
    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="atendimentos")
    
    def __repr__(self):
        return f"<Atendimento(id={self.id}, tipo='{self.tipo}', status='{self.status}')>"