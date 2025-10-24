"""
Controller de Pacientes - CliniSys Desktop
Implementação MVC correta para aplicação desktop
Baseado no modelo atual: nome, cpf, dataNascimento, statusAtendimento
"""

from __future__ import annotations

import re
from typing import List, Optional
from datetime import date

from ..models.paciente import Paciente as PacienteModel
from ..repositories.paciente_repository import (
    create_patient_sync,
    list_patients_sync,
    get_patient_by_id_sync,
    get_patient_by_cpf_sync,
    update_patient_sync,
    delete_patient_sync
)

# Constantes para mensagens
MSG_ID_INVALIDO = "ID do paciente deve ser um número positivo"
MSG_PACIENTE_NAO_ENCONTRADO = "Paciente não encontrado"


class PacienteController:
    """
    Controller para gerenciamento de pacientes no desktop.
    Responsável pela lógica de negócio e validações.
    """

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida formato do CPF."""
        cpf_numbers = re.sub(r'\D', '', cpf)
        
        if len(cpf_numbers) != 11:
            raise ValueError("CPF deve conter 11 dígitos")
        
        if cpf_numbers == cpf_numbers[0] * 11:
            raise ValueError("CPF inválido")
        
        return True

    @staticmethod
    def validate_nome(nome: str) -> bool:
        """Valida nome do paciente."""
        if not nome or len(nome.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        return True

    @staticmethod
    def validate_data_nascimento(data_nasc: date) -> bool:
        """Valida data de nascimento."""
        if data_nasc > date.today():
            raise ValueError("Data de nascimento não pode ser futura")
        return True

    @staticmethod
    def create_patient(nome: str, cpf: str, data_nascimento: date) -> dict:
        """Cria um novo paciente com validações de negócio."""
        try:
            # Validações
            PacienteController.validate_nome(nome)
            PacienteController.validate_cpf(cpf)
            PacienteController.validate_data_nascimento(data_nascimento)

            # Verificar se CPF já existe
            existing_patient = get_patient_by_cpf_sync(cpf)
            if existing_patient:
                raise ValueError(f"CPF {cpf} já está cadastrado no sistema")

            # Criar paciente
            patient = create_patient_sync(nome=nome, cpf=cpf, data_nascimento=data_nascimento)
            
            return {
                "success": True,
                "data": {
                    "id": patient.id,
                    "nome": patient.nome,
                    "cpf": patient.cpf,
                    "data_nascimento": patient.dataNascimento.isoformat(),
                    "status_atendimento": patient.statusAtendimento
                },
                "message": f"Paciente '{patient.nome}' cadastrado com sucesso"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro interno: {str(e)}"}

    @staticmethod
    def list_patients() -> dict:
        """Lista todos os pacientes do sistema."""
        try:
            patients = list_patients_sync()
            patients_data = [
                {
                    "id": patient.id,
                    "nome": patient.nome,
                    "cpf": patient.cpf,
                    "data_nascimento": patient.dataNascimento.isoformat(),
                    "status_atendimento": patient.statusAtendimento
                }
                for patient in patients
            ]
            
            return {
                "success": True,
                "data": patients_data,
                "message": f"{len(patients_data)} paciente(s) encontrado(s)"
            }

        except Exception as e:
            return {"success": False, "message": f"Erro ao listar pacientes: {str(e)}"}

    @staticmethod
    def get_patient_by_id(patient_id: int) -> dict:
        """Busca paciente por ID."""
        try:
            if patient_id <= 0:
                raise ValueError(MSG_ID_INVALIDO)

            patient = get_patient_by_id_sync(patient_id)
            if not patient:
                return {"success": False, "message": MSG_PACIENTE_NAO_ENCONTRADO}

            # patient já é um dicionário retornado por get_patient_by_id_sync
            patient['data_nascimento'] = patient['dataNascimento'].isoformat()
            patient['status_atendimento'] = patient['statusAtendimento']
            
            return {
                "success": True,
                "data": patient,
                "message": "Paciente encontrado"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar paciente: {str(e)}"}

    @staticmethod
    def search_patients_by_cpf(cpf: str) -> dict:
        """Busca paciente por CPF."""
        try:
            PacienteController.validate_cpf(cpf)

            patient = get_patient_by_cpf_sync(cpf)
            if not patient:
                return {"success": False, "message": "Paciente não encontrado"}

            return {
                "success": True,
                "data": {
                    "id": patient.id,
                    "nome": patient.nome,
                    "cpf": patient.cpf,
                    "data_nascimento": patient.dataNascimento.isoformat(),
                    "status_atendimento": patient.statusAtendimento
                },
                "message": "Paciente encontrado"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar paciente: {str(e)}"}

    @staticmethod
    def search_patients(search_term: str) -> dict:
        """Busca pacientes por nome ou CPF."""
        try:
            all_patients = list_patients_sync()
            search_term = search_term.lower().strip()
            
            if not search_term:
                filtered_patients = all_patients
            else:
                filtered_patients = [
                    patient for patient in all_patients
                    if search_term in patient.nome.lower() or search_term in patient.cpf
                ]

            patients_data = [
                {
                    "id": patient.id,
                    "nome": patient.nome,
                    "cpf": patient.cpf,
                    "data_nascimento": patient.dataNascimento.isoformat(),
                    "status_atendimento": patient.statusAtendimento
                }
                for patient in filtered_patients
            ]
            
            return {
                "success": True,
                "data": patients_data,
                "message": f"{len(patients_data)} paciente(s) encontrado(s)"
            }

        except Exception as e:
            return {"success": False, "message": f"Erro na busca: {str(e)}"}