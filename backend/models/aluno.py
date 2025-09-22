
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .usuario import UsuarioSistema
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .clinica import Clinica
    from .atendimento import Atendimento


class Aluno(UsuarioSistema):
    """
    Modelo para Aluno.
    Herda de UsuarioSistema e adiciona matrícula, telefone e clínica.
    """
    __tablename__ = "alunos"
    
    id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios_sistema.id"), primary_key=True)
    matricula: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    clinica_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clinicas.id"), nullable=True)
    
    # Relacionamentos
    clinica: Mapped["Clinica"] = relationship("Clinica", back_populates="alunos")
    atendimentos: Mapped[List["Atendimento"]] = relationship("Atendimento", back_populates="aluno")
    
    # Configuração de herança
    __mapper_args__ = {
        "polymorphic_identity": "aluno"
    }
    
    def __init__(self, nome: str, email: str, senha_hash: str, cpf: str, matricula: str = "", telefone: str = "", clinica_id: int | None = None, **kwargs):
        """Inicializa um Aluno."""
        super().__init__(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            cpf=cpf,
            tipo_usuario="aluno",
            **kwargs
        )
        self.matricula = matricula
        self.telefone = telefone
        self.clinica_id = clinica_id
    
    def __repr__(self):
        return f"<Aluno(id={self.id}, nome='{self.nome}', matricula='{self.matricula}')>"