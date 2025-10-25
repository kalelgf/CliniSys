"""
Repository para operações de triagem - CliniSys Desktop
"""
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..db.database import get_db_sync
from ..models.paciente import Paciente


def ensure_triagem_table():
    """Garante que a tabela triagens existe no banco."""
    db = get_db_sync()
    cur = db.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS triagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                queixa TEXT,
                historia TEXT,
                medicamentos TEXT,
                alergias TEXT,
                pressao TEXT,
                fc TEXT,
                temp TEXT,
                fr TEXT,
                spo2 TEXT,
                dor TEXT,
                prioridade TEXT,
                sintomas TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
            )
        """)
        db.commit()
    finally:
        db.close()


def create_triagem(dados: Dict[str, Any]) -> int:
    """Cria um novo registro de triagem e atualiza status do paciente."""
    ensure_triagem_table()
    db = get_db_sync()
    cur = db.cursor()
    try:
        # Inserir triagem
        cur.execute(
            """INSERT INTO triagens (
                paciente_id, queixa, historia, medicamentos, alergias,
                pressao, fc, temp, fr, spo2, dor, prioridade, sintomas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados['paciente_id'], dados['queixa'], dados['historia'],
                dados['medicamentos'], dados['alergias'], dados['pressao'],
                dados['fc'], dados['temp'], dados['fr'], dados['spo2'],
                dados['dor'], dados['prioridade'], 
                ",".join(dados['sintomas']) if isinstance(dados['sintomas'], list) else dados['sintomas']
            )
        )
        triagem_id = cur.lastrowid
        if triagem_id is None:
            raise RuntimeError("Falha ao recuperar identificador da triagem recém-criada.")

        # Atualizar status do paciente
        cur.execute(
            "UPDATE pacientes SET statusAtendimento = ?, updated_at = ? WHERE id = ?",
            ("Triado", datetime.now().isoformat(), dados['paciente_id'])
        )
        
        db.commit()
        return int(triagem_id)

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_triagem_by_paciente(paciente_id: int) -> Optional[Dict[str, Any]]:
    """Busca a última triagem de um paciente."""
    ensure_triagem_table()
    db = get_db_sync()
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    try:
        cur.execute("""
            SELECT * FROM triagens 
            WHERE paciente_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1""", (paciente_id,))
        row = cur.fetchone()
        if not row:
            return None
        
        return dict(row)
    finally:
        db.close()


def list_triagens_pendentes() -> List[Dict[str, Any]]:
    """Lista pacientes aguardando triagem."""
    ensure_triagem_table()
    db = get_db_sync()
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    try:
        cur.execute("""
            SELECT p.*, COALESCE(t.created_at, p.created_at) as chegada
            FROM pacientes p
            LEFT JOIN triagens t ON t.paciente_id = p.id
            WHERE p.statusAtendimento = 'Aguardando Triagem'
            ORDER BY chegada ASC
        """)
        return [dict(row) for row in cur.fetchall()]
    finally:
        db.close()


def list_triagens_realizadas() -> List[Dict[str, Any]]:
    """Lista pacientes já triados com suas últimas triagens."""
    ensure_triagem_table()
    db = get_db_sync()
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    try:
        cur.execute("""
            SELECT 
                p.*,
                t.created_at as triagem_data,
                t.prioridade
            FROM pacientes p
            INNER JOIN triagens t ON t.paciente_id = p.id
            WHERE p.statusAtendimento = 'Triado'
            AND t.id = (
                SELECT id FROM triagens 
                WHERE paciente_id = p.id 
                ORDER BY created_at DESC 
                LIMIT 1
            )
            ORDER BY 
                CASE t.prioridade 
                    WHEN 'Alta' THEN 1
                    WHEN 'Média' THEN 2
                    WHEN 'Baixa' THEN 3
                    ELSE 4
                END,
                t.created_at ASC
        """)
        return [dict(row) for row in cur.fetchall()]
    finally:
        db.close()