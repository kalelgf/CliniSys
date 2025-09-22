"""
Controller de Usuários - CliniSys Desktop
Implementação MVC correta para aplicação desktop com classes específicas
"""

from __future__ import annotations

import re
import random
from datetime import datetime
from typing import List, Optional, Type, Union

from ..models.usuario import UsuarioSistema
from ..models.administrador import Administrador
from ..models.recepcionista import Recepcionista
from ..models.professor import Professor
from ..models.aluno import Aluno
from ..repositories.usuario_repository import (
    create_user_specific_sync,
    list_users_sync,
    list_users_with_details_sync,
    get_user_by_id_sync,
    get_user_by_email_sync,
    get_user_by_cpf_sync,
    get_user_by_matricula_sync,
    update_user_sync,
    delete_user_sync,
    set_user_active_sync,
    change_user_password_sync,
    init_db_and_seed_sync
)

# Constantes para mensagens
MSG_ID_INVALIDO = "ID do usuário deve ser um número positivo"
MSG_USUARIO_NAO_ENCONTRADO = "Usuário não encontrado"

# Tipos de usuário disponíveis
TIPOS_USUARIO = {
    "administrador": Administrador,
    "recepcionista": Recepcionista,
    "professor": Professor,
    "aluno": Aluno
}


class UserFactory:
    """Factory para criar usuários das classes específicas"""
    
    @staticmethod
    def get_user_class(tipo_usuario: str) -> Type[UsuarioSistema]:
        """Retorna a classe correta para o tipo de usuário"""
        if tipo_usuario not in TIPOS_USUARIO:
            raise ValueError(f"Tipo de usuário '{tipo_usuario}' inválido. Tipos aceitos: {list(TIPOS_USUARIO.keys())}")
        return TIPOS_USUARIO[tipo_usuario]
    
    @staticmethod
    def get_user_type(user: UsuarioSistema) -> str:
        """Retorna o tipo de usuário baseado na classe"""
        for tipo, classe in TIPOS_USUARIO.items():
            if isinstance(user, classe):
                return tipo
        return "usuario_base"


