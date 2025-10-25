"""
Repository de Usuários - CliniSys Desktop
Camada de acesso a dados pura - sem lógica de negócio
"""

from __future__ import annotations

import asyncio
from typing import List, Optional, Type, Union

from sqlalchemy import select, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models.usuario import UsuarioSistema
from ..models.administrador import Administrador
from ..models.recepcionista import Recepcionista
from ..models.professor import Professor
from ..models.aluno import Aluno
from ..db.database import AsyncSessionLocal
from ..db.init_db import create_tables_sync, check_database_sync, create_tables
from ..core.security_simple import hash_password


class UsuarioRepository:
    """
    Repository para acesso aos dados de usuários.
    Responsável apenas por operações CRUD sem validações de negócio.
    """

    @staticmethod
    async def get_by_cpf(db: AsyncSession, cpf: str) -> Optional[UsuarioSistema]:
        """Busca usuário por CPF."""
        stmt = select(UsuarioSistema).where(UsuarioSistema.cpf == cpf)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[UsuarioSistema]:
        """Busca usuário por email."""
        stmt = select(UsuarioSistema).where(UsuarioSistema.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[UsuarioSistema]:
        """Busca usuário por ID."""
        stmt = select(UsuarioSistema).where(UsuarioSistema.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_matricula(db: AsyncSession, matricula: str) -> Optional[UsuarioSistema]:
        """Busca usuário por matrícula (específico para alunos)."""
        from ..models.aluno import Aluno
        stmt = select(Aluno).where(Aluno.matricula == matricula)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_specific(
        db: AsyncSession, 
        user_class: Type[UsuarioSistema],
        *, 
        nome: str, 
        email: str, 
        cpf: str,
        senha_hash: str,
        ativo: bool = True,
        **kwargs
    ) -> UsuarioSistema:
        """Cria um novo usuário da classe específica."""
        # Dados básicos de usuário
        user_data = {
            "nome": nome,
            "email": email,
            "cpf": cpf,
            "senha_hash": senha_hash,
            "ativo": ativo
        }
        
        # Adicionar campos específicos da classe
        user_data.update(kwargs)
        
        user = user_class(**user_data)
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def list_all(db: AsyncSession) -> List[UsuarioSistema]:
        """Lista todos os usuários."""
        stmt = select(UsuarioSistema).order_by(UsuarioSistema.nome)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_alunos(
        db: AsyncSession,
        *,
        apenas_ativos: bool = True
    ) -> List[Aluno]:
        """Lista alunos (opcionalmente apenas os ativos)."""
        stmt = select(Aluno)
        if apenas_ativos:
            stmt = stmt.where(Aluno.ativo.is_(True))
        stmt = stmt.order_by(Aluno.nome.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_all_with_details(db: AsyncSession) -> List[dict]:
        """Lista todos os usuários com detalhes específicos por tipo - estrutura CliniSys original."""
        from ..models.aluno import Aluno
        from ..models.professor import Professor
        from ..models.recepcionista import Recepcionista
        from ..models.administrador import Administrador
        
        # Buscar todos os usuários base com joinedload para evitar lazy loading
        from sqlalchemy.orm import selectinload
        
        stmt = select(UsuarioSistema).order_by(UsuarioSistema.nome)
        result = await db.execute(stmt)
        users = list(result.scalars().all())
        
        users_with_details = []
        for user in users:
            # Fazer refresh na sessão para garantir acesso às propriedades
            await db.refresh(user)
            
            user_data = {
                "id": user.id,
                "nome": user.nome,
                "email": user.email,
                "cpf": user.cpf,
                "ativo": user.ativo,
                "tipo_usuario": user.tipo_usuario,
                "matricula": None,
                "telefone": None,
                "especialidade": None,
                "clinica_id": None
            }
            
            # Buscar dados específicos baseado no tipo usando polimorfismo
            try:
                if isinstance(user, Aluno):
                    user_data["matricula"] = user.matricula
                    user_data["telefone"] = user.telefone
                    user_data["clinica_id"] = user.clinica_id
                        
                elif isinstance(user, Professor):
                    user_data["especialidade"] = user.especialidade
                    user_data["clinica_id"] = user.clinica_id
                        
                elif isinstance(user, Recepcionista):
                    user_data["telefone"] = user.telefone
            except Exception as e:
                print(f"Erro ao acessar propriedades do usuário {user.id}: {e}")
                    
            users_with_details.append(user_data)
        
        return users_with_details

    @staticmethod
    async def update(
        db: AsyncSession,
        user_id: int,
        *,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        ativo: Optional[bool] = None,
        senha_hash: Optional[str] = None
    ) -> Optional[UsuarioSistema]:
        """Atualiza dados do usuário."""
        user = await UsuarioRepository.get_by_id(db, user_id)
        if not user:
            return None
        
        if nome is not None:
            user.nome = nome
        if email is not None:
            user.email = email
        if ativo is not None:
            user.ativo = ativo
        if senha_hash is not None:
            user.senha_hash = senha_hash
        
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_by_id(db: AsyncSession, user_id: int) -> bool:
        """Remove usuário por ID."""
        user = await UsuarioRepository.get_by_id(db, user_id)
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True

    @staticmethod
    async def set_active_status(db: AsyncSession, user_id: int, ativo: bool) -> Optional[UsuarioSistema]:
        """Ativa/desativa usuário."""
        return await UsuarioRepository.update(db, user_id, ativo=ativo)

    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, nova_senha_hash: str) -> Optional[UsuarioSistema]:
        """Altera senha do usuário."""
        return await UsuarioRepository.update(db, user_id, senha_hash=nova_senha_hash)

    @staticmethod
    async def create_default_admin(db: AsyncSession):
        """Cria usuário admin padrão se não existir."""
        from ..core.config import settings
        admin_user = await UsuarioRepository.get_by_email(db, settings.admin_email)
        if not admin_user:
            admin_password_hash = hash_password(settings.admin_password)
            await UsuarioRepository.create_specific(
                db,
                user_class=Administrador,
                nome="Administrador",
                email=settings.admin_email,
                cpf=settings.admin_cpf,
                senha_hash=admin_password_hash,
                ativo=True
            )


# ===================== Funções Síncronas (Desktop Wrappers) ===================== #

def run_async(coro):
    """Executa função assíncrona de forma síncrona."""
    # Sempre usar asyncio.run para criar um novo event loop limpo
    return asyncio.run(coro)


def create_user_specific_sync(
    user_class: Type[UsuarioSistema], 
    nome: str, 
    email: str, 
    cpf: str, 
    senha: str, 
    **kwargs
) -> UsuarioSistema:
    """Versão síncrona de create_user_specific."""
    async def _create():
        async with AsyncSessionLocal() as db:
            senha_hash = hash_password(senha)
            return await UsuarioRepository.create_specific(
                db, 
                user_class=user_class,
                nome=nome, 
                email=email, 
                cpf=cpf, 
                senha_hash=senha_hash,
                **kwargs
            )
    
    return run_async(_create())


def list_users_sync() -> List[UsuarioSistema]:
    """Versão síncrona de list_users."""
    async def _list():
        async with AsyncSessionLocal() as db:
            return await UsuarioRepository.list_all(db)
    
    return run_async(_list())


def list_users_with_details_sync() -> List[dict]:
    """Versão síncrona de list_users_with_details."""
    async def _list():
        async with AsyncSessionLocal() as db:
            return await UsuarioRepository.list_all_with_details(db)
    
    return run_async(_list())


def list_alunos_sync(apenas_ativos: bool = True) -> List[dict]:
    """Versão síncrona de list_alunos."""

    async def _list():
        async with AsyncSessionLocal() as db:
            alunos = await UsuarioRepository.list_alunos(db, apenas_ativos=apenas_ativos)
            return [
                {
                    "id": aluno.id,
                    "nome": aluno.nome,
                    "matricula": getattr(aluno, "matricula", None),
                    "cpf": aluno.cpf,
                    "clinica_id": getattr(aluno, "clinica_id", None),
                }
                for aluno in alunos
            ]

    return run_async(_list())


def get_user_by_id_sync(user_id: int) -> Optional[dict]:
    """Versão síncrona de get_user_by_id. Retorna dicionário com dados do usuário."""
    async def _get():
        async with AsyncSessionLocal() as db:
            user = await UsuarioRepository.get_by_id(db, user_id)
            if user:
                # Converter para dicionário para evitar problemas de sessão
                user_dict = {
                    'id': user.id,
                    'nome': user.nome,
                    'cpf': user.cpf,
                    'email': user.email,
                    'tipo': user.__class__.__name__,
                    'clinica_id': getattr(user, 'clinica_id', None)
                }
                return user_dict
            return None
    
    return run_async(_get())


def get_user_by_cpf_sync(cpf: str) -> Optional[UsuarioSistema]:
    """Versão síncrona de get_user_by_cpf."""
    async def _get():
        async with AsyncSessionLocal() as db:
            return await UsuarioRepository.get_by_cpf(db, cpf)
    
    return run_async(_get())


def get_user_by_email_sync(email: str) -> Optional[UsuarioSistema]:
    """Versão síncrona de get_user_by_email."""
    async def _get():
        async with AsyncSessionLocal() as db:
            return await UsuarioRepository.get_by_email(db, email)
    
    return run_async(_get())


def update_user_sync(
    user_id: int,
    nome: Optional[str] = None,
    email: Optional[str] = None,
    tipo_usuario: Optional[str] = None,
    **kwargs
) -> Optional[UsuarioSistema]:
    """Versão síncrona de update_user."""
    async def _update():
        async with AsyncSessionLocal() as db:
            # Por enquanto, apenas atualiza campos básicos
            # TODO: Implementar atualização de campos específicos por tipo
            return await UsuarioRepository.update(db, user_id, nome=nome, email=email)
    
    return run_async(_update())


def delete_user_sync(user_id: int) -> bool:
    """Versão síncrona de delete_user."""
    async def _delete():
        async with AsyncSessionLocal() as db:
            return await UsuarioRepository.delete_by_id(db, user_id)
    
    return run_async(_delete())


def set_user_active_sync(user_id: int, ativo: bool) -> Optional[UsuarioSistema]:
    """Versão síncrona de set_user_active."""
    async def _set_active():
        async with AsyncSessionLocal() as db:
            return await UsuarioRepository.set_active_status(db, user_id, ativo)
    
    return run_async(_set_active())


def change_user_password_sync(user_id: int, nova_senha: str) -> Optional[UsuarioSistema]:
    """Versão síncrona de change_user_password."""
    async def _change_password():
        async with AsyncSessionLocal() as db:
            nova_senha_hash = hash_password(nova_senha)
            return await UsuarioRepository.change_password(db, user_id, nova_senha_hash)
    
    return run_async(_change_password())


def get_user_by_matricula_sync(matricula: str) -> Optional[UsuarioSistema]:
    """Versão síncrona para buscar usuário por matrícula."""
    async def _get_by_matricula():
        async with AsyncSessionLocal() as db:
            return await UsuarioRepository.get_by_matricula(db, matricula)
    
    return run_async(_get_by_matricula())


def init_db_and_seed_sync():
    """Versão síncrona de init_db_and_seed."""
    try:
        # Criar tabelas primeiro (versão síncrona)
        create_tables_sync()
        
        # Depois criar usuário admin usando versão síncrona
        return asyncio.run(_create_admin_only())
    except Exception as e:
        print(f"Erro na inicialização: {e}")
        raise


async def _create_admin_only():
    """Função interna para criar apenas o admin."""
    async with AsyncSessionLocal() as db:
        await UsuarioRepository.create_default_admin(db)