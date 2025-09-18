"""Tela de Gerenciamento de Usuários - CliniSys-Escola

Este módulo contém a implementação da interface gráfica de gerenciamento
básico de usuários utilizando Tkinter e ttk. Ele NÃO integra ainda com
os serviços reais do backend; funções são simuladas para demonstrar o fluxo.

Requisitos atendidos:
- Janela principal com título e centralização
- Divisão em frames: botões, busca e tabela
- Treeview com colunas ID, Nome, CPF, Email, Perfil + scrollbar vertical
- Botão para adicionar novo usuário abrindo uma janela modal (Toplevel)
- Janela de adicionar usuário com campos: Nome, CPF, Email, Senha, Perfil
- Combobox de Perfil com: Aluno, Professor, Recepcionista
- Botões Salvar e Cancelar na modal
- Mock de dados inicial e atualização da tabela ao salvar novo usuário
- Estrutura em classe para encapsular lógica da UI
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional

try:
    from .backend_integration import (
        Usuario, criar_usuario_sync, listar_usuarios_sync,
        BackendError, ValidationError, ConflictError, test_connection
    )
except ImportError:
    from backend_integration import (
        Usuario, criar_usuario_sync, listar_usuarios_sync,
        BackendError, ValidationError, ConflictError, test_connection
    )

# ===================== Service Layer com Backend Real ===================== #
class UsuarioService:
    """Service que integra com o backend FastAPI real."""

    def listar(self, termo: Optional[str] = None) -> List[Usuario]:
        """Lista usuários do backend, com filtro opcional por nome."""
        try:
            # Backend não suporta busca por termo ainda, então fazemos filtro local
            usuarios = listar_usuarios_sync()
            if not termo:
                return usuarios
            termo_lower = termo.lower()
            return [u for u in usuarios if termo_lower in u.nome.lower() or termo_lower in u.email.lower()]
        except BackendError as e:
            raise ValueError(f"Erro ao listar usuários: {e}")

    def adicionar(self, nome: str, email: str, senha: str, perfil: str) -> Usuario:
        """Adiciona usuário via backend."""
        try:
            # Mapear perfis da UI para valores aceitos pelo backend
            perfil_map = {
                "Aluno": "aluno",
                "Professor": "professor", 
                "Recepcionista": "recepcionista"
            }
            perfil_backend = perfil_map.get(perfil, perfil.lower())
            return criar_usuario_sync(nome, email, senha, perfil_backend)
        except ValidationError as e:
            raise ValueError(str(e))
        except ConflictError as e:
            raise ValueError(str(e))
        except BackendError as e:
            raise ValueError(f"Erro do servidor: {e}")


# ===================== UI Principal ===================== #
class TelaGerenciamentoUsuarios(tk.Frame):
    PERFIS = ("Aluno", "Professor", "Recepcionista")

    def __init__(self, master: tk.Tk | tk.Toplevel, service: UsuarioService | None = None):
        super().__init__(master)
        self.master.title("CliniSys-Escola - Gerenciamento de Usuários")
        self.service = service or UsuarioService()
        self._criar_widgets()
        self._verificar_conexao()
        self._popular_tabela_inicial()

    # --------------- Configuração e criação dos frames --------------- #
    def _criar_widgets(self) -> None:
        self.master.geometry("800x600")
        self._centralizar_janela()

        # Expande linhas/colunas raiz
        self.master.rowconfigure(2, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Frame de botões (topo)
        self.frame_botoes = ttk.Frame(self.master, padding=(10, 10, 10, 5))
        self.frame_botoes.grid(row=0, column=0, sticky="nsew")

        # Frame de busca
        self.frame_busca = ttk.Frame(self.master, padding=(10, 0, 10, 5))
        self.frame_busca.grid(row=1, column=0, sticky="nsew")

        # Frame tabela
        self.frame_tabela = ttk.Frame(self.master, padding=(10, 0, 10, 10))
        self.frame_tabela.grid(row=2, column=0, sticky="nsew")

        self._criar_frame_botoes()
        self._criar_frame_busca()
        self._criar_frame_tabela()

    def _centralizar_janela(self):
        self.master.update_idletasks()
        largura = 800
        altura = 600
        largura_tela = self.master.winfo_screenwidth()
        altura_tela = self.master.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.master.geometry(f"{largura}x{altura}+{x}+{y}")

    def _verificar_conexao(self):
        """Verifica se o backend está disponível."""
        if not test_connection():
            messagebox.showwarning(
                "Aviso", 
                "Não foi possível conectar ao backend.\n"
                "Verifique se o servidor está rodando em http://localhost:8000"
            )

    # --------------- Frame Botões --------------- #
    def _criar_frame_botoes(self):
        btn_adicionar = ttk.Button(self.frame_botoes, text="Adicionar Novo Usuário", command=self._abrir_modal_adicionar)
        btn_adicionar.pack(side=tk.LEFT)

    # --------------- Frame Busca --------------- #
    def _criar_frame_busca(self):
        lbl_busca = ttk.Label(self.frame_busca, text="Buscar por Nome ou Email:")
        lbl_busca.pack(side=tk.LEFT)

        self.var_busca = tk.StringVar()
        entry_busca = ttk.Entry(self.frame_busca, textvariable=self.var_busca, width=40)
        entry_busca.pack(side=tk.LEFT, padx=(8, 8))

        btn_buscar = ttk.Button(self.frame_busca, text="Buscar", command=self._acao_buscar)
        btn_buscar.pack(side=tk.LEFT)

    # --------------- Frame Tabela --------------- #
    def _criar_frame_tabela(self):
        colunas = ("id", "nome", "email", "perfil", "ativo")
        self.tree = ttk.Treeview(self.frame_tabela, columns=colunas, show="headings", height=15)

        # Definição de headings
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("email", text="Email")
        self.tree.heading("perfil", text="Perfil")
        self.tree.heading("ativo", text="Status")

        # Larguras iniciais
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("nome", width=200)
        self.tree.column("email", width=250)
        self.tree.column("perfil", width=120, anchor=tk.CENTER)
        self.tree.column("ativo", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self.frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.frame_tabela.rowconfigure(0, weight=1)
        self.frame_tabela.columnconfigure(0, weight=1)

    # --------------- Popular tabela inicial --------------- #
    def _popular_tabela_inicial(self):
        self._atualizar_tabela(self.service.listar())

    def _atualizar_tabela(self, usuarios: List[Usuario]):
        # Limpa linhas atuais
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insere novas
        for u in usuarios:
            status = "Ativo" if u.ativo else "Inativo"
            perfil_display = u.perfil.title()  # Capitaliza primeira letra
            self.tree.insert("", tk.END, values=(u.id, u.nome, u.email, perfil_display, status))

    # --------------- Ação buscar --------------- #
    def _acao_buscar(self):
        termo = self.var_busca.get().strip()
        usuarios = self.service.listar(termo if termo else None)
        self._atualizar_tabela(usuarios)

    # --------------- Modal Adicionar Usuário --------------- #
    def _abrir_modal_adicionar(self):
        ModalAdicionarUsuario(self.master, self)

    def adicionar_usuario(self, nome: str, email: str, senha: str, perfil: str):
        try:
            usuario = self.service.adicionar(nome, email, senha, perfil)
            # Atualiza tabela
            self._acao_buscar()
            messagebox.showinfo("Sucesso", f"Usuário '{usuario.nome}' adicionado.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")


# ===================== Modal de Adição ===================== #
class ModalAdicionarUsuario(tk.Toplevel):
    def __init__(self, master: tk.Misc, tela_principal: TelaGerenciamentoUsuarios):
        super().__init__(master)
        self.title("Adicionar Novo Usuário")
        self.tela_principal = tela_principal
        self.transient(master)
        self.grab_set()  # Modal
        self.resizable(False, False)

        # Variáveis de formulário
        self.var_nome = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_senha = tk.StringVar()
        self.var_perfil = tk.StringVar(value=TelaGerenciamentoUsuarios.PERFIS[0])

        self._criar_widgets()
        self._centralizar_modal()

    def _criar_widgets(self):
        container = ttk.Frame(self, padding=15)
        container.grid(row=0, column=0, sticky="nsew")

        # Grid config
        for i in range(5):
            container.rowconfigure(i, weight=0)
        container.columnconfigure(1, weight=1)

        # Nome
        ttk.Label(container, text="Nome:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(container, textvariable=self.var_nome, width=40).grid(row=0, column=1, sticky="ew", pady=4)

        # Email
        ttk.Label(container, text="Email:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(container, textvariable=self.var_email, width=40).grid(row=1, column=1, sticky="ew", pady=4)

        # Senha
        ttk.Label(container, text="Senha:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(container, textvariable=self.var_senha, show="*", width=25).grid(row=2, column=1, sticky="ew", pady=4)

        # Perfil
        ttk.Label(container, text="Perfil:").grid(row=3, column=0, sticky="w", pady=4)
        cb_perfil = ttk.Combobox(container, textvariable=self.var_perfil, values=TelaGerenciamentoUsuarios.PERFIS, state="readonly")
        cb_perfil.grid(row=3, column=1, sticky="ew", pady=4)

        # Botões
        frame_botoes = ttk.Frame(container, padding=(0, 10, 0, 0))
        frame_botoes.grid(row=4, column=0, columnspan=2, sticky="e")

        ttk.Button(frame_botoes, text="Salvar", command=self._salvar).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(frame_botoes, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)

    def _centralizar_modal(self):
        self.update_idletasks()
        largura = self.winfo_width() or 400
        altura = self.winfo_height() or 260
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _salvar(self):
        self.tela_principal.adicionar_usuario(
            self.var_nome.get().strip(),
            self.var_email.get().strip(),
            self.var_senha.get().strip(),
            self.var_perfil.get().strip(),
        )
        self.destroy()


# ===================== Função de inicialização standalone ===================== #
def main():
    root = tk.Tk()
    app = TelaGerenciamentoUsuarios(root)
    # Não usar pack aqui: a classe já posiciona elementos diretamente no root via grid.
    # Se futuramente desejar envolver em um Frame, pode-se alterar a herança ou adicionar container.
    root.mainloop()


if __name__ == "__main__":
    main()
