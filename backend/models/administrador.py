
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .usuario import UsuarioSistema


class Administrador(UsuarioSistema):
    """
    Modelo para Administrador.
    Herda de UsuarioSistema.
    """
    __tablename__ = "administradores"
    
    id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios_sistema.id"), primary_key=True)
    
    # Configuração de herança
    __mapper_args__ = {
        "polymorphic_identity": "administrador"
    }
    
    def __init__(self, nome: str, email: str, senha_hash: str, cpf: str, **kwargs):
        """Inicializa um Administrador."""
        super().__init__(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            cpf=cpf,
            tipo_usuario="administrador",
            **kwargs
        )
    
    def __repr__(self):
        return f"<Administrador(id={self.id}, nome='{self.nome}', email='{self.email}')>"