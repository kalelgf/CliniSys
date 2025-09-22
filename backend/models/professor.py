
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .usuario import UsuarioSistema
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clinica import Clinica


class Professor(UsuarioSistema):
    """
    Modelo para Professor.
    Herda de UsuarioSistema e adiciona clínica e especialidade.
    """
    __tablename__ = "professores"
    
    id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios_sistema.id"), primary_key=True)
    especialidade: Mapped[str] = mapped_column(String(200), nullable=False)
    clinica_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clinicas.id"), nullable=True)
    
    # Relacionamentos
    clinica: Mapped["Clinica"] = relationship("Clinica", back_populates="professores")
    
    # Configuração de herança
    __mapper_args__ = {
        "polymorphic_identity": "professor"
    }
    
    def __init__(self, nome: str, email: str, senha_hash: str, cpf: str, especialidade: str = "", clinica_id: int | None = None, **kwargs):
        """Inicializa um Professor."""
        super().__init__(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            cpf=cpf,
            tipo_usuario="professor",
            **kwargs
        )
        self.especialidade = especialidade
        self.clinica_id = clinica_id
    
    def __repr__(self):
        return f"<Professor(id={self.id}, nome='{self.nome}', especialidade='{self.especialidade}')>"