
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ..db.database import Base
from datetime import datetime


class Procedimento(Base):
    """
    Modelo para Procedimento.
    """
    __tablename__ = "procedimentos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(String(500), nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Procedimento(id={self.id}, codigo='{self.codigo}', descricao='{self.descricao}')>"