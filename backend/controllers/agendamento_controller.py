"""
Controller de Agendamentos - CliniSys Desktop
Implementação MVC correta para agendamento de atendimentos
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime

from ..models.aluno import Aluno
from ..models.paciente import Paciente
from ..repositories.usuario_repository import get_user_by_id_sync
from ..repositories.paciente_repository import get_patient_by_id_sync
from ..services import agendamento_service


class AgendamentoController:
    """
    Controller para operações de agendamento de atendimentos.
    Segue o padrão MVC e retorna respostas padronizadas.
    """

    @staticmethod
    def agendar_novo_atendimento(dados: dict) -> dict:
        """
        Agenda um novo atendimento seguindo o Diagrama de Sequência.
        
        Args:
            dados: Dicionário contendo:
                - paciente_id: int
                - aluno_id: int
                - data_hora: datetime ou dict com 'data' e 'horario'
                - tipo: str (opcional, padrão: "Consulta Odontológica")
                - status: str (opcional, padrão: "Agendado")
        
        Returns:
            dict: {"success": bool, "message": str, "data": dict}
        """
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
            aluno = get_user_by_id_sync(aluno_id)
            paciente = get_patient_by_id_sync(paciente_id)
            
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
            if not isinstance(aluno, Aluno):
                return {
                    "success": False,
                    "message": "Usuário não é um aluno.",
                    "data": {}
                }
            
            # 3. Mensagem 5 da Sequência: Chamar serviço para criar atendimento
            # O serviço já faz todas as validações de regras de negócio
            atendimento = agendamento_service.criar_atendimento(
                aluno=aluno,
                paciente=paciente,
                data_hora=data_hora,
                tipo=tipo,
                status=status
            )
            
            # 4. Retornar sucesso
            return {
                "success": True,
                "message": "Atendimento agendado com sucesso!",
                "data": {
                    "atendimento_id": atendimento.id,
                    "aluno_nome": aluno.nome,
                    "paciente_nome": paciente.nome,
                    "data_hora": atendimento.dataHora.strftime("%d/%m/%Y %H:%M"),
                    "tipo": atendimento.tipo,
                    "status": atendimento.status
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
    def listar_horarios_disponiveis(data_str: str) -> dict:
        """
        Lista horários disponíveis para uma determinada data.
        
        Args:
            data_str: Data no formato DD/MM/AAAA
        
        Returns:
            dict: {"success": bool, "message": str, "data": list}
        """
        try:
            # Converter string para datetime
            dia, mes, ano = data_str.split('/')
            data = datetime(int(ano), int(mes), int(dia))
            
            # Obter horários disponíveis
            horarios = agendamento_service.listar_horarios_disponiveis(data)
            
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
        """
        Obtém dados básicos do paciente para exibição.
        
        Args:
            paciente_id: ID do paciente
        
        Returns:
            dict: {"success": bool, "message": str, "data": dict}
        """
        try:
            paciente = get_patient_by_id_sync(paciente_id)
            
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
                    "id": paciente.id,
                    "nome": paciente.nome,
                    "cpf": paciente.cpf,
                    "data_nascimento": paciente.dataNascimento.strftime("%d/%m/%Y"),
                    "status_atendimento": paciente.statusAtendimento
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao obter dados do paciente: {str(e)}",
                "data": {}
            }
