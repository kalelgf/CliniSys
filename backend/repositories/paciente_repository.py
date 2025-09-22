"""
Repository de Pacientes - CliniSys Desktop
Camada de acesso a dados pura - sem lógica de negócio
"""

from __future__ import annotations

import asyncio
from typing import List, Optional
from datetime import date

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models.paciente import Paciente
from ..db.database import AsyncSessionLocal


class PacienteRepository:
    """
    Repository para acesso aos dados de pacientes.
    Responsável apenas por operações CRUD sem validações de negócio.
    """

    @staticmethod
    async def get_by_cpf(db: AsyncSession, cpf: str) -> Optional[Paciente]:
        """Busca paciente por CPF."""
        stmt = select(Paciente).where(Paciente.cpf == cpf)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, patient_id: int) -> Optional[Paciente]:
        """Busca paciente por ID."""
        stmt = select(Paciente).where(Paciente.id == patient_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession, 
        *, 
        nome: str, 
        cpf: str, 
        data_nascimento: date,
        status_atendimento: str = "Aguardando Triagem"
    ) -> Paciente:
        """Cria um novo paciente."""
        patient = Paciente(
            nome=nome,
            cpf=cpf,
            dataNascimento=data_nascimento,
            statusAtendimento=status_atendimento
        )
        
        db.add(patient)
        await db.commit()
        await db.refresh(patient)
        return patient

    @staticmethod
    async def list_all(db: AsyncSession) -> List[Paciente]:
        """Lista todos os pacientes."""
        stmt = select(Paciente).order_by(Paciente.nome)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        patient_id: int,
        *,
        nome: Optional[str] = None,
        status_atendimento: Optional[str] = None
    ) -> Optional[Paciente]:
        """Atualiza dados do paciente."""
        patient = await PacienteRepository.get_by_id(db, patient_id)
        if not patient:
            return None
        
        if nome is not None:
            patient.nome = nome
        if status_atendimento is not None:
            patient.statusAtendimento = status_atendimento
        
        await db.commit()
        await db.refresh(patient)
        return patient

    @staticmethod
    async def delete_by_id(db: AsyncSession, patient_id: int) -> bool:
        """Remove paciente por ID."""
        patient = await PacienteRepository.get_by_id(db, patient_id)
        if not patient:
            return False
        
        await db.delete(patient)
        await db.commit()
        return True


# ===================== Funções Síncronas (Desktop Wrappers) ===================== #

def run_async(coro):
    """Executa função assíncrona de forma síncrona."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Se o loop já está rodando, executar em uma task separada
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # Criar novo loop se necessário
        return asyncio.run(coro)


def create_patient_sync(nome: str, cpf: str, data_nascimento: date) -> Paciente:
    """Versão síncrona de create_patient."""
    async def _create():
        async with AsyncSessionLocal() as db:
            return await PacienteRepository.create(
                db, 
                nome=nome, 
                cpf=cpf, 
                data_nascimento=data_nascimento
            )
    
    return run_async(_create())


def list_patients_sync() -> List[Paciente]:
    """Versão síncrona de list_patients."""
    async def _list():
        async with AsyncSessionLocal() as db:
            return await PacienteRepository.list_all(db)
    
    return run_async(_list())


def get_patient_by_id_sync(patient_id: int) -> Optional[Paciente]:
    """Versão síncrona de get_patient_by_id."""
    async def _get():
        async with AsyncSessionLocal() as db:
            return await PacienteRepository.get_by_id(db, patient_id)
    
    return run_async(_get())


def get_patient_by_cpf_sync(cpf: str) -> Optional[Paciente]:
    """Versão síncrona de get_patient_by_cpf."""
    async def _get():
        async with AsyncSessionLocal() as db:
            return await PacienteRepository.get_by_cpf(db, cpf)
    
    return run_async(_get())


def update_patient_sync(
    patient_id: int,
    nome: Optional[str] = None,
    status_atendimento: Optional[str] = None
) -> Optional[Paciente]:
    """Versão síncrona de update_patient."""
    async def _update():
        async with AsyncSessionLocal() as db:
            return await PacienteRepository.update(db, patient_id, nome=nome, status_atendimento=status_atendimento)
    
    return run_async(_update())


def delete_patient_sync(patient_id: int) -> bool:
    """Versão síncrona de delete_patient."""
    async def _delete():
        async with AsyncSessionLocal() as db:
            return await PacienteRepository.delete_by_id(db, patient_id)
    
    return run_async(_delete())