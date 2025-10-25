
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
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
    procedimentosRealizados: Mapped[str | None] = mapped_column(Text, nullable=True)
    observacoesPosAtendimento: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relacionamentos
    # Permitir NULL quando aluno for excluído (SET NULL)
    aluno_id: Mapped[int | None] = mapped_column(
        Integer, 
        ForeignKey("alunos.id", ondelete="SET NULL"), 
        nullable=True
    )
    aluno: Mapped["Aluno | None"] = relationship("Aluno", back_populates="atendimentos")
    
    # Permitir NULL quando paciente for excluído (SET NULL)
    paciente_id: Mapped[int | None] = mapped_column(
        Integer, 
        ForeignKey("pacientes.id", ondelete="SET NULL"), 
        nullable=True
    )
    paciente: Mapped["Paciente | None"] = relationship("Paciente", back_populates="atendimentos")
    
    def __repr__(self):
        return f"<Atendimento(id={self.id}, tipo='{self.tipo}', status='{self.status}')>"