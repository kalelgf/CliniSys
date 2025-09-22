
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.database import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .clinica import Clinica


class Departamento(Base):
    """
    Modelo para Departamento.
    """
    __tablename__ = "departamentos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    clinica_id: Mapped[int] = mapped_column(Integer, ForeignKey("clinicas.id"), nullable=False)
    
    # Relacionamentos
    clinica: Mapped["Clinica"] = relationship("Clinica", back_populates="departamentos")
    
    def __repr__(self):
        return f"<Departamento(id={self.id}, nome='{self.nome}')>"