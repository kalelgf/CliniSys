
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .usuario import UsuarioSistema


class Recepcionista(UsuarioSistema):
    """
    Modelo para Recepcionista.
    Herda de UsuarioSistema e adiciona telefone.
    """
    __tablename__ = "recepcionistas"
    
    id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios_sistema.id"), primary_key=True)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Configuração de herança
    __mapper_args__ = {
        "polymorphic_identity": "recepcionista"
    }
    
    def __init__(self, nome: str, email: str, senha_hash: str, cpf: str, telefone: str = "", **kwargs):
        """Inicializa uma Recepcionista."""
        super().__init__(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            cpf=cpf,
            tipo_usuario="recepcionista",
            **kwargs
        )
        self.telefone = telefone
    
    def __repr__(self):
        return f"<Recepcionista(id={self.id}, nome='{self.nome}', telefone='{self.telefone}')>"