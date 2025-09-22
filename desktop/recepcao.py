"""
Tela de Recepção - Cadastro de Paciente na Fila de Triagem
"""
from __future__ import annotations

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional

# Adiciona o backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Imports diretos do backend - padrão MVC correto
from backend.controllers.paciente_controller_desktop import PacienteController


# ===================== Service Layer ===================== #
class PacienteService:
    """Service que usa o PacienteController."""

    def create_patient(self, nome: str, cpf: str, data_nascimento: str) -> dict:
        """Cria paciente via Controller com validação prévia."""
        # Validações básicas de formato
        if not nome or not nome.strip():
            raise ValueError("Nome é obrigatório.")
        if not cpf or not cpf.strip():
            raise ValueError("CPF é obrigatório.")
        if not data_nascimento or not data_nascimento.strip():
            raise ValueError("Data de nascimento é obrigatória.")
        
        # Validação básica de formato de data
        if data_nascimento.count('/') != 2:
            raise ValueError("Data deve estar no formato DD/MM/AAAA.")
        
        # Converte string para date
        try:
            day, month, year = data_nascimento.split('/')
            data_obj = date(int(year), int(month), int(day))
        except (ValueError, IndexError):
            raise ValueError("Data inválida. Use o formato DD/MM/AAAA com números válidos.")
        
        # Validação básica de data
        hoje = date.today()
        if data_obj > hoje:
            raise ValueError("Data de nascimento não pode ser no futuro.")
        
        # Validação de idade (não pode ser muito antiga)
        idade_anos = hoje.year - data_obj.year
        if idade_anos > 150:
            raise ValueError("Data de nascimento muito antiga.")
        
        # Usar Controller MVC
        result = PacienteController.create_patient(nome.strip(), cpf.strip(), data_obj)
        
        if not result["success"]:
            raise ValueError(result["message"])
        
        return result["data"]

    def check_cpf_exists(self, cpf: str) -> bool:
        """Verifica se CPF já existe no sistema."""
        try:
            result = PacienteController.search_patients_by_cpf(cpf.strip())
            return result["success"]
        except Exception:
            return False


