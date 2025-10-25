"""
Controller para registro de procedimentos realizados em atendimento.

"""

from __future__ import annotations

from typing import Any


DATETIME_DISPLAY_FORMAT = "%d/%m/%Y %H:%M"

from ..services import atendimento_service


class AtendimentoController:
    """Endpoints síncronos consumidos pela interface desktop."""

    @staticmethod
    def listar_agendados_para_execucao(aluno_id: int) -> dict[str, Any]:
        try:
            atendimentos = atendimento_service.listar_agendados_para_execucao(aluno_id)
            dados_formatados = [
                {
                    "id": item["id"],
                    "data_hora_formatada": item["data_hora"].strftime(DATETIME_DISPLAY_FORMAT),
                    "tipo": item["tipo"],
                    "paciente_id": item["paciente_id"],
                    "paciente_nome": item["paciente_nome"],
                }
                for item in atendimentos
            ]

            return {
                "success": True,
                "message": "Atendimentos agendados recuperados com sucesso.",
                "data": dados_formatados,
            }
        except Exception as exc:  # pylint: disable=broad-except
            return {
                "success": False,
                "message": str(exc),
                "data": [],
            }

    @staticmethod
    def listar_atendimentos_realizados(aluno_id: int) -> dict[str, Any]:
        try:
            atendimentos = atendimento_service.listar_atendimentos_realizados(aluno_id)
            dados_formatados = [
                {
                    "id": item["id"],
                    "data_hora_formatada": item["data_hora"].strftime(DATETIME_DISPLAY_FORMAT)
                    if item["data_hora"]
                    else None,
                    "tipo": item["tipo"],
                    "status": item["status"],
                    "paciente_id": item["paciente_id"],
                    "paciente_nome": item["paciente_nome"],
                    "procedimentos": item.get("procedimentos"),
                    "observacoes": item.get("observacoes"),
                }
                for item in atendimentos
            ]

            return {
                "success": True,
                "message": "Atendimentos concluídos recuperados com sucesso.",
                "data": dados_formatados,
            }
        except Exception as exc:  # pylint: disable=broad-except
            return {
                "success": False,
                "message": str(exc),
                "data": [],
            }

    @staticmethod
    def registrar_procedimentos(dados: dict[str, Any]) -> dict[str, Any]:
        try:
            atendimento_id = dados.get("atendimento_id")
            procedimentos = dados.get("procedimentos")
            observacoes = dados.get("observacoes")

            if atendimento_id is None:
                raise ValueError("ID do atendimento é obrigatório.")

            if not isinstance(atendimento_id, int):
                try:
                    atendimento_id = int(atendimento_id)
                except (TypeError, ValueError) as exc:
                    raise ValueError("ID do atendimento inválido.") from exc

            if procedimentos is None:
                raise ValueError("Descrição dos procedimentos é obrigatória.")

            if not isinstance(procedimentos, str):
                procedimentos = str(procedimentos)

            resultado = atendimento_service.registrar_procedimentos(
                atendimento_id=atendimento_id,
                procedimentos_realizados=procedimentos,
                observacoes=observacoes,
            )

            return {
                "success": True,
                "message": "Procedimentos registrados com sucesso.",
                "data": {
                    "atendimento_id": resultado["id"],
                    "status": resultado["status"],
                    "procedimentos": resultado["procedimentos"],
                    "observacoes": resultado["observacoes"],
                    "data_hora": resultado["data_hora"].strftime(DATETIME_DISPLAY_FORMAT),
                },
            }
        except Exception as exc:  # pylint: disable=broad-except
            return {
                "success": False,
                "message": str(exc),
                "data": {},
            }
