"""
Tela para Visualizar Fila de Triagem e Pacientes Cadastrados
Implementada seguindo o padrão MVC do projeto
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from backend.controllers.triagem_controller_desktop import TriagemController
from backend.controllers.paciente_controller_desktop import PacienteController
from desktop.triagem_view import TelaTriagem

class TelaVisualizarFilaTriagem(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("CliniSys-Escola - Fila de Triagem / Pacientes")
        self.master.geometry("700x400")
        self._centralizar_janela(700, 400)
        self.pack(fill="both", expand=True)
        self._criar_layout()
        self._carregar_pacientes()

    def _centralizar_janela(self, largura, altura):
        self.master.update_idletasks()
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw // 2) - (largura // 2)
        y = (sh // 2) - (altura // 2)
        self.master.geometry(f"{largura}x{altura}+{x}+{y}")

    def _criar_layout(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill="both", expand=True)
        titulo = ttk.Label(frame, text="👁️ Fila de Triagem / Pacientes Cadastrados", font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=(0, 10))
        # Duas listas: aguardando triagem e já triados
        lists_frame = ttk.Frame(frame)
        lists_frame.pack(fill="both", expand=True)

        # Aguardando triagem
        left = ttk.LabelFrame(lists_frame, text="Pacientes Aguardando Triagem", padding=8)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.tree_aguardando = ttk.Treeview(left, columns=("id", "nome", "cpf", "chegada"), show="headings", height=10)
        self.tree_aguardando.heading("id", text="ID")
        self.tree_aguardando.heading("nome", text="Nome")
        self.tree_aguardando.heading("cpf", text="CPF")
        self.tree_aguardando.heading("chegada", text="Chegada")
        self.tree_aguardando.column("id", width=40, anchor="center")
        self.tree_aguardando.column("nome", width=160)
        self.tree_aguardando.column("cpf", width=100, anchor="center")
        self.tree_aguardando.column("chegada", width=100, anchor="center")
        self.tree_aguardando.pack(fill="both", expand=True)

        btn_frame_left = ttk.Frame(left)
        btn_frame_left.pack(fill="x", pady=(8, 0))
        btn_triagem = ttk.Button(btn_frame_left, text="🩺 Realizar Triagem", command=self._realizar_triagem)
        btn_triagem.pack(side="left", padx=5)

        # Pacientes já triados
        right = ttk.LabelFrame(lists_frame, text="Pacientes Triados", padding=8)
        right.pack(side="left", fill="both", expand=True)

        self.tree_triaged = ttk.Treeview(right, columns=("id", "nome", "cpf", "prioridade", "chegada"), show="headings", height=10)
        self.tree_triaged.heading("id", text="ID")
        self.tree_triaged.heading("nome", text="Nome")
        self.tree_triaged.heading("cpf", text="CPF")
        self.tree_triaged.heading("prioridade", text="Prioridade")
        self.tree_triaged.heading("chegada", text="Chegada")
        self.tree_triaged.column("id", width=40, anchor="center")
        self.tree_triaged.column("nome", width=160)
        self.tree_triaged.column("cpf", width=100, anchor="center")
        self.tree_triaged.column("prioridade", width=100, anchor="center")
        self.tree_triaged.column("chegada", width=100, anchor="center")
        self.tree_triaged.pack(fill="both", expand=True)

        # Configurar cores de prioridade
        self.tree_triaged.tag_configure("alta", foreground="red")
        self.tree_triaged.tag_configure("media", foreground="orange")
        self.tree_triaged.tag_configure("baixa", foreground="green")

        btn_frame_right = ttk.Frame(right)
        btn_frame_right.pack(fill="x", pady=(8, 0))
        btn_refresh = ttk.Button(btn_frame_right, text="🔄 Atualizar", command=self._carregar_pacientes)
        btn_refresh.pack(side="left", padx=5)

        btn_fechar = ttk.Button(frame, text="Fechar", command=self.master.destroy, style="Secondary.TButton")
        btn_fechar.pack(pady=10)

    def _carregar_pacientes(self):
        """Carrega as listas de pacientes usando os controllers."""
        # Limpar ambas as listas caso existam
        try:
            self.tree_aguardando.delete(*self.tree_aguardando.get_children())
        except Exception:
            pass
        try:
            self.tree_triaged.delete(*self.tree_triaged.get_children())
        except Exception:
            pass

        # Carregar lista de aguardando triagem
        aguardando = TriagemController.list_fila_triagem()
        if aguardando["success"]:
            for paciente in aguardando["data"]:
                chegada = paciente.get("chegada", "-")
                try:
                    # Formatar chegada se for timestamp
                    dt = datetime.fromisoformat(chegada)
                    chegada = dt.strftime("%d/%m %H:%M")
                except:
                    pass

                self.tree_aguardando.insert("", "end", values=(
                    paciente["id"], paciente["nome"], paciente["cpf"], chegada
                ))

        # Carregar lista de triados
        triados = TriagemController.list_pacientes_triados()
        if triados["success"]:
            for paciente in triados["data"]:
                chegada = paciente.get("triagem_data", "-")
                try:
                    # Formatar chegada se for timestamp
                    dt = datetime.fromisoformat(chegada)
                    chegada = dt.strftime("%d/%m %H:%M")
                except:
                    pass

                prioridade = paciente.get("prioridade", "-")
                tag = "normal"
                if prioridade == "Alta":
                    tag = "alta"
                elif prioridade == "Média":
                    tag = "media"
                elif prioridade == "Baixa":
                    tag = "baixa"

                self.tree_triaged.insert("", "end", values=(
                    paciente["id"], paciente["nome"], paciente["cpf"], 
                    prioridade, chegada
                ), tags=(tag,))

    def _realizar_triagem(self):
        """Abre a janela de triagem para o paciente selecionado na lista de aguardando."""
        selecao = self.tree_aguardando.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um paciente da lista de aguardando triagem.")
            return

        item = self.tree_aguardando.item(selecao[0])
        paciente_id = int(item["values"][0])

        # Abrir tela de triagem/modal
        try:
            TelaTriagem(self.master, paciente_id, on_save=self._carregar_pacientes)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir triagem: {e}")
