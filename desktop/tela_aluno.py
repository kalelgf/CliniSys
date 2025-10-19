"""
Tela Principal do Aluno - CliniSys Desktop
Interface do módulo do aluno com acesso ao agendamento
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import sys
import os

# Adiciona o backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.repositories.paciente_repository import list_patients_sync
from backend.db.init_db import create_tables_sync
from desktop.agendamento_view import TelaAgendarAtendimento


class TelaAluno:
    """
    Tela principal do módulo do aluno.
    Permite visualizar pacientes e agendar atendimentos.
    """

    def __init__(self, parent, aluno_id: int, aluno_nome: str):
        """
        Inicializa a tela do aluno.
        
        Args:
            parent: Janela pai
            aluno_id: ID do aluno logado
            aluno_nome: Nome do aluno logado
        """
        # Garantir que as tabelas existem
        try:
            create_tables_sync()
        except Exception:
            pass  # Tabelas já existem
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"CliniSys - Módulo do Aluno: {aluno_nome}")
        self.window.geometry("900x600")
        
        self.aluno_id = aluno_id
        self.aluno_nome = aluno_nome
        self.pacientes = []
        
        # Widgets
        self.tree: Optional[ttk.Treeview] = None
        
        # Criar interface primeiro
        self._criar_interface()
        
        # Centralizar depois de criar interface
        self._centralizar_janela(900, 600)
        
        # Carregar dados
        self._carregar_pacientes()
        
        # Tornar modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Garantir que a janela fica em primeiro plano
        self.window.lift()
        self.window.focus_force()

    def _centralizar_janela(self, largura: int, altura: int):
        """Centraliza a janela na tela."""
        self.window.update_idletasks()
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = (sw // 2) - (largura // 2)
        y = (sh // 2) - (altura // 2)
        self.window.geometry(f"{largura}x{altura}+{x}+{y}")

    def _criar_interface(self):
        """Cria a interface gráfica."""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # ==================== CABEÇALHO ====================
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        titulo = ttk.Label(
            header_frame,
            text=f"👨‍⚕️ Bem-vindo, {self.aluno_nome}",
            font=("Segoe UI", 18, "bold")
        )
        titulo.pack(side="left")
        
        # Botão de logout
        btn_logout = ttk.Button(
            header_frame,
            text="Sair",
            command=self.window.destroy
        )
        btn_logout.pack(side="right")
        
        # ==================== LISTA DE PACIENTES ====================
        lista_frame = ttk.LabelFrame(main_frame, text="Pacientes Disponíveis", padding="10")
        lista_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Instrução
        instrucao = ttk.Label(
            lista_frame,
            text="Selecione um paciente para agendar atendimento:",
            font=("Segoe UI", 10)
        )
        instrucao.pack(pady=(0, 10))
        
        # Frame da Treeview com scrollbar
        tree_frame = ttk.Frame(lista_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        colunas = ("ID", "Nome", "CPF", "Data Nascimento", "Status")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=colunas,
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.config(command=self.tree.yview)
        
        # Configurar colunas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Data Nascimento", text="Data Nascimento")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nome", width=250)
        self.tree.column("CPF", width=120, anchor="center")
        self.tree.column("Data Nascimento", width=120, anchor="center")
        self.tree.column("Status", width=150)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Bind duplo clique
        self.tree.bind("<Double-1>", self._on_duplo_clique)
        
        # ==================== BOTÕES DE AÇÃO ====================
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill="x", pady=(10, 0))
        
        btn_agendar = ttk.Button(
            botoes_frame,
            text="📅 Agendar Atendimento",
            command=self._agendar_atendimento,
            style="Accent.TButton"
        )
        btn_agendar.pack(side="left", padx=5, expand=True, fill="x")
        
        btn_atualizar = ttk.Button(
            botoes_frame,
            text="🔄 Atualizar Lista",
            command=self._carregar_pacientes
        )
        btn_atualizar.pack(side="left", padx=5, expand=True, fill="x")
        
        # Configurar estilos
        self._configurar_estilos()

    def _configurar_estilos(self):
        """Configura estilos personalizados."""
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

    def _carregar_pacientes(self):
        """Carrega lista de pacientes do banco."""
        try:
            # Limpar árvore
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Carregar do banco
            self.pacientes = list_patients_sync()
            
            # Preencher árvore
            for paciente in self.pacientes:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        paciente.id,
                        paciente.nome,
                        paciente.cpf,
                        paciente.dataNascimento.strftime("%d/%m/%Y"),
                        paciente.statusAtendimento
                    )
                )
            
            if not self.pacientes:
                messagebox.showinfo(
                    "Informação",
                    "Nenhum paciente cadastrado no sistema."
                )
        
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar pacientes:\n{str(e)}"
            )

    def _agendar_atendimento(self):
        """Abre a tela de agendamento para o paciente selecionado."""
        try:
            # Verificar se há seleção
            selecao = self.tree.selection()
            if not selecao:
                messagebox.showwarning(
                    "Atenção",
                    "Por favor, selecione um paciente da lista."
                )
                return
            
            # Obter dados do paciente selecionado
            item = self.tree.item(selecao[0])
            valores = item["values"]
            paciente_id = int(valores[0])
            
            # Abrir tela de agendamento
            TelaAgendarAtendimento(self.window, paciente_id, self.aluno_id)
        
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir tela de agendamento:\n{str(e)}"
            )

    def _on_duplo_clique(self, event):
        """Callback para duplo clique na lista."""
        self._agendar_atendamento()


# ===================== Função de Teste ===================== #

def main():
    """Função principal para teste standalone."""
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal
    
    # Teste com dados fictícios
    aluno_id = 1
    aluno_nome = "João da Silva"
    
    tela = TelaAluno(root, aluno_id, aluno_nome)
    root.mainloop()


if __name__ == "__main__":
    main()
