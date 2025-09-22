from __future__ import annotations

import asyncio
from datetime import date, datetime
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Paciente, UsuarioSistema
from ..db.database import AsyncSessionLocal


# ============= Funções Assíncronas Originais =============

async def get_patient_by_cpf(db: AsyncSession, cpf: str) -> Paciente | None:
    stmt = select(Paciente).where(Paciente.cpf == cpf)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def check_cpf_exists_in_system(db: AsyncSession, cpf: str) -> bool:
    patient_stmt = select(Paciente.id).where(Paciente.cpf == cpf)
    patient_result = await db.execute(patient_stmt)
    
    if patient_result.scalar_one_or_none():
        return True
    
    return False


async def create_patient_async(db: AsyncSession, nome: str, cpf: str, data_nascimento: date) -> Paciente:
    """Cria um paciente no banco de dados (versão assíncrona)."""
    cpf_exists = await check_cpf_exists_in_system(db, cpf)
    if cpf_exists:
        raise ValueError("CPF já cadastrado no sistema.")
    
    new_patient = Paciente(
        nome=nome,
        cpf=cpf,
        dataNascimento=data_nascimento,
        statusAtendimento="Aguardando Triagem"
    )
    
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)
    
    return new_patient


async def list_patients_in_triage_async(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Paciente]:
    """Lista pacientes aguardando triagem (versão assíncrona)."""
    stmt = (
        select(Paciente)
        .where(Paciente.statusAtendimento == "Aguardando Triagem")
        .order_by(Paciente.created_at)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ============= Funções Síncronas =============

def _run_async(coro):
    """Helper para condições de corrida assíncronas de forma síncrona."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # Se já existe um loop rodando, usa thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return loop.run_until_complete(coro)


async def _create_patient_internal(nome: str, cpf: str, data_nascimento: date) -> Paciente:
    """Função interna para criar paciente."""
    async with AsyncSessionLocal() as db:
        return await create_patient_async(db, nome, cpf, data_nascimento)


async def _list_patients_internal(skip: int = 0, limit: int = 50) -> list[Paciente]:
    """Função interna para listar pacientes."""
    async with AsyncSessionLocal() as db:
        return await list_patients_in_triage_async(db, skip, limit)


async def _check_cpf_internal(cpf: str) -> bool:
    """Função interna para verificar CPF."""
    async with AsyncSessionLocal() as db:
        return await check_cpf_exists_in_system(db, cpf)


def create_patient(nome: str, cpf: str, data_nascimento: date) -> Paciente:
    """Cria um paciente no banco de dados (versão síncrona)."""
    return _run_async(_create_patient_internal(nome, cpf, data_nascimento))


def list_patients_in_triage(skip: int = 0, limit: int = 50) -> list[Paciente]:
    """Lista pacientes aguardando triagem (versão síncrona)."""
    return _run_async(_list_patients_internal(skip, limit))


def check_cpf_exists(cpf: str) -> bool:
    """Verifica se CPF já existe no sistema (versão síncrona)."""
    return _run_async(_check_cpf_internal(cpf))