"""Tela de Recepção - Cadastro de Paciente na Fila de Triagem

Esta interface Tkinter simula o fluxo de cadastro de pacientes na fila de triagem.
Integração real futura: chamar `paciente_service.create_patient` (assíncrono) via
threading ou asyncio + loop separado. Aqui usamos um service mock síncrono.

Requisitos atendidos:
- Janela 500x400 centralizada com título "CliniSys-Escola - Recepção"
- Título grande da tela
- Formulário com: Nome Completo, CPF, Data de Nascimento (DD/MM/AAAA)
- Botões: Cadastrar na Fila (principal), Limpar Campos
- Label de status colorido (verde sucesso, vermelho erro)
- Simulação de verificação de CPF duplicado
- Organização em classe `TelaRecepcao`
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

try:
    from .backend_integration import (
        Paciente, criar_paciente_sync,
        BackendError, ValidationError, ConflictError, test_connection
    )
except ImportError:
    from backend_integration import (
        Paciente, criar_paciente_sync,
        BackendError, ValidationError, ConflictError, test_connection
    )

# ===================== Service Layer com Backend Real ===================== #
class PacienteService:
    """Service que integra com o backend FastAPI real."""

    def create_patient(self, nome: str, cpf: str, data_nascimento: str) -> Paciente:
        """Cria paciente via backend com validação prévia."""
        # Validações frontend antes de enviar para backend
        if not nome or not nome.strip():
            raise ValueError("Nome é obrigatório.")
        if len(nome.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres.")
        if not cpf or not cpf.strip():
            raise ValueError("CPF é obrigatório.")
        if not data_nascimento or not data_nascimento.strip():
            raise ValueError("Data de nascimento é obrigatória.")
        
        # Validação básica de formato de data
        if not data_nascimento.count('/') == 2:
            raise ValueError("Data deve estar no formato DD/MM/AAAA.")
        
        try:
            return criar_paciente_sync(nome.strip(), cpf.strip(), data_nascimento.strip())
        except ValidationError as e:
            raise ValueError(str(e))
        except ConflictError as e:
            raise ValueError(str(e))
        except BackendError as e:
            raise ValueError(f"Erro do servidor: {e}")


# ===================== UI ===================== #
class TelaRecepcao(tk.Frame):
    def __init__(self, master: tk.Tk | tk.Toplevel, service: Optional[PacienteService] = None):
        super().__init__(master)
        self.master.title("CliniSys-Escola - Recepção")
        self.master.geometry("500x400")
        self._centralizar_janela(500, 400)
        self.service = service or PacienteService()

        # Variáveis de formulário
        self.var_nome = tk.StringVar()
        self.var_cpf = tk.StringVar()
        self.var_data_nasc = tk.StringVar()

        self._criar_layout()
        self._verificar_conexao()

    # --------------- Centralizar --------------- #
    def _centralizar_janela(self, largura: int, altura: int):
        self.master.update_idletasks()
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw // 2) - (largura // 2)
        y = (sh // 2) - (altura // 2)
        self.master.geometry(f"{largura}x{altura}+{x}+{y}")

    def _verificar_conexao(self):
        """Verifica se o backend está disponível."""
        if not test_connection():
            from tkinter import messagebox
            messagebox.showwarning(
                "Aviso", 
                "Não foi possível conectar ao backend.\n"
                "Verifique se o servidor está rodando em http://localhost:8000"
            )

    # --------------- Layout Principal --------------- #
    def _criar_layout(self):
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        # Título
        frame_titulo = ttk.Frame(self.master, padding=(15, 15, 15, 5))
        frame_titulo.grid(row=0, column=0, sticky="ew")
        lbl_titulo = ttk.Label(frame_titulo, text="Cadastro de Paciente na Fila de Triagem", font=("Segoe UI", 14, "bold"))
        lbl_titulo.pack()

        # Formulário
        frame_form = ttk.Frame(self.master, padding=(20, 10, 20, 10))
        frame_form.grid(row=1, column=0, sticky="nsew")
        for i in range(3):
            frame_form.rowconfigure(i, weight=0)
        frame_form.columnconfigure(1, weight=1)

        # Nome
        ttk.Label(frame_form, text="Nome Completo:").grid(row=0, column=0, sticky="w", pady=6)
        entry_nome = ttk.Entry(frame_form, textvariable=self.var_nome)
        entry_nome.grid(row=0, column=1, sticky="ew", pady=6)

        # CPF
        ttk.Label(frame_form, text="CPF:").grid(row=1, column=0, sticky="w", pady=6)
        entry_cpf = ttk.Entry(frame_form, textvariable=self.var_cpf)
        entry_cpf.grid(row=1, column=1, sticky="ew", pady=6)

        # Data de Nascimento
        ttk.Label(frame_form, text="Data de Nascimento (DD/MM/AAAA):").grid(row=2, column=0, sticky="w", pady=6)
        entry_data = ttk.Entry(frame_form, textvariable=self.var_data_nasc)
        entry_data.grid(row=2, column=1, sticky="ew", pady=6)

        # Botões
        frame_botoes = ttk.Frame(self.master, padding=(20, 5, 20, 5))
        frame_botoes.grid(row=2, column=0, sticky="ew")
        frame_botoes.columnconfigure(0, weight=1)
        frame_botoes.columnconfigure(1, weight=0)

        btn_cadastrar = ttk.Button(frame_botoes, text="Cadastrar na Fila", command=self._acao_cadastrar)
        btn_cadastrar.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=4)

        btn_limpar = ttk.Button(frame_botoes, text="Limpar Campos", command=self._limpar_campos)
        btn_limpar.grid(row=0, column=1, sticky="ew", ipady=4)

        # Status
        frame_status = ttk.Frame(self.master, padding=(15, 5, 15, 10))
        frame_status.grid(row=3, column=0, sticky="ew")
        self.lbl_status = ttk.Label(frame_status, text="", anchor="w")
        self.lbl_status.pack(fill="x")

        # Foco inicial
        entry_nome.focus_set()

    # --------------- Ações --------------- #
    def _acao_cadastrar(self):
        nome = self.var_nome.get().strip()
        cpf = self.var_cpf.get().strip()
        data_nasc = self.var_data_nasc.get().strip()

        # Reset status
        self._atualizar_status("", "black")

        try:
            paciente = self.service.create_patient(nome, cpf, data_nasc)
            self._atualizar_status("Paciente cadastrado com sucesso!", "green")
            self._limpar_campos()
        except ValueError as e:
            self._atualizar_status(f"Erro: {e}", "red")
        except Exception as e:
            self._atualizar_status(f"Erro inesperado: {e}", "red")

    def _limpar_campos(self):
        self.var_nome.set("")
        self.var_cpf.set("")
        self.var_data_nasc.set("")

    def _atualizar_status(self, mensagem: str, cor: str):
        # ttk.Label não altera cor de texto facilmente em alguns temas; usar style
        style = ttk.Style()
        style.configure("Status.TLabel", foreground=cor)
        self.lbl_status.configure(text=mensagem, style="Status.TLabel")


# ===================== Execução Standalone ===================== #
def main():
    root = tk.Tk()
    app = TelaRecepcao(root)
    # Não usar pack aqui: a classe já posiciona elementos diretamente no root via grid
    root.mainloop()


if __name__ == "__main__":
    main()
