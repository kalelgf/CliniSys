
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.database import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .professor import Professor
    from .aluno import Aluno
    from .departamento import Departamento


class Clinica(Base):
    """
    Modelo para Clínica.
    """
    __tablename__ = "clinicas"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Relacionamentos
    alunos: Mapped[List["Aluno"]] = relationship("Aluno", back_populates="clinica")
    professores: Mapped[List["Professor"]] = relationship("Professor", back_populates="clinica")
    departamentos: Mapped[List["Departamento"]] = relationship("Departamento", back_populates="clinica")
    
    def __repr__(self):
        return f"<Clinica(id={self.id}, codigo='{self.codigo}', nome='{self.nome}')>"