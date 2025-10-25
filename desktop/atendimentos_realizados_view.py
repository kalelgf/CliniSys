"""
Tela para visualizar atendimentos já realizados por um aluno.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
import sys
import os

# Garantir acesso ao backend quando executado via desktop
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.controllers.atendimento_controller import AtendimentoController  # noqa: E402


FONT_FAMILY = "Segoe UI"
HEADER_FONT = (FONT_FAMILY, 14, "bold")
LABEL_BOLD_FONT = (FONT_FAMILY, 10, "bold")


class TelaAtendimentosRealizados:
    """Janela modal para exibir histórico de atendimentos concluídos."""

    def __init__(self, parent: tk.Misc, aluno_id: int, aluno_nome: str):
        self.parent = parent
        self.aluno_id = aluno_id
        self.aluno_nome = aluno_nome

        self.window = tk.Toplevel(parent)
        self.window.title("Atendimentos Realizados")
        self.window.geometry("740x560")

        self.tree: Optional[ttk.Treeview] = None
        self.label_status: Optional[ttk.Label] = None
        self.label_paciente: Optional[ttk.Label] = None
        self.procedimentos_text: Optional[tk.Text] = None
        self.observacoes_text: Optional[tk.Text] = None
        self.atendimentos: List[Dict[str, Any]] = []

        self._criar_interface()
        self._centralizar_janela(740, 560)
        self._carregar_atendimentos()

        master_for_transient = parent if isinstance(parent, (tk.Tk, tk.Toplevel)) else None
        if master_for_transient is not None:
            self.window.transient(master_for_transient)
        self.window.grab_set()
        self.window.lift()
        self.window.focus_force()

    def _centralizar_janela(self, largura: int, altura: int) -> None:
        self.window.update_idletasks()
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x_pos = (sw // 2) - (largura // 2)
        y_pos = (sh // 2) - (altura // 2)
        self.window.geometry(f"{largura}x{altura}+{x_pos}+{y_pos}")

    def _criar_interface(self) -> None:
        main_frame = ttk.Frame(self.window, padding="16")
        main_frame.pack(fill="both", expand=True)

        header = ttk.Label(
            main_frame,
            text=f"Histórico de atendimentos realizados por {self.aluno_nome}",
            font=HEADER_FONT,
        )
        header.pack(pady=(0, 12))

        lista_frame = ttk.LabelFrame(main_frame, text="Atendimentos concluídos", padding="10")
        lista_frame.pack(fill="both", pady=(0, 12))

        tree_frame = ttk.Frame(lista_frame)
        tree_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "data", "tipo", "paciente"),
            show="headings",
            height=6,
            yscrollcommand=scrollbar.set,
            selectmode="browse",
        )
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("id", text="ID")
        self.tree.heading("data", text="Data/Hora")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("paciente", text="Paciente")

        self.tree.column("id", width=70, anchor="center")
        self.tree.column("data", width=170)
        self.tree.column("tipo", width=180)
        self.tree.column("paciente", width=240)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        detalhes_frame = ttk.LabelFrame(main_frame, text="Detalhes do atendimento", padding="10")
        detalhes_frame.pack(fill="both", expand=True)

        info_frame = ttk.Frame(detalhes_frame)
        info_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(info_frame, text="Paciente:", font=LABEL_BOLD_FONT).grid(row=0, column=0, sticky="w")
        self.label_paciente = ttk.Label(info_frame, text="-")
        self.label_paciente.grid(row=0, column=1, sticky="w")

        ttk.Label(info_frame, text="Status:", font=LABEL_BOLD_FONT).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.label_status = ttk.Label(info_frame, text="-")
        self.label_status.grid(row=1, column=1, sticky="w", pady=(4, 0))

        ttk.Label(detalhes_frame, text="Procedimentos realizados", font=LABEL_BOLD_FONT).pack(anchor="w")
        self.procedimentos_text = tk.Text(detalhes_frame, height=6, wrap="word", state=tk.DISABLED)
        self.procedimentos_text.pack(fill="both", expand=True, pady=(2, 8))

        ttk.Label(detalhes_frame, text="Observações", font=LABEL_BOLD_FONT).pack(anchor="w")
        self.observacoes_text = tk.Text(detalhes_frame, height=4, wrap="word", state=tk.DISABLED)
        self.observacoes_text.pack(fill="both", expand=True, pady=(2, 0))

        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill="x", pady=(12, 0))

        fechar_btn = ttk.Button(botoes_frame, text="Fechar", command=self.window.destroy)
        fechar_btn.pack(side="right")

    def _carregar_atendimentos(self) -> None:
        resposta = AtendimentoController.listar_atendimentos_realizados(self.aluno_id)
        if not resposta.get("success"):
            messagebox.showerror("Erro", resposta.get("message", "Erro desconhecido ao carregar atendimentos."))
            return

        self.atendimentos = resposta.get("data", [])
        if not self.atendimentos:
            messagebox.showinfo(
                "Informação",
                "Não há atendimentos concluídos para este aluno.",
            )

        self._popular_tree()

    def _popular_tree(self) -> None:
        if not self.tree:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for atendimento in self.atendimentos:
            self.tree.insert(
                "",
                "end",
                iid=str(atendimento["id"]),
                values=(
                    atendimento["id"],
                    atendimento.get("data_hora_formatada") or "-",
                    atendimento.get("tipo") or "-",
                    atendimento.get("paciente_nome") or "-",
                ),
            )

    def _on_tree_select(self, _event: tk.Event) -> None:  # pylint: disable=unused-argument
        atendimento = self._obter_atendimento_selecionado()
        if atendimento is None:
            return
        self._exibir_detalhes(atendimento)

    def _obter_atendimento_selecionado(self) -> Optional[Dict[str, Any]]:
        if not self.tree:
            return None
        selection = self.tree.selection()
        if not selection:
            return None
        atendimento_id = int(selection[0])
        for item in self.atendimentos:
            if item.get("id") == atendimento_id:
                return item
        return None

    def _exibir_detalhes(self, atendimento: Dict[str, Any]) -> None:
        if self.label_paciente:
            paciente_texto = str(atendimento.get("paciente_nome") or "-")
            self.label_paciente.configure(text=paciente_texto)

        if self.label_status:
            status = str(atendimento.get("status") or "-")
            self.label_status.configure(text=status)

        self._preencher_texto(self.procedimentos_text, atendimento.get("procedimentos"))
        self._preencher_texto(self.observacoes_text, atendimento.get("observacoes"))

    def _preencher_texto(self, widget: Optional[tk.Text], conteudo: Optional[Any]) -> None:
        if widget is None:
            return
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        texto = str(conteudo).strip() if conteudo else "Nenhuma informação registrada."
        widget.insert(tk.END, texto)
        widget.configure(state=tk.DISABLED)


__all__ = ["TelaAtendimentosRealizados"]
