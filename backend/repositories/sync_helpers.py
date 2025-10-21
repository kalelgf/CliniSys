"""
Helpers síncronos para acesso ao banco de dados SQLite
Evita problemas com asyncio em aplicações Tkinter
"""

import sqlite3
import os
from typing import Optional, Dict, Any
from datetime import datetime


def get_db_path() -> str:
    """Retorna o caminho do banco de dados."""
    return os.path.join(os.path.dirname(__file__), "..", "..", "desktop", "clinisys_uc_admin.db")


def get_user_by_id_sync_direct(user_id: int) -> Optional[Dict[str, Any]]:
    """Busca usuário por ID diretamente no SQLite (sem asyncio)."""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    cursor = conn.cursor()
    
    try:
        # Buscar usuário base
        cursor.execute("""
            SELECT id, nome, cpf, email, tipo_usuario
            FROM usuarios_sistema
            WHERE id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        user_dict = {
            'id': row['id'],
            'nome': row['nome'],
            'cpf': row['cpf'],
            'email': row['email'],
            'tipo': row['tipo_usuario'].capitalize(),  # Padronizar primeira letra maiúscula
            'clinica_id': None
        }
        
        # Se for aluno, buscar clinica_id da tabela alunos
        if row['tipo_usuario'].lower() == 'aluno':
            cursor.execute("""
                SELECT clinica_id
                FROM alunos
                WHERE id = ?
            """, (user_id,))
            
            aluno_row = cursor.fetchone()
            if aluno_row and aluno_row['clinica_id']:
                user_dict['clinica_id'] = aluno_row['clinica_id']
        
        return user_dict
    
    finally:
        conn.close()


def get_patient_by_id_sync_direct(patient_id: int) -> Optional[Dict[str, Any]]:
    """Busca paciente por ID diretamente no SQLite (sem asyncio)."""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Buscar paciente
        cursor.execute("""
            SELECT id, nome, cpf, dataNascimento, statusAtendimento, clinica_id
            FROM pacientes
            WHERE id = ?
        """, (patient_id,))
        
        row = cursor.fetchone()
        
        if row:
            # Converter data nascimento de string para datetime
            data_nasc_str = row['dataNascimento']
            if isinstance(data_nasc_str, str):
                data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
            else:
                data_nasc = data_nasc_str
            
            return {
                'id': row['id'],
                'nome': row['nome'],
                'cpf': row['cpf'],
                'dataNascimento': data_nasc,
                'statusAtendimento': row['statusAtendimento'],
                'clinica_id': row['clinica_id'] if 'clinica_id' in row.keys() else None
            }
        
        return None
    
    finally:
        conn.close()


def update_user_sync_direct(user_id: int, nome: Optional[str] = None, 
                            email: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Atualiza usuário diretamente no SQLite (sem asyncio).
    Retorna os dados atualizados do usuário ou None se não encontrado.
    """
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Verificar se usuário existe
        cursor.execute("SELECT id, tipo_usuario FROM usuarios_sistema WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        tipo_usuario = row['tipo_usuario']
        
        # Atualizar campos básicos na tabela usuarios_sistema
        updates = []
        params = []
        
        if nome is not None:
            updates.append("nome = ?")
            params.append(nome)
        
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        
        if updates:
            params.append(user_id)
            sql = f"UPDATE usuarios_sistema SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(sql, params)
        
        # Atualizar campos específicos por tipo
        if tipo_usuario.lower() == 'aluno':
            aluno_updates = []
            aluno_params = []
            
            if 'matricula' in kwargs and kwargs['matricula'] is not None:
                aluno_updates.append("matricula = ?")
                aluno_params.append(kwargs['matricula'])
            
            if 'telefone' in kwargs and kwargs['telefone'] is not None:
                aluno_updates.append("telefone = ?")
                aluno_params.append(kwargs['telefone'])
            
            if 'clinica_id' in kwargs and kwargs['clinica_id'] is not None:
                aluno_updates.append("clinica_id = ?")
                aluno_params.append(kwargs['clinica_id'])
            
            if aluno_updates:
                aluno_params.append(user_id)
                sql = f"UPDATE alunos SET {', '.join(aluno_updates)} WHERE id = ?"
                cursor.execute(sql, aluno_params)
        
        elif tipo_usuario.lower() == 'professor':
            prof_updates = []
            prof_params = []
            
            if 'especialidade' in kwargs and kwargs['especialidade'] is not None:
                prof_updates.append("especialidade = ?")
                prof_params.append(kwargs['especialidade'])
            
            if 'clinica_id' in kwargs and kwargs['clinica_id'] is not None:
                prof_updates.append("clinica_id = ?")
                prof_params.append(kwargs['clinica_id'])
            
            if prof_updates:
                prof_params.append(user_id)
                sql = f"UPDATE professores SET {', '.join(prof_updates)} WHERE id = ?"
                cursor.execute(sql, prof_params)
        
        elif tipo_usuario.lower() == 'recepcionista':
            if 'telefone' in kwargs and kwargs['telefone'] is not None:
                cursor.execute("UPDATE recepcionistas SET telefone = ? WHERE id = ?", 
                             (kwargs['telefone'], user_id))
        
        # Commit das alterações
        conn.commit()
        
        # Buscar dados atualizados
        return get_user_by_id_sync_direct(user_id)
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()


def get_user_by_email_sync_direct(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário por email diretamente no SQLite (sem asyncio).
    Retorna os dados do usuário ou None se não encontrado.
    """
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, nome, cpf, email, tipo_usuario
            FROM usuarios_sistema
            WHERE email = ?
        """, (email,))
        
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'nome': row['nome'],
                'cpf': row['cpf'],
                'email': row['email'],
                'tipo': row['tipo_usuario'].capitalize()
            }
        
        return None
    
    finally:
        conn.close()
