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
    salvar_sync,
    verificar_paciente_tem_agendamento_no_dia_sync
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


def validar_mesma_clinica(aluno: Aluno, paciente: Paciente) -> bool:
    """
    RN04: Valida se o paciente pertence à mesma clínica do aluno.
    
    Nota: O modelo Paciente atual não possui clinica_id.
    Esta validação pressupõe que será adicionado ou usa lógica alternativa.
    Por enquanto, retorna True (assumindo que a validação será implementada).
    """
    # TODO: Verificar se o modelo Paciente tem clinica_id
    # Se não tiver, esta regra pode ser implementada de outra forma
    # Por exemplo, verificando se o paciente já foi atendido na clínica
    
    if not hasattr(paciente, 'clinica_id'):
        # Se o paciente não tem clinica_id, não podemos validar
        # Pode-se decidir permitir (return True) ou bloquear (return False)
        return True  # Permitindo por padrão
    
    return aluno.clinica_id == getattr(paciente, 'clinica_id', None)


# ===================== Função Principal de Criação ===================== #

def criar_atendimento(
    aluno: Aluno,
    paciente: Paciente,
    data_hora: datetime,
    tipo: str = "Consulta Odontológica",
    status: str = "Agendado"
) -> Atendimento:
    """
    Cria um novo atendimento após validar todas as regras de negócio.
    
    Args:
        aluno: Objeto Aluno que realizará o atendimento
        paciente: Objeto Paciente a ser atendido
        data_hora: Data e hora do atendimento
        tipo: Tipo do atendimento (padrão: "Consulta Odontológica")
        status: Status inicial (padrão: "Agendado")
    
    Returns:
        Atendimento criado e salvo no banco
    
    Raises:
        Exception: Se alguma regra de negócio for violada
    """
    
    # Validação RN04: Mesma clínica
    if not validar_mesma_clinica(aluno, paciente):
        raise Exception("Paciente não pertence à clínica deste aluno.")
    
    # Validação RN03: Dia útil
    if not validar_dia_util(data_hora):
        raise Exception("Agendamento fora do horário permitido. Apenas dias úteis (segunda a sexta).")
    
    # Validação RN03: Horário comercial
    if not validar_horario_comercial(data_hora):
        raise Exception("Agendamento fora do horário permitido. Horário comercial: 08:00 às 18:00.")
    
    # Validação NOVA: Paciente só pode ter um agendamento por dia
    print(f"[DEBUG SERVICE] Verificando agendamento duplicado para paciente {paciente.id} na data {data_hora}")
    tem_agendamento = verificar_paciente_tem_agendamento_no_dia_sync(paciente.id, data_hora)
    print(f"[DEBUG SERVICE] Resultado da verificação: {tem_agendamento}")
    
    if tem_agendamento:
        data_formatada = data_hora.strftime("%d/%m/%Y")
        raise Exception(
            f"O paciente {paciente.nome} já possui um agendamento para o dia {data_formatada}.\n"
            "Cada paciente pode ter apenas um agendamento por dia."
        )
    
    # Validação de disponibilidade: Verifica conflitos de horário
    disponivel = verificar_disponibilidade_sync(
        aluno_id=aluno.id,
        paciente_id=paciente.id,
        data_hora=data_hora
    )
    
    if not disponivel:
        raise Exception("Horário indisponível para o aluno ou paciente.")
    
    # Todas as validações passaram - criar o atendimento
    novo_atendimento = Atendimento(
        aluno_id=aluno.id,
        paciente_id=paciente.id,
        dataHora=data_hora,
        tipo=tipo,
        status=status
    )
    
    # Salvar no banco
    atendimento_salvo = salvar_sync(novo_atendimento)
    
    return atendimento_salvo


# ===================== Funções Auxiliares ===================== #

def listar_horarios_disponiveis(data: datetime) -> list[str]:
    """
    Retorna lista de horários disponíveis para um determinado dia.
    Horários: 08:00, 09:00, 10:00, 11:00, 13:00, 14:00, 15:00, 16:00, 17:00
    (Pausa para almoço: 12:00-13:00)
    """
    if not validar_dia_util(data):
        return []  # Sem horários em fins de semana
    
    horarios = [
        "08:00", "09:00", "10:00", "11:00",
        "13:00", "14:00", "15:00", "16:00", "17:00"
    ]
    
    return horarios


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