# ===================== UI ===================== #
class TelaRecepcao(tk.Frame):
    def __init__(self, master: tk.Tk | tk.Toplevel, service: Optional[PacienteService] = None):
        super().__init__(master)
        self.master.title("CliniSys-Escola - Recepção")
        self.master.geometry("600x500")
        self._centralizar_janela(600, 500)
        self.service = service or PacienteService()

        # Variáveis de formulário
        self.var_nome = tk.StringVar()
        self.var_cpf = tk.StringVar()
        self.var_data_nasc = tk.StringVar()

        self._criar_layout()

    # --------------- Centralizar --------------- #
    def _centralizar_janela(self, largura: int, altura: int):
        self.master.update_idletasks()
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw // 2) - (largura // 2)
        y = (sh // 2) - (altura // 2)
        self.master.geometry(f"{largura}x{altura}+{x}+{y}")

    # --------------- Layout Principal --------------- #
    def _criar_layout(self):
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        # Título
        frame_titulo = ttk.Frame(self.master, padding=(20, 20, 20, 10))
        frame_titulo.grid(row=0, column=0, sticky="ew")
        
        lbl_titulo = ttk.Label(
            frame_titulo, 
            text="🏥 Cadastro de Paciente na Fila de Triagem", 
            font=("Segoe UI", 16, "bold")
        )
        lbl_titulo.pack()

        # Formulário
        frame_form = ttk.LabelFrame(self.master, text="Dados do Paciente", padding=(20, 15, 20, 15))
        frame_form.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        for i in range(3):
            frame_form.rowconfigure(i, weight=0)
        frame_form.columnconfigure(1, weight=1)

        # Nome
        ttk.Label(frame_form, text="Nome Completo:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=8
        )
        entry_nome = ttk.Entry(frame_form, textvariable=self.var_nome, font=("Segoe UI", 10))
        entry_nome.grid(row=0, column=1, sticky="ew", pady=8, padx=(10, 0))

        # CPF
        ttk.Label(frame_form, text="CPF:", font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=8
        )
        entry_cpf = ttk.Entry(frame_form, textvariable=self.var_cpf, font=("Segoe UI", 10))
        entry_cpf.grid(row=1, column=1, sticky="ew", pady=8, padx=(10, 0))

        # Data de Nascimento
        ttk.Label(frame_form, text="Data de Nascimento:", font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=8
        )
        frame_data = ttk.Frame(frame_form)
        frame_data.grid(row=2, column=1, sticky="ew", pady=8, padx=(10, 0))
        frame_data.columnconfigure(0, weight=1)
        
        entry_data = ttk.Entry(frame_data, textvariable=self.var_data_nasc, font=("Segoe UI", 10))
        entry_data.grid(row=0, column=0, sticky="ew")
        
        ttk.Label(frame_data, text="(DD/MM/AAAA)", foreground="gray").grid(
            row=0, column=1, sticky="e", padx=(5, 0)
        )

        # Botões
        frame_botoes = ttk.Frame(self.master, padding=(20, 10, 20, 10))
        frame_botoes.grid(row=2, column=0, sticky="ew")
        frame_botoes.columnconfigure(0, weight=1)
        frame_botoes.columnconfigure(1, weight=0)

        btn_cadastrar = ttk.Button(
            frame_botoes, 
            text="✅ Cadastrar na Fila", 
            command=self._acao_cadastrar,
            style="Action.TButton"
        )
        btn_cadastrar.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=8)

        btn_limpar = ttk.Button(
            frame_botoes, 
            text="🧹 Limpar Campos", 
            command=self._limpar_campos,
            style="Secondary.TButton"
        )
        btn_limpar.grid(row=0, column=1, sticky="ew", ipady=8)

        # Status
        frame_status = ttk.LabelFrame(self.master, text="Status", padding=(15, 10, 15, 10))
        frame_status.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        self.lbl_status = ttk.Label(
            frame_status, 
            text="💡 Preencha os campos e clique em 'Cadastrar na Fila'", 
            anchor="w",
            font=("Segoe UI", 10)
        )
        self.lbl_status.pack(fill="x")

        # Configurar estilos
        self._configurar_estilos()

        # Foco inicial
        entry_nome.focus_set()

    def _configurar_estilos(self):
        """Configura estilos personalizados."""
        style = ttk.Style()
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Secondary.TButton", font=("Segoe UI", 10))

    # --------------- Ações --------------- #
    def _acao_cadastrar(self):
        nome = self.var_nome.get().strip()
        cpf = self.var_cpf.get().strip()
        data_nasc = self.var_data_nasc.get().strip()

        # Reset status
        self._atualizar_status("🔄 Processando...", "blue")
        self.master.update()

        try:
            paciente = self.service.create_patient(nome, cpf, data_nasc)
            self._atualizar_status(
                f"✅ Paciente '{paciente['nome']}' cadastrado com sucesso! Status: {paciente['status_atendimento']}", 
                "green"
            )
            # Limpar campos sem alterar a mensagem de sucesso
            self._limpar_campos_silencioso()
        except ValueError as e:
            self._atualizar_status(f"❌ Erro: {e}", "red")
        except Exception as e:
            self._atualizar_status(f"💥 Erro inesperado: {e}", "red")

    def _limpar_campos(self):
        """Limpa os campos e atualiza o status."""
        self.var_nome.set("")
        self.var_cpf.set("")
        self.var_data_nasc.set("")
        self._atualizar_status("💡 Campos limpos. Pronto para novo cadastro.", "blue")

    def _limpar_campos_silencioso(self):
        """Limpa os campos sem alterar o status."""
        self.var_nome.set("")
        self.var_cpf.set("")
        self.var_data_nasc.set("")

    def _atualizar_status(self, mensagem: str, cor: str):
        """Atualiza o status com cor."""
        # Mapear cores para configurações do ttk
        color_map = {
            "green": "#28a745",
            "red": "#dc3545", 
            "blue": "#007bff",
            "orange": "#fd7e14",
            "black": "#000000"
        }
        
        style = ttk.Style()
        style.configure("Status.TLabel", foreground=color_map.get(cor, "#000000"))
        self.lbl_status.configure(text=mensagem, style="Status.TLabel")


# ===================== Execução Standalone ===================== #
def main():
    """Execução standalone da tela de recepção."""
    root = tk.Tk()
    try:
        app = TelaRecepcao(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao iniciar a aplicação:\n{str(e)}")


if __name__ == "__main__":
    main()
