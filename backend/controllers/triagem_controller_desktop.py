"""
Controller de Triagem - CliniSys Desktop
Responsável pela lógica de triagem de pacientes
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..repositories.triagem_repository import (
    create_triagem,
    get_triagem_by_paciente,
    list_triagens_pendentes,
    list_triagens_realizadas
)

# Constantes para validação
PRESSAO_PATTERN = r'^\d{2,3}/\d{2,3}$'
SPO2_MIN, SPO2_MAX = 0, 100
TEMP_MIN, TEMP_MAX = 35.0, 42.0
FC_MIN, FC_MAX = 40, 200
FR_MIN, FR_MAX = 10, 40
DOR_MIN, DOR_MAX = 0, 10

class TriagemController:
    """Controller para gerenciamento de triagens."""

    @staticmethod
    def validate_pressao(pressao: str) -> bool:
        """Valida formato da pressão arterial (sistólica/diastólica)."""
        import re
        if not pressao:
            return True  # Opcional
        if not re.match(PRESSAO_PATTERN, pressao):
            raise ValueError("Pressão deve estar no formato 'sistólica/diastólica' (ex: 120/80)")
        
        try:
            sys, dia = map(int, pressao.split('/'))
            if not (60 <= sys <= 300) or not (40 <= dia <= 200):
                raise ValueError("Valores de pressão fora do intervalo aceitável")
        except ValueError as e:
            if str(e).startswith("Valores"):
                raise
            raise ValueError("Pressão deve conter apenas números")
        
        return True

    @staticmethod
    def validate_spo2(spo2: str) -> bool:
        """Valida saturação de O2."""
        if not spo2:
            return True  # Opcional
        try:
            valor = float(spo2)
            if not (SPO2_MIN <= valor <= SPO2_MAX):
                raise ValueError(f"Saturação deve estar entre {SPO2_MIN}% e {SPO2_MAX}%")
        except ValueError:
            raise ValueError("Saturação deve ser um número")
        return True

    @staticmethod
    def validate_temperatura(temp: str) -> bool:
        """Valida temperatura."""
        if not temp:
            return True  # Opcional
        try:
            valor = float(temp)
            if not (TEMP_MIN <= valor <= TEMP_MAX):
                raise ValueError(f"Temperatura deve estar entre {TEMP_MIN}°C e {TEMP_MAX}°C")
        except ValueError:
            raise ValueError("Temperatura deve ser um número")
        return True

    @staticmethod
    def validate_fc(fc: str) -> bool:
        """Valida frequência cardíaca."""
        if not fc:
            return True  # Opcional
        try:
            valor = int(fc)
            if not (FC_MIN <= valor <= FC_MAX):
                raise ValueError(f"Frequência cardíaca deve estar entre {FC_MIN} e {FC_MAX} bpm")
        except ValueError:
            raise ValueError("Frequência cardíaca deve ser um número inteiro")
        return True

    @staticmethod
    def validate_fr(fr: str) -> bool:
        """Valida frequência respiratória."""
        if not fr:
            return True  # Opcional
        try:
            valor = int(fr)
            if not (FR_MIN <= valor <= FR_MAX):
                raise ValueError(f"Frequência respiratória deve estar entre {FR_MIN} e {FR_MAX}")
        except ValueError:
            raise ValueError("Frequência respiratória deve ser um número inteiro")
        return True

    @staticmethod
    def validate_dor(dor: str) -> bool:
        """Valida escala de dor."""
        if not dor:
            return True  # Opcional
        try:
            valor = int(dor)
            if not (DOR_MIN <= valor <= DOR_MAX):
                raise ValueError(f"Escala de dor deve estar entre {DOR_MIN} e {DOR_MAX}")
        except ValueError:
            raise ValueError("Escala de dor deve ser um número inteiro")
        return True

    @staticmethod
    def validate_queixa(queixa: str) -> bool:
        """Valida queixa principal."""
        if not queixa or len(queixa.strip()) < 10:
            raise ValueError("Queixa principal deve ter pelo menos 10 caracteres")
        return True

    @staticmethod
    def validate_prioridade(prioridade: str) -> bool:
        """Valida prioridade da triagem."""
        if prioridade not in ("Alta", "Média", "Baixa"):
            raise ValueError("Prioridade deve ser Alta, Média ou Baixa")
        return True

    @staticmethod
    def realizar_triagem(dados: Dict[str, Any]) -> dict:
        """
        Realiza triagem de um paciente com validações.
        Retorna dict com success, data (id da triagem) e message.
        """
        try:
            # Validações obrigatórias
            TriagemController.validate_queixa(dados.get('queixa', ''))
            TriagemController.validate_prioridade(dados.get('prioridade', ''))

            # Validações opcionais (campos podem estar vazios)
            TriagemController.validate_pressao(dados.get('pressao', ''))
            TriagemController.validate_spo2(dados.get('spo2', ''))
            TriagemController.validate_temperatura(dados.get('temp', ''))
            TriagemController.validate_fc(dados.get('fc', ''))
            TriagemController.validate_fr(dados.get('fr', ''))
            TriagemController.validate_dor(dados.get('dor', ''))

            # Criar triagem
            triagem_id = create_triagem(dados)

            return {
                "success": True,
                "data": {"id": triagem_id},
                "message": "Triagem realizada com sucesso"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro ao realizar triagem: {str(e)}"}

    @staticmethod
    def get_paciente_triagem(paciente_id: int) -> dict:
        """Busca última triagem de um paciente."""
        try:
            triagem = get_triagem_by_paciente(paciente_id)
            if not triagem:
                return {
                    "success": False,
                    "message": "Paciente não possui triagem"
                }

            return {
                "success": True,
                "data": triagem,
                "message": "Triagem encontrada"
            }

        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar triagem: {str(e)}"}

    @staticmethod
    def list_fila_triagem() -> dict:
        """Lista pacientes aguardando triagem."""
        try:
            pacientes = list_triagens_pendentes()
            return {
                "success": True,
                "data": pacientes,
                "message": f"{len(pacientes)} paciente(s) aguardando triagem"
            }

        except Exception as e:
            return {"success": False, "message": f"Erro ao listar fila: {str(e)}"}

    @staticmethod
    def list_pacientes_triados() -> dict:
        """Lista pacientes já triados."""
        try:
            pacientes = list_triagens_realizadas()
            return {
                "success": True,
                "data": pacientes,
                "message": f"{len(pacientes)} paciente(s) triado(s)"
            }

        except Exception as e:
            return {"success": False, "message": f"Erro ao listar triados: {str(e)}"}