class UsuarioController:
    """
    Controller para gerenciamento de usuários no desktop.
    Responsável pela lógica de negócio e validações.
    """

    @staticmethod
    def generate_unique_matricula() -> str:
        """
        Gera uma matrícula única para aluno no formato AASSRRR.
        AA = Ano (2 dígitos)
        SS = Semestre (01 ou 02)
        RRR = Sequencial aleatório (000-999)
        
        Garante unicidade verificando se a matrícula já existe.
        """
        now = datetime.now()
        ano = str(now.year)[-2:]  # Últimos 2 dígitos do ano (ex: 25)
        
        # Determinar semestre baseado no mês
        # Janeiro-Junho = 01, Julho-Dezembro = 02
        semestre = "01" if now.month <= 6 else "02"
        
        # Tentar gerar matrícula única até 100 tentativas
        for _ in range(100):
            sequencial = f"{random.randint(0, 999):03d}"  # 000-999 com zero à esquerda
            matricula = f"{ano}{semestre}{sequencial}"
            
            # Verificar se a matrícula já existe
            existing_user = get_user_by_matricula_sync(matricula)
            
            if not existing_user:
                return matricula
        
        # Se não conseguiu gerar após 100 tentativas, usar timestamp
        timestamp = str(int(now.timestamp()))[-3:]  # Últimos 3 dígitos do timestamp
        return f"{ano}{semestre}{timestamp}"

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """
        Valida formato e dígitos verificadores do CPF.
        Regra de negócio: CPF deve ser válido conforme algoritmo padrão.
        """
        # Remove caracteres não numéricos
        cpf_numbers = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf_numbers) != 11:
            raise ValueError("CPF deve conter 11 dígitos")
        
        # Verifica se não são todos iguais
        if cpf_numbers == cpf_numbers[0] * 11:
            raise ValueError("CPF inválido")
        
        # Calcula primeiro dígito verificador
        soma = sum(int(cpf_numbers[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        # Calcula segundo dígito verificador
        soma = sum(int(cpf_numbers[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        # Verifica se os dígitos estão corretos
        if int(cpf_numbers[9]) != dv1 or int(cpf_numbers[10]) != dv2:
            raise ValueError("CPF inválido")
        
        return True

    @staticmethod
    def validate_password_policy(senha: str) -> bool:
        """
        Valida se a senha atende aos requisitos mínimos.
        Regra de negócio: mínimo 8 caracteres, pelo menos 1 letra e 1 dígito.
        """
        if len(senha) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        if not re.search(r'[a-zA-Z]', senha):
            raise ValueError("Senha deve conter pelo menos uma letra")
        if not re.search(r'\d', senha):
            raise ValueError("Senha deve conter pelo menos um dígito")
        return True

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Valida formato do email.
        Regra de negócio: deve ser um email válido.
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Formato de email inválido")
        return True

    @staticmethod
    def validate_nome(nome: str) -> bool:
        """
        Valida nome do usuário.
        Regra de negócio: não pode estar vazio e deve ter pelo menos 2 caracteres.
        """
        if not nome or len(nome.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        return True

    @staticmethod
    def init_system():
        """
        Inicializa o sistema criando banco e usuário admin padrão.
        Lógica de negócio: garantir que sistema tenha dados iniciais.
        """
        try:
            init_db_and_seed_sync()
            return {"success": True, "message": "Sistema inicializado com sucesso"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao inicializar sistema: {str(e)}"}

    @staticmethod
    def create_user(nome: str, email: str, cpf: str, senha: str, tipo_usuario: str, **kwargs) -> dict:
        """
        Cria um novo usuário da classe específica com validações de negócio.
        """
        try:
            # Validações de negócio
            UsuarioController.validate_nome(nome)
            UsuarioController.validate_email_format(email)
            UsuarioController.validate_cpf(cpf)
            UsuarioController.validate_password_policy(senha)

            # Verificar se email já existe (regra de negócio)
            existing_user = get_user_by_email_sync(email)
            if existing_user:
                raise ValueError(f"Email {email} já está cadastrado no sistema")

            # Verificar se CPF já existe (regra de negócio)
            existing_cpf_user = get_user_by_cpf_sync(cpf)
            if existing_cpf_user:
                raise ValueError(f"CPF {cpf} já está cadastrado no sistema")

            # Validar tipo de usuário e obter classe
            user_class = UserFactory.get_user_class(tipo_usuario)

            # Se for aluno, gerar matrícula automaticamente
            if tipo_usuario == "aluno":
                if "matricula" not in kwargs or not kwargs["matricula"]:
                    kwargs["matricula"] = UsuarioController.generate_unique_matricula()

            # Criar usuário da classe específica via repository
            user = create_user_specific_sync(
                user_class=user_class,
                nome=nome, 
                email=email, 
                cpf=cpf, 
                senha=senha,
                **kwargs
            )
            
            return {
                "success": True,
                "data": {
                    "id": user.id,
                    "nome": user.nome,
                    "email": user.email,
                    "cpf": user.cpf,
                    "tipo_usuario": UserFactory.get_user_type(user),
                    "ativo": user.ativo
                },
                "message": f"Usuário '{user.nome}' criado com sucesso"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro interno: {str(e)}"}

    @staticmethod
    def list_users() -> dict:
        """
        Lista todos os usuários do sistema com detalhes completos.
        """
        try:
            users_data = list_users_with_details_sync()
            
            # Transformar os dados para o formato esperado pela interface
            for user_data in users_data:
                # Mapear perfil para tipo_usuario
                if 'perfil' in user_data:
                    user_data['tipo_usuario'] = user_data['perfil']
                    del user_data['perfil']
            
            return {
                "success": True,
                "data": users_data,
                "message": f"{len(users_data)} usuário(s) encontrado(s)"
            }

        except Exception as e:
            return {"success": False, "message": f"Erro ao listar usuários: {str(e)}"}

    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """
        Busca usuário por ID com validações.
        """
        try:
            # Validação de negócio
            if user_id <= 0:
                raise ValueError(MSG_ID_INVALIDO)

            user = get_user_by_id_sync(user_id)
            if not user:
                return {"success": False, "message": MSG_USUARIO_NAO_ENCONTRADO}

            return {
                "success": True,
                "data": {
                    "id": user.id,
                    "nome": user.nome,
                    "email": user.email,
                    "tipo_usuario": UserFactory.get_user_type(user),
                    "ativo": user.ativo,
                },
                "message": "Usuário encontrado"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro ao buscar usuário: {str(e)}"}

    @staticmethod
    def update_user(user_id: int, nome: Optional[str] = None, 
                   email: Optional[str] = None, tipo_usuario: Optional[str] = None, **kwargs) -> dict:
        """
        Atualiza dados do usuário com validações de negócio.
        """
        try:
            # Validação de ID
            if user_id <= 0:
                raise ValueError(MSG_ID_INVALIDO)

            # Verificar se usuário existe
            existing_user = get_user_by_id_sync(user_id)
            if not existing_user:
                return {"success": False, "message": MSG_USUARIO_NAO_ENCONTRADO}

            # Validações de negócio
            if nome is not None:
                UsuarioController.validate_nome(nome)

            if email is not None:
                UsuarioController.validate_email_format(email)
                # Verificar se email já está em uso por outro usuário
                email_user = get_user_by_email_sync(email)
                if email_user and email_user.id != user_id:
                    raise ValueError(f"Email {email} já está em uso por outro usuário")

            # Validar tipo de usuário se fornecido
            if tipo_usuario is not None:
                try:
                    UserFactory.get_user_class(tipo_usuario)
                except ValueError:
                    raise ValueError(f"Tipo de usuário '{tipo_usuario}' inválido. Tipos aceitos: {list(TIPOS_USUARIO.keys())}")

            # Atualizar via repository/service
            updated_user = update_user_sync(user_id, nome=nome, email=email, tipo_usuario=tipo_usuario, **kwargs)
            
            if not updated_user:
                return {"success": False, "message": "Falha ao atualizar usuário"}
            
            return {
                "success": True,
                "data": {
                    "id": updated_user.id,
                    "nome": updated_user.nome,
                    "email": updated_user.email,
                    "tipo_usuario": UserFactory.get_user_type(updated_user),
                    "ativo": updated_user.ativo
                },
                "message": f"Usuário '{updated_user.nome}' atualizado com sucesso"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar usuário: {str(e)}"}

    @staticmethod
    def delete_user(user_id: int) -> dict:
        """
        Remove usuário com validações de negócio.
        """
        try:
            # Validação de ID
            if user_id <= 0:
                raise ValueError(MSG_ID_INVALIDO)

            # Verificar se usuário existe
            existing_user = get_user_by_id_sync(user_id)
            if not existing_user:
                return {"success": False, "message": MSG_USUARIO_NAO_ENCONTRADO}

            # Regra de negócio: não permitir exclusão do próprio admin se for o último
            if isinstance(existing_user, Administrador):
                # Contar quantos admins existem
                all_users = list_users_sync()
                admin_count = sum(1 for u in all_users if isinstance(u, Administrador) and u.ativo)
                if admin_count <= 1:
                    raise ValueError("Não é possível excluir o último administrador do sistema")

            # Excluir via repository/service
            success = delete_user_sync(user_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Usuário '{existing_user.nome}' excluído com sucesso"
                }
            else:
                return {"success": False, "message": "Falha ao excluir usuário"}

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro ao excluir usuário: {str(e)}"}

    @staticmethod
    def set_user_status(user_id: int, ativo: bool) -> dict:
        """
        Ativa/desativa usuário com validações de negócio.
        """
        try:
            # Validação de ID
            if user_id <= 0:
                raise ValueError(MSG_ID_INVALIDO)

            # Verificar se usuário existe
            existing_user = get_user_by_id_sync(user_id)
            if not existing_user:
                return {"success": False, "message": MSG_USUARIO_NAO_ENCONTRADO}

            # Regra de negócio: não permitir desativar o último admin
            if not ativo and isinstance(existing_user, Administrador):
                all_users = list_users_sync()
                active_admin_count = sum(1 for u in all_users if isinstance(u, Administrador) and u.ativo)
                if active_admin_count <= 1:
                    raise ValueError("Não é possível desativar o último administrador ativo")

            # Atualizar status via repository/service
            updated_user = set_user_active_sync(user_id, ativo)
            
            if not updated_user:
                return {"success": False, "message": "Falha ao alterar status do usuário"}
            
            status_text = "ativado" if ativo else "desativado"
            return {
                "success": True,
                "data": {
                    "id": updated_user.id,
                    "nome": updated_user.nome,
                    "ativo": updated_user.ativo
                },
                "message": f"Usuário '{updated_user.nome}' {status_text} com sucesso"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro ao alterar status: {str(e)}"}

    @staticmethod
    def change_password(user_id: int, nova_senha: str) -> dict:
        """
        Altera senha do usuário com validações de negócio.
        """
        try:
            # Validação de ID
            if user_id <= 0:
                raise ValueError(MSG_ID_INVALIDO)

            # Verificar se usuário existe
            existing_user = get_user_by_id_sync(user_id)
            if not existing_user:
                return {"success": False, "message": MSG_USUARIO_NAO_ENCONTRADO}

            # Validar nova senha
            UsuarioController.validate_password_policy(nova_senha)

            # Alterar senha via repository/service
            updated_user = change_user_password_sync(user_id, nova_senha)
            
            if not updated_user:
                return {"success": False, "message": "Falha ao alterar senha do usuário"}
            
            return {
                "success": True,
                "data": {
                    "id": updated_user.id,
                    "nome": updated_user.nome
                },
                "message": f"Senha do usuário '{updated_user.nome}' alterada com sucesso"
            }

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Erro ao alterar senha: {str(e)}"}

    @staticmethod
    def search_users(search_term: str) -> dict:
        """
        Busca usuários por nome ou email.
        Lógica de negócio: busca case-insensitive.
        """
        try:
            all_users = list_users_sync()
            search_term = search_term.lower().strip()
            
            if not search_term:
                # Se termo vazio, retorna todos
                filtered_users = all_users
            else:
                # Filtrar por nome ou email
                filtered_users = [
                    user for user in all_users
                    if search_term in user.nome.lower() or search_term in user.email.lower()
                ]

            users_data = [
                {
                    "id": user.id,
                    "nome": user.nome,
                    "email": user.email,
                    "tipo_usuario": UserFactory.get_user_type(user),
                    "ativo": user.ativo,
                }
                for user in filtered_users
            ]
            
            return {
                "success": True,
                "data": users_data,
                "message": f"{len(users_data)} usuário(s) encontrado(s)"
            }

        except Exception as e:
            return {"success": False, "message": f"Erro na busca: {str(e)}"}
    
    @staticmethod
    def get_all_users() -> dict:
        """Alias para list_users() para compatibilidade"""
        return UsuarioController.list_users()