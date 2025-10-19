"""
Repository de Consultas/Atendimentos - CliniSys Desktop
Camada de acesso a dados pura para operações de agendamento
"""

from __future__ import annotations

import asyncio
from typing import Optional
from datetime import datetime

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models.atendimento import Atendimento
from ..db.database import AsyncSessionLocal


class ConsultaRepository:
    """
    Repository para acesso aos dados de atendimentos/consultas.
    Responsável apenas por operações CRUD sem validações de negócio.
    """

    @staticmethod
    async def verificar_disponibilidade(
        db: AsyncSession,
        aluno_id: int,
        paciente_id: int,
        data_hora: datetime
    ) -> bool:
        """
        Verifica se o horário está disponível para o aluno E para o paciente.
        Retorna True se disponível, False se houver conflito.
        """
        # Consulta para verificar se já existe atendimento no mesmo horário
        # para o aluno OU para o paciente
        stmt = select(func.count(Atendimento.id)).where(
            and_(
                Atendimento.dataHora == data_hora,
                (
                    (Atendimento.aluno_id == aluno_id) |
                    (Atendimento.paciente_id == paciente_id)
                )
            )
        )
        
        result = await db.execute(stmt)
        count = result.scalar()
        
        # Retorna True se count == 0 (horário livre)
        return count == 0

    @staticmethod
    async def salvar(db: AsyncSession, atendimento: Atendimento) -> Atendimento:
        """
        Salva um novo atendimento no banco de dados.
        """
        try:
            db.add(atendimento)
            await db.commit()
            await db.refresh(atendimento)
            return atendimento
        except IntegrityError as e:
            await db.rollback()
            raise Exception(f"Erro ao salvar atendimento: {str(e)}")

    @staticmethod
    async def get_by_id(db: AsyncSession, atendimento_id: int) -> Optional[Atendimento]:
        """Busca atendimento por ID."""
        stmt = select(Atendimento).where(Atendimento.id == atendimento_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def listar_por_aluno(db: AsyncSession, aluno_id: int) -> list[Atendimento]:
        """Lista todos os atendimentos de um aluno."""
        stmt = select(Atendimento).where(Atendimento.aluno_id == aluno_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def listar_por_paciente(db: AsyncSession, paciente_id: int) -> list[Atendimento]:
        """Lista todos os atendimentos de um paciente."""
        stmt = select(Atendimento).where(Atendimento.paciente_id == paciente_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def verificar_paciente_tem_agendamento_no_dia(
        db: AsyncSession,
        paciente_id: int,
        data: datetime
    ) -> bool:
        """
        Verifica se o paciente já tem algum agendamento no dia especificado.
        Retorna True se já existe agendamento, False caso contrário.
        """
        from sqlalchemy import func, cast, Date
        
        # Extrair apenas a data (sem horário) para comparação
        data_apenas = data.date()
        
        print(f"[DEBUG] Verificando agendamentos para paciente_id={paciente_id}, data={data_apenas}")
        
        # Forçar leitura direta do banco (sem cache)
        await db.flush()  # Garante que todas as mudanças pendentes sejam escritas
        
        # Debug: Listar TODOS os atendimentos deste paciente
        stmt_debug = select(Atendimento).where(Atendimento.paciente_id == paciente_id)
        result_debug = await db.execute(stmt_debug)
        todos_atendimentos = result_debug.scalars().all()
        print(f"[DEBUG] Total de atendimentos do paciente {paciente_id}: {len(todos_atendimentos)}")
        for atend in todos_atendimentos:
            print(f"  - ID {atend.id}: {atend.dataHora} (data: {atend.dataHora.date()})")
        
        # Consulta para verificar se já existe atendimento no mesmo dia
        # Usando Date do SQLite diretamente para garantir comparação correta
        stmt = select(func.count(Atendimento.id)).where(
            and_(
                Atendimento.paciente_id == paciente_id,
                func.date(Atendimento.dataHora) == data_apenas
            )
        )
        
        result = await db.execute(stmt)
        count = result.scalar()
        
        print(f"[DEBUG] Encontrados {count} agendamentos no dia {data_apenas}")
        
        # Retorna True se count > 0 (já tem agendamento)
        return count > 0


# ===================== Versões Síncronas para Desktop ===================== #

def verificar_disponibilidade_sync(
    aluno_id: int,
    paciente_id: int,
    data_hora: datetime
) -> bool:
    """Versão síncrona de verificar_disponibilidade."""
    async def _async_wrapper():
        async with AsyncSessionLocal() as db:
            return await ConsultaRepository.verificar_disponibilidade(
                db, aluno_id, paciente_id, data_hora
            )
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_async_wrapper())


def salvar_sync(atendimento: Atendimento) -> Atendimento:
    """Versão síncrona de salvar."""
    async def _async_wrapper():
        async with AsyncSessionLocal() as db:
            return await ConsultaRepository.salvar(db, atendimento)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_async_wrapper())


def get_by_id_sync(atendimento_id: int) -> Optional[Atendimento]:
    """Versão síncrona de get_by_id."""
    async def _async_wrapper():
        async with AsyncSessionLocal() as db:
            return await ConsultaRepository.get_by_id(db, atendimento_id)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_async_wrapper())


def listar_por_aluno_sync(aluno_id: int) -> list[Atendimento]:
    """Versão síncrona de listar_por_aluno."""
    async def _async_wrapper():
        async with AsyncSessionLocal() as db:
            return await ConsultaRepository.listar_por_aluno(db, aluno_id)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_async_wrapper())


def listar_por_paciente_sync(paciente_id: int) -> list[Atendimento]:
    """Versão síncrona de listar_por_paciente."""
    async def _async_wrapper():
        async with AsyncSessionLocal() as db:
            return await ConsultaRepository.listar_por_paciente(db, paciente_id)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_async_wrapper())


def verificar_paciente_tem_agendamento_no_dia_sync(
    paciente_id: int,
    data: datetime
) -> bool:
    """Versão síncrona de verificar_paciente_tem_agendamento_no_dia."""
    async def _async_wrapper():
        async with AsyncSessionLocal() as db:
            return await ConsultaRepository.verificar_paciente_tem_agendamento_no_dia(
                db, paciente_id, data
            )
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_async_wrapper())
