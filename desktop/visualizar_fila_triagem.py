"""
Tela para Visualizar Fila de Triagem e Pacientes Cadastrados
"""
import tkinter as tk
from tkinter import ttk, messagebox
from backend.controllers.paciente_controller_desktop import PacienteController

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
        self.tree = ttk.Treeview(frame, columns=("id", "nome", "cpf", "data_nascimento", "status"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("cpf", text="CPF")
        self.tree.heading("data_nascimento", text="Nascimento")
        self.tree.heading("status", text="Status Atendimento")
        self.tree.pack(fill="both", expand=True)
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=180)
        self.tree.column("cpf", width=100, anchor="center")
        self.tree.column("data_nascimento", width=100, anchor="center")
        self.tree.column("status", width=150)
        btn_fechar = ttk.Button(frame, text="Fechar", command=self.master.destroy, style="Secondary.TButton")
        btn_fechar.pack(pady=10)

    def _carregar_pacientes(self):
        self.tree.delete(*self.tree.get_children())
        try:
            result = PacienteController.list_patients()
            if result["success"]:
                for paciente in result["data"]:
                    self.tree.insert("", "end", values=(
                        paciente["id"], paciente["nome"], paciente["cpf"], paciente["data_nascimento"], paciente["status_atendimento"]
                    ))
            else:
                messagebox.showinfo("Info", result["message"])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar pacientes: {e}")
