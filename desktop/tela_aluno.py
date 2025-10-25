"""
Tela Principal do Aluno - CliniSys Desktop
Interface do módulo do aluno com acesso ao agendamento
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Sequence, Literal
import sys
import os

# Adiciona o backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.repositories.paciente_repository import list_patients_sync
from backend.repositories.usuario_repository import list_alunos_sync
from backend.db.init_db import create_tables_sync
from desktop.agendamento_view import TelaAgendarAtendimento
from desktop.registrar_procedimentos_view import TelaRegistrarProcedimentos
from backend.controllers.atendimento_controller import AtendimentoController


DEFAULT_FONT_FAMILY = "Segoe UI"
TITLE_FONT = (DEFAULT_FONT_FAMILY, 18, "bold")
INSTRUCTION_FONT = (DEFAULT_FONT_FAMILY, 10)
BUTTON_FONT = (DEFAULT_FONT_FAMILY, 11, "bold")
AnchorType = Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"]
ALERTA_TITULO = "Atenção"
DETAIL_LABEL_FONT = (DEFAULT_FONT_FAMILY, 10, "bold")
BTN_REFRESH_LABEL = "🔄 Atualizar"
COL_DATA_HORA = "Data/Hora"


class TelaAluno:
    """
    Tela principal do módulo do aluno.
    Permite visualizar pacientes e agendar atendimentos.
    """

    def __init__(
        self,
        parent,
        aluno_id: Optional[int] = None,
        aluno_nome: str | None = None
    ):
        """
        Inicializa a tela do aluno.
        
        Args:
            parent: Janela pai
            aluno_id: ID do aluno logado (opcional)
            aluno_nome: Nome do aluno logado (opcional)
        """
        # Garantir que as tabelas existem
        try:
            create_tables_sync()
        except Exception:
            pass  # Tabelas já existem
        
        self.window = tk.Toplevel(parent)
        self.window.title("CliniSys - Módulo do Aluno")
        self.window.geometry("900x600")
        try:
            self.window.state("zoomed")
        except tk.TclError:
            pass  # Fallback para ambientes sem suporte a zoom
        
        self.aluno_id: Optional[int] = aluno_id
        self.aluno_nome: str = aluno_nome or ""
        self.alunos = []
        self.pacientes = []
        self.agendamentos = []
        self.atendimentos_concluidos = []
        
        # Widgets
        self.tree_triados = None
        self.tree_agendados = None
        self.tree_concluidos = None
        self.titulo_label = None
        self.aluno_selector = None
        self.text_procedimentos = None
        self.text_observacoes = None
        
        # Criar interface primeiro
        self._criar_interface()
        
        # Centralizar depois de criar interface
        self._centralizar_janela(900, 600)
        
        # Carregar dados
        self._carregar_alunos()
        
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

    def _formatar_titulo(self) -> str:
        nome = self.aluno_nome or "Selecione o aluno"
        return f"👨‍⚕️ Bem-vindo, {nome}"

    def _atualizar_titulo(self) -> None:
        if self.titulo_label:
            self.titulo_label.configure(text=self._formatar_titulo())

        if self.aluno_nome:
            self.window.title(f"CliniSys - Módulo do Aluno: {self.aluno_nome}")
        else:
            self.window.title("CliniSys - Módulo do Aluno")

    def _carregar_alunos(self) -> None:
        try:
            self.alunos = list_alunos_sync()
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar alunos cadastrados:\n{exc}"
            )
            self.alunos = []
            self._atualizar_titulo()
            return

        if not self.alunos:
            messagebox.showwarning(
                ALERTA_TITULO,
                "Nenhum aluno cadastrado. Cadastre um aluno para prosseguir."
            )
            self.aluno_id = None
            self.aluno_nome = ""
            if self.aluno_selector:
                self.aluno_selector["values"] = []
            self._atualizar_titulo()
            self._carregar_pacientes(exibir_alerta_vazio=False)
            self._carregar_agendamentos()
            self._carregar_atendimentos_concluidos()
            return

        nomes = [aluno["nome"] for aluno in self.alunos]
        if self.aluno_selector:
            self.aluno_selector["values"] = nomes

        indice_atual = None
        if self.aluno_id is not None:
            for idx, aluno in enumerate(self.alunos):
                if aluno.get("id") == self.aluno_id:
                    indice_atual = idx
                    break

        if indice_atual is None:
            indice_atual = 0

        self._definir_aluno_atual(
            self.alunos[indice_atual],
            atualizar_combobox=True,
            atualizar_lista=True
        )

    def _definir_aluno_atual(
        self,
        aluno: Dict[str, object],
        *,
        atualizar_combobox: bool = False,
        atualizar_lista: bool = False
    ) -> None:
        aluno_id_val = aluno.get("id")
        if isinstance(aluno_id_val, int):
            self.aluno_id = aluno_id_val
        elif aluno_id_val is None:
            self.aluno_id = None
        else:
            try:
                self.aluno_id = int(aluno_id_val)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                self.aluno_id = None
        self.aluno_nome = str(aluno.get("nome") or "")
        self._atualizar_titulo()

        if atualizar_combobox and self.aluno_selector:
            nomes = [item["nome"] for item in self.alunos]
            try:
                indice = nomes.index(self.aluno_nome)
            except ValueError:
                indice = None
            if indice is not None:
                self.aluno_selector.current(indice)

        if atualizar_lista:
            self._carregar_pacientes(exibir_alerta_vazio=False)
            self._carregar_agendamentos()
            self._carregar_atendimentos_concluidos()

    def _on_aluno_selecionado(self, _event: tk.Event) -> None:  # pylint: disable=unused-argument
        if not self.aluno_selector:
            return
        nome_selecionado = self.aluno_selector.get()
        aluno_selecionado = next(
            (aluno for aluno in self.alunos if aluno.get("nome") == nome_selecionado),
            None,
        )
        if aluno_selecionado:
            self._definir_aluno_atual(
                aluno_selecionado,
                atualizar_combobox=False,
                atualizar_lista=True
            )

    def _garantir_aluno_selecionado(self) -> bool:
        if self.aluno_id is None:
            messagebox.showwarning(
                ALERTA_TITULO,
                "Selecione um aluno antes de continuar."
            )
            return False
        return True

    def _on_procedimento_registrado(self) -> None:
        self._carregar_pacientes(exibir_alerta_vazio=False)
        self._carregar_agendamentos()
        self._carregar_atendimentos_concluidos()

    def _on_agendamento_realizado(self) -> None:
        self._carregar_pacientes(exibir_alerta_vazio=False)
        self._carregar_agendamentos()

    def _criar_interface(self):
        """Cria a interface principal com visão unificada do aluno."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        titulo = ttk.Label(header_frame, text=self._formatar_titulo(), font=TITLE_FONT)
        titulo.pack(side="left")
        self.titulo_label = titulo

        ttk.Button(header_frame, text="Sair", command=self.window.destroy).pack(side="right")

        seletor_frame = ttk.Frame(main_frame)
        seletor_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            seletor_frame,
            text="Selecione o aluno para visualizar seus atendimentos:",
            font=INSTRUCTION_FONT,
        ).pack(side="left")

        self.aluno_selector = ttk.Combobox(seletor_frame, state="readonly", width=40)
        self.aluno_selector.pack(side="left", padx=(10, 0))
        self.aluno_selector.bind("<<ComboboxSelected>>", self._on_aluno_selecionado)

        listas_frame = ttk.Frame(main_frame)
        listas_frame.pack(fill="both", expand=True)
        listas_frame.rowconfigure(0, weight=1)
        for coluna in range(3):
            listas_frame.columnconfigure(coluna, weight=1)

        triados_frame = ttk.LabelFrame(
            listas_frame,
            text="Pacientes triados aguardando agendamento",
            padding="10",
        )
        triados_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ttk.Label(
            triados_frame,
            text="Selecione um paciente para abrir a tela de agendamento",
            font=INSTRUCTION_FONT,
        ).pack(anchor="w", pady=(0, 8))

        triados_tree_frame = ttk.Frame(triados_frame)
        triados_tree_frame.pack(fill="both", expand=True)

        triados_scroll_y = ttk.Scrollbar(triados_tree_frame, orient="vertical")
        triados_scroll_y.pack(side="right", fill="y")
        triados_scroll_x = ttk.Scrollbar(triados_frame, orient="horizontal")
        triados_scroll_x.pack(fill="x", pady=(4, 0))

        triados_columns: Sequence[tuple[str, int, AnchorType]] = [
            ("ID", 50, "center"),
            ("Nome", 220, "w"),
            ("CPF", 120, "center"),
            ("Data Nascimento", 120, "center"),
            ("Status", 130, "w"),
        ]

        self.tree_triados = ttk.Treeview(
            triados_tree_frame,
            columns=[col for col, _, _ in triados_columns],
            show="headings",
            yscrollcommand=triados_scroll_y.set,
            xscrollcommand=triados_scroll_x.set,
            selectmode="browse",
        )
        triados_scroll_y.config(command=self.tree_triados.yview)
        triados_scroll_x.config(command=self.tree_triados.xview)

        for coluna, largura, anchor in triados_columns:
            self.tree_triados.heading(coluna, text=coluna)
            self.tree_triados.column(coluna, width=largura, anchor=anchor)

        self.tree_triados.pack(side="left", fill="both", expand=True)
        self.tree_triados.bind("<Double-1>", self._on_duplo_clique)

        triados_btns = ttk.Frame(triados_frame)
        triados_btns.pack(fill="x", pady=(8, 0))

        ttk.Button(
            triados_btns,
            text="📅 Agendar Atendimento",
            command=self._agendar_atendimento,
            style="Accent.TButton",
        ).pack(side="left", padx=(0, 6))

        ttk.Button(triados_btns, text=BTN_REFRESH_LABEL, command=self._carregar_pacientes).pack(side="left")

        agendados_frame = ttk.LabelFrame(
            listas_frame,
            text="Consultas agendadas para este aluno",
            padding="10",
        )
        agendados_frame.grid(row=0, column=1, sticky="nsew", padx=4)

        agendados_tree_frame = ttk.Frame(agendados_frame)
        agendados_tree_frame.pack(fill="both", expand=True)

        agendados_scroll_y = ttk.Scrollbar(agendados_tree_frame, orient="vertical")
        agendados_scroll_y.pack(side="right", fill="y")
        agendados_scroll_x = ttk.Scrollbar(agendados_frame, orient="horizontal")
        agendados_scroll_x.pack(fill="x", pady=(4, 0))

        agendados_columns: Sequence[tuple[str, int, AnchorType]] = [
            ("ID", 60, "center"),
            (COL_DATA_HORA, 150, "center"),
            ("Tipo", 160, "w"),
            ("Paciente", 220, "w"),
        ]

        self.tree_agendados = ttk.Treeview(
            agendados_tree_frame,
            columns=[col for col, _, _ in agendados_columns],
            show="headings",
            yscrollcommand=agendados_scroll_y.set,
            xscrollcommand=agendados_scroll_x.set,
            selectmode="browse",
        )
        agendados_scroll_y.config(command=self.tree_agendados.yview)
        agendados_scroll_x.config(command=self.tree_agendados.xview)

        for coluna, largura, anchor in agendados_columns:
            self.tree_agendados.heading(coluna, text=coluna)
            self.tree_agendados.column(coluna, width=largura, anchor=anchor)

        self.tree_agendados.pack(side="left", fill="both", expand=True)

        agendados_btns = ttk.Frame(agendados_frame)
        agendados_btns.pack(fill="x", pady=(8, 0))

        ttk.Button(
            agendados_btns,
            text="📝 Registrar Procedimentos",
            command=self._registrar_procedimentos,
        ).pack(side="left", padx=(0, 6))

        ttk.Button(agendados_btns, text=BTN_REFRESH_LABEL, command=self._carregar_agendamentos).pack(side="left")

        concluidos_frame = ttk.LabelFrame(
            listas_frame,
            text="Consultas concluídas por este aluno",
            padding="10",
        )
        concluidos_frame.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        concluidos_tree_frame = ttk.Frame(concluidos_frame)
        concluidos_tree_frame.pack(fill="both", expand=True)

        concluidos_scroll_y = ttk.Scrollbar(concluidos_tree_frame, orient="vertical")
        concluidos_scroll_y.pack(side="right", fill="y")
        concluidos_scroll_x = ttk.Scrollbar(concluidos_frame, orient="horizontal")
        concluidos_scroll_x.pack(fill="x", pady=(4, 0))

        concluidos_columns: Sequence[tuple[str, int, AnchorType]] = [
            ("ID", 60, "center"),
            (COL_DATA_HORA, 150, "center"),
            ("Tipo", 160, "w"),
            ("Paciente", 220, "w"),
        ]

        self.tree_concluidos = ttk.Treeview(
            concluidos_tree_frame,
            columns=[col for col, _, _ in concluidos_columns],
            show="headings",
            yscrollcommand=concluidos_scroll_y.set,
            xscrollcommand=concluidos_scroll_x.set,
            selectmode="browse",
        )
        concluidos_scroll_y.config(command=self.tree_concluidos.yview)
        concluidos_scroll_x.config(command=self.tree_concluidos.xview)

        for coluna, largura, anchor in concluidos_columns:
            self.tree_concluidos.heading(coluna, text=coluna)
            self.tree_concluidos.column(coluna, width=largura, anchor=anchor)

        self.tree_concluidos.pack(side="left", fill="both", expand=True)
        self.tree_concluidos.bind("<<TreeviewSelect>>", self._on_concluido_selecionado)

        detalhes_frame = ttk.Frame(concluidos_frame)
        detalhes_frame.pack(fill="both", expand=True, pady=(10, 0))

        ttk.Label(detalhes_frame, text="Procedimentos registrados", font=DETAIL_LABEL_FONT).pack(
            anchor="w"
        )
        self.text_procedimentos = tk.Text(detalhes_frame, height=4, wrap="word", state=tk.DISABLED)
        self.text_procedimentos.pack(fill="both", expand=True, pady=(2, 8))

        ttk.Label(detalhes_frame, text="Observações", font=DETAIL_LABEL_FONT).pack(anchor="w")
        self.text_observacoes = tk.Text(detalhes_frame, height=3, wrap="word", state=tk.DISABLED)
        self.text_observacoes.pack(fill="both", expand=True)

        concluidos_btns = ttk.Frame(concluidos_frame)
        concluidos_btns.pack(fill="x", pady=(8, 0))

        ttk.Button(
            concluidos_btns,
            text=BTN_REFRESH_LABEL,
            command=self._carregar_atendimentos_concluidos,
        ).pack(side="left")

        self._configurar_estilos()

    def _configurar_estilos(self):
        """Configura estilos personalizados."""
        ttk.Style().configure("Accent.TButton", font=BUTTON_FONT)

    def _carregar_pacientes(self, exibir_alerta_vazio: bool = True):
        """Carrega lista de pacientes do banco."""
        tree_widget = self.tree_triados
        if tree_widget is None:
            return

        for item in tree_widget.get_children():
            tree_widget.delete(item)

        try:
            if self.aluno_id is None:
                if exibir_alerta_vazio:
                    messagebox.showinfo(
                        ALERTA_TITULO,
                        "Selecione um aluno para visualizar os pacientes."
                    )
                return
            
            # Carregar do banco
            # Mostrar apenas pacientes triados aguardando atendimento
            all_pacientes = list_patients_sync()
            self.pacientes = [
                p for p in all_pacientes
                if getattr(p, 'statusAtendimento', '') == 'Triado'
            ]
            
            # Preencher árvore
            for paciente in self.pacientes:
                tree_widget.insert(
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
            
            if not self.pacientes and exibir_alerta_vazio:
                messagebox.showinfo(
                    "Informação",
                    "Nenhum paciente triado disponível para agendamento."
                )
        
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar pacientes:\n{str(e)}"
            )

    def _carregar_agendamentos(self) -> None:
        """Carrega a lista de consultas agendadas para o aluno atual."""
        tree_widget = self.tree_agendados
        if tree_widget is None:
            return

        for item in tree_widget.get_children():
            tree_widget.delete(item)

        if self.aluno_id is None:
            self.agendamentos = []
            return

        try:
            resposta = AtendimentoController.listar_agendados_para_execucao(self.aluno_id)
            if not resposta.get("success"):
                raise RuntimeError(resposta.get("message", "Não foi possível carregar os agendamentos."))

            self.agendamentos = resposta.get("data", [])
            for atendimento in self.agendamentos:
                tree_widget.insert(
                    "",
                    "end",
                    iid=str(atendimento["id"]),
                    values=(
                        atendimento.get("id"),
                        atendimento.get("data_hora_formatada") or "-",
                        atendimento.get("tipo") or "-",
                        atendimento.get("paciente_nome") or "-",
                    ),
                )
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Erro", f"Erro ao carregar consultas agendadas:\n{exc}")
            self.agendamentos = []

    def _carregar_atendimentos_concluidos(self) -> None:
        """Carrega a lista de consultas concluídas e exibe detalhes."""
        tree_widget = self.tree_concluidos
        if tree_widget is None:
            return

        for item in tree_widget.get_children():
            tree_widget.delete(item)

        self._limpar_detalhes_concluido()

        if self.aluno_id is None:
            self.atendimentos_concluidos = []
            return

        try:
            resposta = AtendimentoController.listar_atendimentos_realizados(self.aluno_id)
            if not resposta.get("success"):
                raise RuntimeError(resposta.get("message", "Não foi possível carregar os atendimentos concluídos."))

            self.atendimentos_concluidos = resposta.get("data", [])
            for atendimento in self.atendimentos_concluidos:
                tree_widget.insert(
                    "",
                    "end",
                    iid=str(atendimento.get("id")),
                    values=(
                        atendimento.get("id"),
                        atendimento.get("data_hora_formatada") or "-",
                        atendimento.get("tipo") or "-",
                        atendimento.get("paciente_nome") or "-",
                    ),
                )
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Erro", f"Erro ao carregar consultas concluídas:\n{exc}")
            self.atendimentos_concluidos = []

    def _limpar_detalhes_concluido(self) -> None:
        self._preencher_texto(self.text_procedimentos, "")
        self._preencher_texto(self.text_observacoes, "")

    def _on_concluido_selecionado(self, _event: tk.Event) -> None:  # pylint: disable=unused-argument
        if self.tree_concluidos is None:
            return
        selection = self.tree_concluidos.selection()
        if not selection:
            self._limpar_detalhes_concluido()
            return

        selecionado_id = int(selection[0])
        atendimento = next(
            (item for item in self.atendimentos_concluidos if item.get("id") == selecionado_id),
            None,
        )

        if atendimento is None:
            self._limpar_detalhes_concluido()
            return

        self._preencher_texto(self.text_procedimentos, atendimento.get("procedimentos"))
        self._preencher_texto(self.text_observacoes, atendimento.get("observacoes"))

    def _preencher_texto(self, widget: Optional[tk.Text], conteudo: Optional[str]) -> None:
        if widget is None:
            return
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        texto = (conteudo or "Nenhuma informação registrada.").strip()
        if not texto:
            texto = "Nenhuma informação registrada."
        widget.insert(tk.END, texto)
        widget.configure(state=tk.DISABLED)

    def _agendar_atendimento(self):
        """Abre a tela de agendamento para o paciente selecionado."""
        try:
            if not self._garantir_aluno_selecionado():
                return
            tree_widget = self.tree_triados
            if tree_widget is None:
                messagebox.showerror(
                    "Erro",
                    "Lista de pacientes não foi inicializada corretamente."
                )
                return
            # Verificar se há seleção
            selecao = tree_widget.selection()
            if not selecao:
                messagebox.showwarning(
                    ALERTA_TITULO,
                    "Por favor, selecione um paciente da lista."
                )
                return
            
            # Obter dados do paciente selecionado
            item = tree_widget.item(selecao[0])
            valores = item["values"]
            paciente_id = int(valores[0])
            
            # Abrir tela de agendamento
            aluno_id = self.aluno_id
            if aluno_id is None:
                return
            TelaAgendarAtendimento(
                self.window,
                paciente_id,
                aluno_id,
                on_success=self._on_agendamento_realizado,
            )
        
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir tela de agendamento:\n{str(e)}"
            )

    def _on_duplo_clique(self, event):
        """Callback para duplo clique na lista."""
        handler = getattr(self, "_agendar_atendimento", None)
        if callable(handler):
            handler()

    def _registrar_procedimentos(self):
        """Abre a tela de registro de procedimentos."""
        if not self._garantir_aluno_selecionado():
            return
        tree_widget = self.tree_agendados
        if tree_widget is None:
            messagebox.showerror(
                "Erro",
                "Lista de consultas agendadas não foi inicializada corretamente."
            )
            return
        selecionados = tree_widget.selection()
        if not selecionados:
            messagebox.showwarning(
                ALERTA_TITULO,
                "Selecione uma consulta agendada para registrar os procedimentos."
            )
            return
        atendimento_id = int(selecionados[0])
        atendimento_dados = next(
            (item for item in self.agendamentos if item.get("id") == atendimento_id),
            None,
        )
        if atendimento_dados is None:
            messagebox.showerror(
                "Erro",
                "Não foi possível localizar os dados da consulta selecionada."
            )
            return
        aluno_id = self.aluno_id
        if aluno_id is None:
            return
        TelaRegistrarProcedimentos(
            self.window,
            aluno_id,
            self.aluno_nome,
            atendimento_preselecionado=atendimento_dados,
            on_success=self._on_procedimento_registrado
        )

# ===================== Função de Teste ===================== #

def main():
    """Função principal para teste standalone."""
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal
    
    # Teste com dados fictícios
    aluno_id = 1
    aluno_nome = "João da Silva"
    
    TelaAluno(root, aluno_id, aluno_nome)
    root.mainloop()


if __name__ == "__main__":
    main()
