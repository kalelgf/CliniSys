"""Populate the local SQLite database with demo users and patients."""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import date

from sqlalchemy import select

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.db.init_db import create_tables_sync
from backend.db.database import AsyncSessionLocal
from backend.models.clinica import Clinica
from backend.repositories.usuario_repository import (
    create_user_specific_sync,
    get_user_by_cpf_sync,
)
from backend.repositories.paciente_repository import (
    create_patient_sync,
    get_patient_by_cpf_sync,
)
from backend.models.administrador import Administrador
from backend.models.recepcionista import Recepcionista
from backend.models.aluno import Aluno

CLINICAS = [
    {"codigo": "CLIN-ODONTO-01", "nome": "Clínica de Odontologia Geral"},
    {"codigo": "CLIN-PED-02", "nome": "Clínica de Odontopediatria"},
]

USUARIOS = [
    {
        "classe": Administrador,
        "nome": "Ana Beatriz Coordenadora",
        "email": "ana.coordenadora@clinisys.com",
        "cpf": "11122233300",
        "senha": "admin123",
        "extra": {},
    },
    {
        "classe": Recepcionista,
        "nome": "Bruno Henrique Recepcao",
        "email": "bruno.recepcao@clinisys.com",
        "cpf": "22233344411",
        "senha": "recepcao123",
        "extra": {"telefone": "48991234567"},
    },
]

PACIENTES = [
    ("Helena Souza", "34567890123", date(1990, 5, 4)),
    ("Marcos Almeida", "45678901234", date(1985, 9, 12)),
    ("Joana Pereira", "56789012345", date(2001, 1, 23)),
]

ALUNOS = [
    {
        "nome": "Mateus Gomes",
        "email": "mateus.gomes@aluno.ufsc.br",
        "cpf": "33344455522",
        "senha": "aluno123",
        "matricula": "ALN2025001",
        "telefone": "48998765432",
        "clinica_codigo": "CLIN-ODONTO-01",
    },
    {
        "nome": "Leticia Ramos",
        "email": "leticia.ramos@aluno.ufsc.br",
        "cpf": "44455566633",
        "senha": "aluno123",
        "matricula": "ALN2025002",
        "telefone": "48987654321",
        "clinica_codigo": "CLIN-PED-02",
    },
]


async def ensure_clinicas() -> dict[str, int]:
    async with AsyncSessionLocal() as session:
        created = 0
        for dados in CLINICAS:
            stmt = select(Clinica).where(Clinica.codigo == dados["codigo"])
            result = await session.execute(stmt)
            clinica = result.scalar_one_or_none()
            if clinica is None:
                clinica = Clinica(**dados)
                session.add(clinica)
                created += 1
        if created:
            await session.commit()
        result = await session.execute(select(Clinica))
        clinicas = result.scalars().all()
        return {c.codigo: c.id for c in clinicas}


def seed_users(clinica_map: dict[str, int]) -> None:
    for usuario in USUARIOS:
        if get_user_by_cpf_sync(usuario["cpf"]):
            continue
        create_user_specific_sync(
            usuario["classe"],
            nome=usuario["nome"],
            email=usuario["email"],
            cpf=usuario["cpf"],
            senha=usuario["senha"],
            **usuario["extra"],
        )

    for aluno in ALUNOS:
        if get_user_by_cpf_sync(aluno["cpf"]):
            continue
        clinica_id = clinica_map.get(aluno["clinica_codigo"])
        create_user_specific_sync(
            Aluno,
            nome=aluno["nome"],
            email=aluno["email"],
            cpf=aluno["cpf"],
            senha=aluno["senha"],
            matricula=aluno["matricula"],
            telefone=aluno["telefone"],
            clinica_id=clinica_id,
        )


def seed_pacientes() -> None:
    for nome, cpf, data_nasc in PACIENTES:
        if get_patient_by_cpf_sync(cpf):
            continue
        create_patient_sync(nome=nome, cpf=cpf, data_nascimento=data_nasc)


def main() -> None:
    print("Criando tabelas (se necessário)...")
    create_tables_sync()
    print("Inserindo clínicas...")
    clinica_map = asyncio.run(ensure_clinicas())
    print(f"Clinicas disponíveis: {len(clinica_map)}")
    print("Inserindo usuários...")
    seed_users(clinica_map)
    print("Inserindo pacientes...")
    seed_pacientes()
    print("População concluída.")


if __name__ == "__main__":
    main()
