
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .paciente import Paciente
    from .procedimento import Procedimento


class Prontuario(Base):
    """
    Modelo para Prontuário.
    """
    __tablename__ = "prontuarios"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Relacionamento com Paciente (1:1)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), nullable=False, unique=True)
    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="prontuario")
    
    # Relacionamento com Procedimento (1:1)
    procedimento_id: Mapped[int] = mapped_column(Integer, ForeignKey("procedimentos.id"), nullable=False, unique=True)
    procedimento: Mapped["Procedimento"] = relationship("Procedimento")
    
    def __repr__(self):
        return f"<Prontuario(id={self.id}, codigo='{self.codigo}')>"