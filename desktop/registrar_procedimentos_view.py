"""
Tela para registrar procedimentos realizados em atendimentos.

"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Callable, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.controllers.atendimento_controller import AtendimentoController  # noqa: E402


DEFAULT_FONT_FAMILY = "Segoe UI"
HEADER_FONT = (DEFAULT_FONT_FAMILY, 14, "bold")
DETAIL_FONT = (DEFAULT_FONT_FAMILY, 10)
ACCENT_BUTTON_FONT = (DEFAULT_FONT_FAMILY, 10, "bold")


class TelaRegistrarProcedimentos:
    """Janela modal que permite registrar procedimentos concluídos."""

    def __init__(
        self,
        parent: tk.Misc,
        aluno_id: int,
        aluno_nome: str,
        *,
        atendimento_preselecionado: Optional[Dict[str, Any]] = None,
        on_success: Optional[Callable[[], None]] = None,
    ):
        self.parent = parent
        self.aluno_id = aluno_id
        self.aluno_nome = aluno_nome
        self.on_success = on_success
        self.atendimento_preselecionado = atendimento_preselecionado

        self.window = tk.Toplevel(parent)
        self.window.title("Registrar Procedimentos")
        self.window.geometry("700x600")

        self.tree: Optional[ttk.Treeview] = None
        self.procedimentos_text: Optional[tk.Text] = None
        self.observacoes_text: Optional[tk.Text] = None
        self.atendimentos: List[Dict] = []

        self._criar_interface()
        self._centralizar_janela(700, 600)
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
        main_frame = ttk.Frame(self.window, padding="12")
        main_frame.pack(fill="both", expand=True)

        header = ttk.Label(
            main_frame,
            text=f"Registrar procedimentos para {self.aluno_nome}",
            font=HEADER_FONT,
        )
        header.pack(pady=(0, 6))

        if self.atendimento_preselecionado:
            paciente_nome = self.atendimento_preselecionado.get("paciente_nome") or "-"
            data_hora = self.atendimento_preselecionado.get("data_hora_formatada") or "-"
            tipo = self.atendimento_preselecionado.get("tipo") or "-"
            resumo = f"Consulta selecionada: {paciente_nome} • {tipo} • {data_hora}"
            ttk.Label(main_frame, text=resumo, font=DETAIL_FONT).pack(pady=(0, 10), anchor="w")

        lista_frame = ttk.LabelFrame(main_frame, text="Atendimentos agendados", padding="10")
        lista_frame.pack(fill="x")

        tree_frame = ttk.Frame(lista_frame)
        tree_frame.pack(fill="x")

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

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("data", width=160)
        self.tree.column("tipo", width=160)
        self.tree.column("paciente", width=220)

        self.tree.pack(fill="x")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_atendimento)

        form_frame = ttk.LabelFrame(main_frame, text="Procedimentos realizados", padding="10")
        form_frame.pack(fill="both", expand=True, pady=(15, 0))

        self.procedimentos_text = tk.Text(form_frame, height=8, wrap="word")
        self.procedimentos_text.pack(fill="both", expand=True)

        obs_label = ttk.Label(form_frame, text="Observações (opcional)")
        obs_label.pack(anchor="w", pady=(12, 4))

        self.observacoes_text = tk.Text(form_frame, height=4, wrap="word")
        self.observacoes_text.pack(fill="both", expand=True)

        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill="x", pady=(12, 0))

        registrar_btn = ttk.Button(
            botoes_frame,
            text="Registrar",
            command=self._registrar_procedimentos,
            style="Accent.TButton",
        )
        registrar_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        fechar_btn = ttk.Button(botoes_frame, text="Fechar", command=self.window.destroy)
        fechar_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

    ttk.Style().configure("Accent.TButton", font=ACCENT_BUTTON_FONT)

    def _carregar_atendimentos(self) -> None:
        if self.atendimento_preselecionado is not None:
            self.atendimentos = [self.atendimento_preselecionado]
        else:
            resposta = AtendimentoController.listar_agendados_para_execucao(self.aluno_id)
            if not resposta.get("success"):
                messagebox.showerror("Erro", resposta.get("message", "Erro desconhecido."))
                return

            self.atendimentos = resposta.get("data", [])
            if not self.atendimentos:
                messagebox.showinfo(
                    "Informação",
                    "Não há atendimentos agendados para registrar procedimentos.",
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
                    atendimento["tipo"],
                    atendimento.get("paciente_nome") or "-",
                ),
            )

        if self.atendimento_preselecionado and self.atendimentos:
            selecionado = str(self.atendimentos[0]["id"])
            self.tree.selection_set(selecionado)
            self.tree.focus(selecionado)

    def _on_select_atendimento(self, _event: tk.Event) -> None:  # pylint: disable=unused-argument
        if self.procedimentos_text:
            self.procedimentos_text.delete("1.0", "end")
        if self.observacoes_text:
            self.observacoes_text.delete("1.0", "end")

    def _obter_atendimento_selecionado(self) -> Optional[Dict]:
        if not self.tree:
            return None
        selection = self.tree.selection()
        if not selection:
            return None
        atendimento_id = int(selection[0])
        return next((item for item in self.atendimentos if item["id"] == atendimento_id), None)

    def _registrar_procedimentos(self) -> None:
        atendimento = self._obter_atendimento_selecionado()
        if atendimento is None:
            messagebox.showwarning(
                "Atenção",
                "Selecione um atendimento para registrar os procedimentos.",
            )
            return

        procedimentos = self.procedimentos_text.get("1.0", "end").strip() if self.procedimentos_text else ""
        observacoes = self.observacoes_text.get("1.0", "end").strip() if self.observacoes_text else None

        resposta = AtendimentoController.registrar_procedimentos(
            {
                "atendimento_id": atendimento["id"],
                "procedimentos": procedimentos,
                "observacoes": observacoes,
            }
        )

        if not resposta.get("success"):
            messagebox.showerror("Erro", resposta.get("message", "Erro ao registrar procedimentos."))
            return

        messagebox.showinfo("Sucesso", "Procedimentos registrados com sucesso.")
        if callable(self.on_success):
            try:
                self.on_success()
            except Exception as callback_exc:  # pragma: no cover - apenas log
                print(f"[WARN] Callback pós-registro falhou: {callback_exc}")
        self.atendimentos = [item for item in self.atendimentos if item["id"] != atendimento["id"]]
        self._popular_tree()
        if self.procedimentos_text:
            self.procedimentos_text.delete("1.0", "end")
        if self.observacoes_text:
            self.observacoes_text.delete("1.0", "end")

        if not self.atendimentos:
            self.window.destroy()
