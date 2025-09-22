"""
Inicialização do banco de dados - CliniSys Desktop
"""

import asyncio
from sqlalchemy import text

from .database import engine, AsyncSessionLocal
from ..models.usuario import UsuarioSistema


async def create_tables():
    """Cria as tabelas do banco de dados."""
    # Importar todos os modelos para garantir que estejam registrados
    from ..models import usuario
    
    async with engine.begin() as conn:
        # Criar todas as tabelas baseadas nos modelos
        from .database import Base
        await conn.run_sync(Base.metadata.create_all)


async def check_database():
    """Verifica se o banco de dados está funcionando."""
    try:
        async with AsyncSessionLocal() as session:
            # Tentar executar uma consulta simples
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception:
        return False


def create_tables_sync():
    """Versão síncrona para criar tabelas."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(create_tables())


def check_database_sync():
    """Versão síncrona para verificar banco."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(check_database())