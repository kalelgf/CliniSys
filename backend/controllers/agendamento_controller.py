"""
Controller de Agendamentos - CliniSys Desktop
Implementação MVC correta para agendamento de atendimentos
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime

from ..models.aluno import Aluno
from ..models.paciente import Paciente
from ..repositories.sync_helpers import get_user_by_id_sync_direct, get_patient_by_id_sync_direct
from ..services import agendamento_service


class AgendamentoController:


    @staticmethod
    def agendar_novo_atendimento(dados: dict) -> dict:

        try:
            # 1. Extrair dados do dicionário
            paciente_id = dados.get("paciente_id")
            aluno_id = dados.get("aluno_id")
            data_hora = dados.get("data_hora")
            tipo = dados.get("tipo", "Consulta Odontológica")
            status = dados.get("status", "Agendado")
            
            # Validações básicas de entrada
            if not paciente_id:
                return {
                    "success": False,
                    "message": "ID do paciente é obrigatório.",
                    "data": {}
                }
            
            if not aluno_id:
                return {
                    "success": False,
                    "message": "ID do aluno é obrigatório.",
                    "data": {}
                }
            
            if not data_hora:
                return {
                    "success": False,
                    "message": "Data e horário são obrigatórios.",
                    "data": {}
                }
            
            # Se data_hora não for datetime, tentar converter
            if not isinstance(data_hora, datetime):
                if isinstance(data_hora, dict):
                    data_str = data_hora.get("data")
                    horario_str = data_hora.get("horario")
                    try:
                        data_hora = agendamento_service.formatar_data_hora(data_str, horario_str)
                    except ValueError as e:
                        return {
                            "success": False,
                            "message": f"Formato de data/hora inválido: {str(e)}",
                            "data": {}
                        }
                else:
                    return {
                        "success": False,
                        "message": "Formato de data_hora inválido.",
                        "data": {}
                    }
            
            # 2. Mensagens 3 e 4 da Sequência: Buscar aluno e paciente
            aluno = get_user_by_id_sync_direct(aluno_id)
            paciente = get_patient_by_id_sync_direct(paciente_id)
            
            # Validar se foram encontrados
            if not aluno:
                return {
                    "success": False,
                    "message": "Aluno não encontrado.",
                    "data": {}
                }
            
            if not paciente:
                return {
                    "success": False,
                    "message": "Paciente não encontrado.",
                    "data": {}
                }
            
            # Validar se o usuário é realmente um aluno
            if aluno.get('tipo', '').lower() != 'aluno':
                return {
                    "success": False,
                    "message": "Usuário não é um aluno.",
                    "data": {}
                }
            
            # Extrair dados (agora são dicionários, não precisa extrair)
            aluno_nome = aluno['nome']
            paciente_nome = paciente['nome']
            
            
            # Passar apenas IDs para evitar problemas de sessão
            atendimento = agendamento_service.criar_atendimento(
                aluno_id=aluno_id,
                paciente_id=paciente_id,
                data_hora=data_hora,
                tipo=tipo,
                status=status
            )
            
            # Extrair dados do atendimento salvo
            atendimento_id = atendimento.id
            atendimento_data_hora = atendimento.dataHora.strftime("%d/%m/%Y %H:%M")
            atendimento_tipo = atendimento.tipo
            atendimento_status = atendimento.status
            
            # 4. Retornar sucesso
            return {
                "success": True,
                "message": "Atendimento agendado com sucesso!",
                "data": {
                    "atendimento_id": atendimento_id,
                    "aluno_nome": aluno_nome,
                    "paciente_nome": paciente_nome,
                    "data_hora": atendimento_data_hora,
                    "tipo": atendimento_tipo,
                    "status": atendimento_status
                }
            }
        
        except Exception as e:
            # Captura exceções de regras de negócio do serviço
            return {
                "success": False,
                "message": str(e),
                "data": {}
            }

    @staticmethod
    def listar_horarios_disponiveis(data_str: str, aluno_id: Optional[int] = None) -> dict:

        try:
            # Converter string para datetime
            dia, mes, ano = data_str.split('/')
            data = datetime(int(ano), int(mes), int(dia))
            
            # Obter horários disponíveis
            horarios = agendamento_service.listar_horarios_disponiveis(data, aluno_id)
            
            if not horarios:
                return {
                    "success": False,
                    "message": "Não há horários disponíveis para esta data (apenas dias úteis).",
                    "data": []
                }
            
            return {
                "success": True,
                "message": f"{len(horarios)} horários disponíveis.",
                "data": horarios
            }
        
        except (ValueError, IndexError) as e:
            return {
                "success": False,
                "message": f"Formato de data inválido: {str(e)}",
                "data": []
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao listar horários: {str(e)}",
                "data": []
            }

    @staticmethod
    def obter_dados_paciente(paciente_id: int) -> dict:

        try:
            paciente = get_patient_by_id_sync_direct(paciente_id)
            
            if not paciente:
                return {
                    "success": False,
                    "message": "Paciente não encontrado.",
                    "data": {}
                }
            
            return {
                "success": True,
                "message": "Dados do paciente obtidos com sucesso.",
                "data": {
                    "id": paciente['id'],
                    "nome": paciente['nome'],
                    "cpf": paciente['cpf'],
                    "data_nascimento": paciente['dataNascimento'].strftime("%d/%m/%Y"),
                    "status_atendimento": paciente['statusAtendimento']
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao obter dados do paciente: {str(e)}",
                "data": {}
            }
