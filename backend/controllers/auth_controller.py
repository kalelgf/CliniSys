"""
Controller de Autenticação - CliniSys Desktop
Baseado no ControladorUsuario do clinica_odonto-main
Responsável pela autenticação e gerenciamento de sessão de usuários
"""

import os
import datetime
import jwt  # PyJWT
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from ..repositories.usuario_repository import get_user_by_cpf_sync
from ..core.security_simple import verify_password
from ..core.config import settings

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", settings.secret_key)
TOKEN_FILE = "usuario_token.jwt"


class AuthController:
    """Controller para gerenciamento de autenticação e sessão."""

    @staticmethod
    def fazer_login(dados_login: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Realiza login do usuário com CPF e senha.
        
        Args:
            dados_login: Dicionário com 'cpf' e 'senha'
            
        Returns:
            Dicionário com dados do usuário logado ou None se falhar
        """
        if not dados_login:
            return None
            
        cpf = dados_login.get("cpf", "").strip()
        senha = dados_login.get("senha", "")
        
        if not cpf or not senha:
            return None
        
        try:
            # Buscar usuário por CPF
            usuario = get_user_by_cpf_sync(cpf)
            
            if not usuario:
                print("Usuário não encontrado!")
                return None
            
            # Verificar se usuário está ativo
            if not usuario.ativo:
                print("Usuário inativo!")
                return None
            
            # Verificar senha
            if not verify_password(senha, usuario.senha_hash):
                print("Senha incorreta!")
                return None
            
            # Login bem-sucedido - gerar token JWT
            print(f"Login bem-sucedido! Tipo: {usuario.tipo_usuario}")
            
            # Preparar payload do token
            payload = {
                "cpf": usuario.cpf,
                "tipo_usuario": usuario.tipo_usuario,
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # expira em 24h
            }
            
            # Adicionar campos específicos por tipo
            if hasattr(usuario, 'clinica_id') and usuario.clinica_id:
                payload["clinica_id"] = usuario.clinica_id
            
            if hasattr(usuario, 'matricula') and usuario.matricula:
                payload["matricula"] = usuario.matricula
            
            try:
                # Gerar token JWT (PyJWT retorna string)
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                
                # Salvar token em arquivo
                with open(TOKEN_FILE, "w") as f:
                    f.write(token)
                
                return payload
                
            except Exception as e:
                print(f"Erro ao gerar token JWT: {e}")
                return None
                
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
            return None
    
    @staticmethod
    def usuario_logado() -> Optional[Dict[str, Any]]:
        """
        Verifica se há um usuário logado através do token JWT.
        
        Returns:
            Dicionário com dados do usuário logado ou None se não houver sessão válida
        """
        try:
            if not os.path.exists(TOKEN_FILE):
                return None
            
            with open(TOKEN_FILE, "r") as f:
                token = f.read().strip()
            
            if not token:
                return None
            
            # Decodificar token (PyJWT valida exp automaticamente)
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            return payload
            
        except jwt.ExpiredSignatureError:
            # Token expirado
            AuthController.deslogar()
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            AuthController.deslogar()
            return None
        except Exception as e:
            print(f"Erro ao verificar usuário logado: {e}")
            return None
    
    @staticmethod
    def deslogar() -> bool:
        """
        Remove a sessão do usuário (deleta arquivo de token).
        
        Returns:
            True se deslogou com sucesso, False caso contrário
        """
        try:
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            return True
        except Exception as e:
            print(f"Erro ao deslogar: {e}")
            return False
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """
        Valida formato do CPF (11 dígitos numéricos).
        
        Args:
            cpf: CPF a ser validado
            
        Returns:
            True se válido, False caso contrário
        """
        cpf_limpo = cpf.strip().replace(".", "").replace("-", "")
        return len(cpf_limpo) == 11 and cpf_limpo.isdigit()
    
    @staticmethod
    def validar_senha(senha: str) -> bool:
        """
        Valida formato da senha (mínimo 6 caracteres).
        
        Args:
            senha: Senha a ser validada
            
        Returns:
            True se válida, False caso contrário
        """
        return len(senha) >= 6

