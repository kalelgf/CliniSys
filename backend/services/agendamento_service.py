"""
Serviços de Agendamento de Atendimentos - CliniSys
Regras de negócio para agendamento de consultas
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from ..models.atendimento import Atendimento
from ..models.aluno import Aluno
from ..models.paciente import Paciente
from ..repositories.consulta_repository import (
    verificar_disponibilidade_sync,
    verificar_conflito_detalhado_sync,
    salvar_sync,
    verificar_paciente_tem_agendamento_no_dia_sync,
    listar_horarios_ocupados_por_aluno_sync
)


# ===================== Validações de Regras de Negócio ===================== #

def validar_dia_util(data_hora: datetime) -> bool:
    """
    RN03: Valida se a data é um dia útil (segunda a sexta).
    Retorna True se for dia útil, False caso contrário.
    """
    # weekday(): 0=segunda, 1=terça, ..., 4=sexta, 5=sábado, 6=domingo
    return data_hora.weekday() < 5  # 0-4 são dias úteis


def validar_horario_comercial(data_hora: datetime) -> bool:
    """
    RN03: Valida se o horário está dentro do horário comercial (08:00-18:00).
    Retorna True se estiver dentro do horário, False caso contrário.
    """
    horario = data_hora.time()
    horario_inicio = time(8, 0)  # 08:00
    horario_fim = time(18, 0)     # 18:00
    
    return horario_inicio <= horario < horario_fim


def validar_data_hora_futura(data_hora: datetime) -> bool:
    """
    RN05: Valida se a data e hora do agendamento não está no passado.
    Retorna True se for futura, False se for passada.
    """
    agora = datetime.now()
    return data_hora > agora


def validar_mesma_clinica(aluno: Aluno, paciente: Paciente) -> bool:
    """
    RN04: Valida se o paciente pertence à mesma clínica do aluno.
    
    Args:
        aluno: Objeto Aluno que realizará o atendimento
        paciente: Objeto Paciente a ser atendido
    
    Returns:
        True se pertencem à mesma clínica, False caso contrário
    
    Raises:
        Exception: Se o paciente não estiver vinculado a nenhuma clínica
    """
    # Se ambos não têm clínica, permitir (para compatibilidade com dados antigos)
    if paciente.clinica_id is None and aluno.clinica_id is None:
        return True
    
    # Se o paciente tem clínica mas o aluno não, ou vice-versa
    if paciente.clinica_id is None or aluno.clinica_id is None:
        # Permitir por enquanto (avisar no futuro)
        return True
    
    # Verificar se é a mesma clínica do aluno
    if aluno.clinica_id != paciente.clinica_id:
        return False
    
    return True


def validar_mesma_clinica_por_id(aluno_clinica_id: Optional[int], paciente_clinica_id: Optional[int], 
                                  aluno_nome: str, paciente_nome: str) -> bool:
    """
    RN04: Valida se o paciente pertence à mesma clínica do aluno (versão usando IDs).
    
    Args:
        aluno_clinica_id: ID da clínica do aluno
        paciente_clinica_id: ID da clínica do paciente
        aluno_nome: Nome do aluno (para mensagens de erro)
        paciente_nome: Nome do paciente (para mensagens de erro)
    
    Returns:
        True se pertencem à mesma clínica, False caso contrário
    """
    # Se ambos não têm clínica, permitir (para compatibilidade com dados antigos)
    if paciente_clinica_id is None and aluno_clinica_id is None:
        return True
    
    # Se o paciente tem clínica mas o aluno não, ou vice-versa
    if paciente_clinica_id is None or aluno_clinica_id is None:
        # Permitir por enquanto (avisar no futuro)
        return True
    
    # Verificar se é a mesma clínica do aluno
    if aluno_clinica_id != paciente_clinica_id:
        return False
    
    return True


# ===================== Função Principal de Criação ===================== #

def criar_atendimento(
    aluno_id: int,
    paciente_id: int,
    data_hora: datetime,
    tipo: str = "Consulta Odontológica",
    status: str = "Agendado"
) -> Atendimento:
    """
    Cria um novo atendimento após validar todas as regras de negócio.
    
    Args:
        aluno_id: ID do aluno que realizará o atendimento
        paciente_id: ID do paciente a ser atendido
        data_hora: Data e hora do atendimento
        tipo: Tipo do atendimento (padrão: "Consulta Odontológica")
        status: Status inicial (padrão: "Agendado")
    
    Returns:
        Atendimento criado e salvo no banco
    
    Raises:
        Exception: Se alguma regra de negócio for violada
    """
    
    # Buscar aluno e paciente para validações (usar funções síncronas diretas)
    from ..repositories.sync_helpers import get_user_by_id_sync_direct, get_patient_by_id_sync_direct
    
    aluno = get_user_by_id_sync_direct(aluno_id)
    paciente = get_patient_by_id_sync_direct(paciente_id)
    
    if not aluno:
        raise Exception(f"Aluno com ID {aluno_id} não encontrado.")
    
    if not paciente:
        raise Exception(f"Paciente com ID {paciente_id} não encontrado.")
    
    # Extrair dados necessários (agora são dicionários)
    aluno_nome = aluno['nome']
    aluno_clinica_id = aluno['clinica_id']
    
    paciente_nome = paciente['nome']
    paciente_clinica_id = paciente['clinica_id']
    
    # Validação RN04: Mesma clínica (usando dados extraídos)
    if not validar_mesma_clinica_por_id(aluno_clinica_id, paciente_clinica_id, aluno_nome, paciente_nome):
        raise Exception(
            f"Paciente '{paciente_nome}' não pertence à clínica do aluno '{aluno_nome}'.\n"
            f"Apenas pacientes da mesma clínica podem ser atendidos.\n"
            f"Paciente está na clínica ID: {paciente_clinica_id}, "
            f"Aluno está na clínica ID: {aluno_clinica_id}"
        )
    
    # Validação RN05: Data/hora não pode estar no passado
    if not validar_data_hora_futura(data_hora):
        data_formatada = data_hora.strftime("%d/%m/%Y às %H:%M")
        raise Exception(
            f"Não é possível agendar para uma data/hora no passado.\n"
            f"Data/hora informada: {data_formatada}"
        )
    
    # Validação RN03: Dia útil
    if not validar_dia_util(data_hora):
        raise Exception("Agendamento fora do horário permitido. Apenas dias úteis (segunda a sexta).")
    
    # Validação RN03: Horário comercial
    if not validar_horario_comercial(data_hora):
        raise Exception("Agendamento fora do horário permitido. Horário comercial: 08:00 às 18:00.")
    
    # Validação NOVA: Paciente só pode ter um agendamento por dia
    print(f"[DEBUG SERVICE] Verificando agendamento duplicado para paciente {paciente_id} na data {data_hora}")
    tem_agendamento = verificar_paciente_tem_agendamento_no_dia_sync(paciente_id, data_hora)
    print(f"[DEBUG SERVICE] Resultado da verificação: {tem_agendamento}")
    
    if tem_agendamento:
        data_formatada = data_hora.strftime("%d/%m/%Y")
        raise Exception(
            f"O paciente {paciente_nome} já possui um agendamento para o dia {data_formatada}.\n"
            "Cada paciente pode ter apenas um agendamento por dia."
        )
    
    # Validação de disponibilidade: Verifica conflitos de horário
    conflito_info = verificar_conflito_detalhado_sync(
        aluno_id=aluno_id,
        paciente_id=paciente_id,
        data_hora=data_hora
    )
    
    if not conflito_info["disponivel"]:
        raise Exception(conflito_info["mensagem"])
    
    # Todas as validações passaram - criar o atendimento
    novo_atendimento = Atendimento(
        aluno_id=aluno_id,
        paciente_id=paciente_id,
        dataHora=data_hora,
        tipo=tipo,
        status=status
    )
    
    # Salvar no banco
    atendimento_salvo = salvar_sync(novo_atendimento)
    
    return atendimento_salvo


# ===================== Funções Auxiliares ===================== #

def listar_horarios_disponiveis(data: datetime, aluno_id: Optional[int] = None) -> list[str]:
    """
    Retorna lista de horários disponíveis para um determinado dia.
    Se aluno_id for fornecido, filtra apenas horários livres para aquele aluno.
    
    Horários possíveis: 08:00, 09:00, 10:00, 11:00, 13:00, 14:00, 15:00, 16:00, 17:00
    (Pausa para almoço: 12:00-13:00)
    
    Args:
        data: Data para verificar disponibilidade
        aluno_id: ID do aluno (opcional). Se fornecido, filtra horários ocupados.
    
    Returns:
        Lista de strings com horários disponíveis (formato "HH:MM")
    """
    if not validar_dia_util(data):
        return []  # Sem horários em fins de semana
    
    # Todos os horários possíveis
    todos_horarios = [
        "08:00", "09:00", "10:00", "11:00",
        "13:00", "14:00", "15:00", "16:00", "17:00"
    ]
    
    # Se não foi fornecido aluno_id, retornar todos os horários
    if aluno_id is None:
        return todos_horarios
    
    # Buscar horários já ocupados pelo aluno nesta data
    horarios_ocupados = listar_horarios_ocupados_por_aluno_sync(aluno_id, data)
    
    # Converter datetime para string "HH:MM"
    horarios_ocupados_str = [h.strftime("%H:%M") for h in horarios_ocupados]
    
    # Filtrar apenas horários disponíveis
    horarios_disponiveis = [h for h in todos_horarios if h not in horarios_ocupados_str]
    
    return horarios_disponiveis


def formatar_data_hora(data_str: str, horario_str: str) -> datetime:
    """
    Converte strings de data (DD/MM/AAAA) e horário (HH:MM) em datetime.
    
    Args:
        data_str: Data no formato DD/MM/AAAA
        horario_str: Horário no formato HH:MM
    
    Returns:
        Objeto datetime
    
    Raises:
        ValueError: Se o formato estiver incorreto
    """
    try:
        # Parse da data
        dia, mes, ano = data_str.split('/')
        
        # Parse do horário
        hora, minuto = horario_str.split(':')
        
        # Criar datetime
        data_hora = datetime(
            year=int(ano),
            month=int(mes),
            day=int(dia),
            hour=int(hora),
            minute=int(minuto)
        )
        
        return data_hora
    
    except (ValueError, IndexError) as e:
        raise ValueError(f"Formato de data/hora inválido: {str(e)}")
