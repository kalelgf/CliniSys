"""
Serviços relacionados ao registro de procedimentos em atendimentos.

"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any

from ..repositories.consulta_repository import (
    get_by_id_sync,
    listar_agendados_por_aluno_sync,
    listar_concluidos_por_aluno_sync,
    registrar_procedimentos_sync,
)
from ..repositories.paciente_repository import update_patient_sync
from ..repositories.sync_helpers import get_patient_by_id_sync_direct


def listar_agendados_para_execucao(aluno_id: int) -> List[Dict[str, Any]]:
    """Retorna atendimentos agendados para o aluno informado."""
    if not aluno_id:
        raise ValueError("ID do aluno é obrigatório.")

    atendimentos = listar_agendados_por_aluno_sync(aluno_id)
    resultado: List[Dict[str, Any]] = []

    for atendimento in atendimentos:
        paciente_info = None
        if atendimento.paciente_id:
            paciente_info = get_patient_by_id_sync_direct(atendimento.paciente_id)

        resultado.append(
            {
                "id": atendimento.id,
                "data_hora": atendimento.dataHora,
                "tipo": atendimento.tipo,
                "paciente_id": atendimento.paciente_id,
                "paciente_nome": paciente_info.get("nome") if paciente_info else None,
            }
        )

    return resultado


def listar_atendimentos_realizados(aluno_id: int) -> List[Dict[str, Any]]:
    """Retorna atendimentos já concluídos pelo aluno."""
    if not aluno_id:
        raise ValueError("ID do aluno é obrigatório.")

    atendimentos = listar_concluidos_por_aluno_sync(aluno_id)
    resultado: List[Dict[str, Any]] = []

    for atendimento in atendimentos:
        paciente_info = None
        if atendimento.paciente_id:
            paciente_info = get_patient_by_id_sync_direct(atendimento.paciente_id)

        resultado.append(
            {
                "id": atendimento.id,
                "data_hora": atendimento.dataHora,
                "tipo": atendimento.tipo,
                "status": atendimento.status,
                "paciente_id": atendimento.paciente_id,
                "paciente_nome": paciente_info.get("nome") if paciente_info else None,
                "procedimentos": atendimento.procedimentosRealizados,
                "observacoes": atendimento.observacoesPosAtendimento,
            }
        )

    return resultado


def registrar_procedimentos(
    atendimento_id: int,
    procedimentos_realizados: str,
    observacoes: str | None = None,
) -> Dict[str, Any]:
    """Registra os procedimentos realizados em um atendimento."""
    if not atendimento_id:
        raise ValueError("ID do atendimento é obrigatório.")

    if procedimentos_realizados is None or not procedimentos_realizados.strip():
        raise ValueError("Descrição dos procedimentos é obrigatória.")

    atendimento = get_by_id_sync(atendimento_id)
    if atendimento is None:
        raise ValueError("Atendimento não encontrado.")

    if atendimento.status != "Agendado":
        raise ValueError("Somente atendimentos agendados podem receber procedimentos.")

    atualizado = registrar_procedimentos_sync(
        atendimento_id,
        procedimentos_realizados.strip(),
        observacoes.strip() if observacoes and observacoes.strip() else None,
    )

    if atualizado is None:
        raise RuntimeError("Falha ao registrar procedimentos para o atendimento informado.")

    if atualizado.paciente_id is not None:
        update_patient_sync(
            patient_id=atualizado.paciente_id,
            status_atendimento="Atendimento Concluído"
        )

    return {
        "id": atualizado.id,
        "status": atualizado.status,
        "procedimentos": atualizado.procedimentosRealizados,
        "observacoes": atualizado.observacoesPosAtendimento,
        "data_hora": atualizado.dataHora,
    }
