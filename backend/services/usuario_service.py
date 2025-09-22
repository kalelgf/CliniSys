"""
Serviços de usuário
Funções síncronas e assíncronas para gerenciamento de usuários
"""

from __future__ import annotations

import asyncio
import re
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models.usuario import UsuarioSistema, PerfilUsuario
from ..db.database import AsyncSessionLocal
from ..core.security_simple import hash_password, verify_password


def validate_password_policy(senha: str) -> bool:
    """Valida se a senha atende aos requisitos mínimos."""
    if len(senha) < 8:
        return False
    if not re.search(r'[a-zA-Z]', senha):
        return False
    if not re.search(r'\d', senha):
        return False
    return True


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UsuarioSistema]:
    """Busca usuário por email."""
    stmt = select(UsuarioSistema).where(UsuarioSistema.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[UsuarioSistema]:
    """Busca usuário por ID."""
    stmt = select(UsuarioSistema).where(UsuarioSistema.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, 
    *, 
    nome: str, 
    email: str, 
    senha: str, 
    perfil: PerfilUsuario
) -> UsuarioSistema:
    """Cria um novo usuário."""
    if not validate_password_policy(senha):
        raise ValueError("Senha não atende aos requisitos mínimos (>=8, letra e dígito)")
    
    existing_user = await get_user_by_email(db, email)
    if existing_user:
        raise ValueError(f"Email {email} já está em uso")
    
    hashed_password = hash_password(senha)
    user = UsuarioSistema(
        nome=nome,
        email=email,
        senha_hash=hashed_password,
        perfil=perfil,
        ativo=True
    )
    
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"Email {email} já está em uso")


async def list_users(db: AsyncSession) -> List[UsuarioSistema]:
    """Lista todos os usuários."""
    stmt = select(UsuarioSistema).order_by(UsuarioSistema.nome)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_user(
    db: AsyncSession,
    user_id: int,
    *,
    nome: Optional[str] = None,
    email: Optional[str] = None,
    perfil: Optional[PerfilUsuario] = None
) -> UsuarioSistema:
    """Atualiza dados do usuário."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuário não encontrado")
    
    if email and email != user.email:
        existing_user = await get_user_by_email(db, email)
        if existing_user:
            raise ValueError(f"Email {email} já está em uso")
    
    if nome is not None:
        user.nome = nome
    if email is not None:
        user.email = email
    if perfil is not None:
        user.perfil = perfil
    
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise ValueError("Erro ao atualizar usuário")


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Remove usuário."""
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    await db.delete(user)
    await db.commit()
    return True


async def set_user_active(db: AsyncSession, user_id: int, ativo: bool) -> UsuarioSistema:
    """Ativa/desativa usuário."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuário não encontrado")
    
    user.ativo = ativo
    await db.commit()
    await db.refresh(user)
    return user


async def change_user_password(db: AsyncSession, user_id: int, nova_senha: str) -> UsuarioSistema:
    """Altera senha do usuário."""
    if not validate_password_policy(nova_senha):
        raise ValueError("Senha não atende aos requisitos mínimos")
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuário não encontrado")
    
    user.senha_hash = hash_password(nova_senha)
    await db.commit()
    await db.refresh(user)
    return user


async def init_db_and_seed(db: AsyncSession):
    """Inicializa banco e cria usuário admin se não existir."""
    admin_user = await get_user_by_email(db, "admin@clinisys.com")
    if not admin_user:
        await create_user(
            db,
            nome="Administrador",
            email="admin@clinisys.com",
            senha="admin123",
            perfil=PerfilUsuario.admin
        )


# ===================== Funções Síncronas ===================== #

def run_async(coro):
    """Executa função assíncrona de forma síncrona."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


def create_user_sync(nome: str, email: str, senha: str, perfil: PerfilUsuario) -> UsuarioSistema:
    """Versão síncrona de create_user."""
    async def _create():
        async with AsyncSessionLocal() as db:
            return await create_user(db, nome=nome, email=email, senha=senha, perfil=perfil)
    
    return run_async(_create())


def list_users_sync() -> List[UsuarioSistema]:
    """Versão síncrona de list_users."""
    async def _list():
        async with AsyncSessionLocal() as db:
            return await list_users(db)
    
    return run_async(_list())


def get_user_by_id_sync(user_id: int) -> Optional[UsuarioSistema]:
    """Versão síncrona de get_user_by_id."""
    async def _get():
        async with AsyncSessionLocal() as db:
            return await get_user_by_id(db, user_id)
    
    return run_async(_get())


def get_user_by_email_sync(email: str) -> Optional[UsuarioSistema]:
    """Versão síncrona de get_user_by_email."""
    async def _get():
        async with AsyncSessionLocal() as db:
            return await get_user_by_email(db, email)
    
    return run_async(_get())


def update_user_sync(
    user_id: int,
    nome: Optional[str] = None,
    email: Optional[str] = None,
    perfil: Optional[PerfilUsuario] = None
) -> UsuarioSistema:
    """Versão síncrona de update_user."""
    async def _update():
        async with AsyncSessionLocal() as db:
            return await update_user(db, user_id, nome=nome, email=email, perfil=perfil)
    
    return run_async(_update())


def delete_user_sync(user_id: int) -> bool:
    """Versão síncrona de delete_user."""
    async def _delete():
        async with AsyncSessionLocal() as db:
            return await delete_user(db, user_id)
    
    return run_async(_delete())


def set_user_active_sync(user_id: int, ativo: bool) -> UsuarioSistema:
    """Versão síncrona de set_user_active."""
    async def _set_active():
        async with AsyncSessionLocal() as db:
            return await set_user_active(db, user_id, ativo)
    
    return run_async(_set_active())


def change_user_password_sync(user_id: int, nova_senha: str) -> UsuarioSistema:
    """Versão síncrona de change_user_password."""
    async def _change_password():
        async with AsyncSessionLocal() as db:
            return await change_user_password(db, user_id, nova_senha)
    
    return run_async(_change_password())


def init_db_and_seed_sync():
    """Versão síncrona de init_db_and_seed."""
    async def _init():
        async with AsyncSessionLocal() as db:
            await init_db_and_seed(db)
    
    return run_async(_init())