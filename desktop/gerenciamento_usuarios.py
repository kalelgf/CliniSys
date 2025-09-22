"""
Tela de Gerenciamento de Usuários
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
from pathlib import Path
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.controllers.usuario_controller_desktop import UsuarioController

# Tipos de usuário disponíveis
TIPOS_USUARIO = {
    "administrador": "Administrador",
    "recepcionista": "Recepcionista", 
    "professor": "Professor",
    "aluno": "Aluno"
}


# ===================== Funções de Alto Nível (Desktop) ===================== #

def init_db_and_seed():
    """Inicializa banco e cria admin padrão se não existir."""
    result = UsuarioController.init_system()
    if not result["success"]:
        raise Exception(result["message"])


def list_users() -> List[dict]:
    """Lista todos os usuários do banco."""
    result = UsuarioController.list_users()
    if not result["success"]:
        raise Exception(result["message"])
    return result["data"]


def create_user(nome: str, email: str, cpf: str, senha: str, tipo_usuario: str, **kwargs) -> dict:
    """Cria um novo usuário."""
    result = UsuarioController.create_user(nome, email, cpf, senha, tipo_usuario, **kwargs)
    if not result["success"]:
        raise Exception(result["message"])
    return result["data"]


def get_user_detail(user_id: int) -> dict:
    """Busca detalhes completos de um usuário específico."""
    try:
        # Buscar na lista completa que já tem todos os detalhes
        usuarios = list_users()
        usuario = next((u for u in usuarios if u["id"] == user_id), None)
        
        if not usuario:
            raise Exception("Usuário não encontrado")
            
        return usuario
        
    except Exception as e:
        raise Exception(f"Erro ao buscar detalhes do usuário: {str(e)}")


def update_user_data(user_id: int, nome: str, email: str, tipo_usuario: str, **kwargs) -> dict:
    """Atualiza dados do usuário."""
    result = UsuarioController.update_user(user_id, nome=nome, email=email, tipo_usuario=tipo_usuario, **kwargs)
    if not result["success"]:
        raise Exception(result["message"])
    return result["data"]


def delete_user_data(user_id: int) -> bool:
    """Remove usuário."""
    result = UsuarioController.delete_user(user_id)
    if not result["success"]:
        raise Exception(result["message"])
    return True


def set_user_status(user_id: int, ativo: bool) -> dict:
    """Ativa/desativa usuário."""
    result = UsuarioController.set_user_status(user_id, ativo)
    if not result["success"]:
        raise Exception(result["message"])
    return result["data"]


def change_password(user_id: int, nova_senha: str) -> dict:
    """Altera senha do usuário."""
    result = UsuarioController.change_password(user_id, nova_senha)
    if not result["success"]:
        raise Exception(result["message"])
    return result["data"]


# ===================== Interface Gráfica ===================== #

class TelaGerenciamentoUsuarios:
    """Tela principal de gerenciamento de usuários."""
    
    def __init__(self, master):
        self.master = master
        self.master.title("CliniSys-Escola - Gerenciamento de Usuários")
        self.master.state('zoomed')  # Maximizar janela no Windows
        
        # Configurar variáveis
        self.var_busca = tk.StringVar()
        self.var_filtro_tipo_usuario = tk.StringVar(value="Todos")
        self.var_filtro_status = tk.StringVar(value="Todos")

        # Criar interface
        self._criar_widgets()
        
        # Inicializar banco e carregar dados
        self._inicializar_db()
        self._acao_buscar()

    def _inicializar_db(self):
        """Inicializa o banco de dados."""
        try:
            init_db_and_seed()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inicializar banco: {e}")

    def _criar_widgets(self):
        """Cria todos os widgets da interface."""
        # Frame principal
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar redimensionamento
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Criar componentes específicos
        self._criar_titulo(main_frame)
        self._criar_frame_busca(main_frame)
        self._criar_tabela(main_frame)
        self._criar_frame_botoes(main_frame)

    def _criar_titulo(self, parent):
        """Cria título da tela."""
        lbl_titulo = ttk.Label(parent, text="👥 Gerenciamento de Usuários", 
                              font=("Segoe UI", 16, "bold"))
        lbl_titulo.grid(row=0, column=0, pady=(0, 20), sticky="w")

    def _criar_frame_busca(self, parent):
        """Cria área de busca e filtros."""
        frame_busca = ttk.LabelFrame(parent, text="Filtros e Busca", padding="10")
        frame_busca.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Busca
        ttk.Label(frame_busca, text="🔍 Buscar:").grid(row=0, column=0, padx=(0, 5))
        entry_busca = ttk.Entry(frame_busca, textvariable=self.var_busca, width=30)
        entry_busca.grid(row=0, column=1, padx=(0, 10))
        entry_busca.bind('<KeyRelease>', lambda e: self._acao_buscar())
        
        btn_buscar = ttk.Button(frame_busca, text="Buscar", command=self._acao_buscar)
        btn_buscar.grid(row=0, column=2, padx=(0, 10))

    def _criar_tabela(self, parent):
        """Cria tabela de usuários."""
        # Frame para tabela
        frame_tabela = ttk.Frame(parent)
        frame_tabela.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configurar colunas
        colunas = ("ID", "Nome", "Email", "CPF", "Tipo", "Matrícula", "Status")
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=15)
        
        # Configurar cabeçalhos
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="Email")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Matrícula", text="Matrícula")
        self.tree.heading("Status", text="Status")
        
        # Configurar larguras
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Nome", width=180, anchor=tk.W)
        self.tree.column("Email", width=200, anchor=tk.W)
        self.tree.column("CPF", width=120, anchor=tk.CENTER)
        self.tree.column("Tipo", width=120, anchor=tk.CENTER)
        self.tree.column("Matrícula", width=100, anchor=tk.CENTER)
        self.tree.column("Status", width=80, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar redimensionamento
        frame_tabela.columnconfigure(0, weight=1)
        frame_tabela.rowconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

    def _criar_frame_botoes(self, parent):
        """Cria botões de ação."""
        frame_botoes = ttk.Frame(parent)
        frame_botoes.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        btn_adicionar = ttk.Button(frame_botoes, text="➕ Adicionar", command=self._abrir_modal_adicionar)
        btn_adicionar.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_editar = ttk.Button(frame_botoes, text="✏️ Editar", command=self._editar_usuario)
        btn_editar.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_excluir = ttk.Button(frame_botoes, text="🗑️ Excluir", command=self._excluir_usuario)
        btn_excluir.pack(side=tk.LEFT, padx=(0, 5))
        
        # Adicionar espaço e botão atualizar
        btn_atualizar = ttk.Button(frame_botoes, text="🔄 Atualizar", command=self._atualizar_lista)
        btn_atualizar.pack(side=tk.LEFT, padx=(20, 5))
        
        # Adicionar label de status
        self.lbl_status = ttk.Label(frame_botoes, text="", foreground="green")
        self.lbl_status.pack(side=tk.RIGHT, padx=(5, 0))

    def _acao_buscar(self):
        """Busca e atualiza lista de usuários."""
        try:
            usuarios = list_users()
            
            # Aplicar filtros
            termo = self.var_busca.get().strip().lower()
            if termo:
                usuarios = [u for u in usuarios if termo in u["nome"].lower() or termo in u["email"].lower()]
            
            self._atualizar_tabela(usuarios)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar usuários: {e}")

    def _atualizar_lista(self):
        """Atualiza a lista de usuários (botão Atualizar)."""
        try:
            # Mostrar mensagem de carregamento
            self.lbl_status.config(text="Atualizando lista...", foreground="blue")
            self.master.update()
            
            # Recarregar dados do banco
            self._acao_buscar()
            
            # Mostrar mensagem de sucesso
            self.lbl_status.config(text="Lista atualizada com sucesso!", foreground="green")
            
            # Limpar mensagem após 3 segundos
            self.master.after(3000, lambda: self.lbl_status.config(text=""))
            
        except Exception as e:
            self.lbl_status.config(text="Erro ao atualizar!", foreground="red")
            messagebox.showerror("Erro", f"Erro ao atualizar lista: {e}")

    def _atualizar_tabela(self, usuarios):
        """Atualiza tabela com lista de usuários."""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Inserir usuários
        for u in usuarios:
            status = "Ativo" if u["ativo"] else "Inativo"
            tipo_display = (TIPOS_USUARIO.get(u["tipo_usuario"], u["tipo_usuario"]) or u["tipo_usuario"]).title()
            cpf_display = u.get("cpf", "N/A")
            matricula_display = u.get("matricula", "N/A") if u["tipo_usuario"] == "aluno" else "-"
            self.tree.insert("", tk.END, values=(u["id"], u["nome"], u["email"], cpf_display, tipo_display, matricula_display, status))

    def _get_usuario_selecionado(self):
        """Retorna dados do usuário selecionado."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return None
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        return {
            'id': int(values[0]),
            'nome': values[1],
            'email': values[2],
            'cpf': values[3],
            'tipo_usuario': values[4].lower(),
            'matricula': values[5] if values[5] != "-" else None,
            'ativo': values[6] == "Ativo"
        }

    def _abrir_modal_adicionar(self):
        """Abre modal para adicionar usuário."""
        ModalAdicionarUsuario(self.master, self)

    def _editar_usuario(self):
        """Edita usuário selecionado."""
        usuario_data = self._get_usuario_selecionado()
        if usuario_data:
            try:
                user_detail = get_user_detail(usuario_data['id'])
                ModalEditarUsuario(self.master, self, user_detail)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")

    def _excluir_usuario(self):
        """Exclui usuário selecionado."""
        usuario_data = self._get_usuario_selecionado()
        if not usuario_data:
            return
            
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Excluir usuário '{usuario_data['nome']}'?"
        )
        
        if resposta:
            try:
                delete_user_data(usuario_data['id'])
                self._acao_buscar()
                messagebox.showinfo("Sucesso", "Usuário excluído.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    def adicionar_usuario(self, nome: str, email: str, cpf: str, senha: str, tipo_usuario: str, **kwargs):
        """Adiciona usuário."""
        try:
            usuario = create_user(nome, email, cpf, senha, tipo_usuario, **kwargs)
            self._acao_buscar()
            messagebox.showinfo("Sucesso", f"Usuário '{usuario['nome']}' adicionado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar: {e}")

    def editar_usuario(self, user_id: int, nome: str, email: str, tipo_usuario: str, **kwargs):
        """Edita usuário existente."""
        try:
            usuario = update_user_data(user_id, nome, email, tipo_usuario, **kwargs)
            self._acao_buscar()
            messagebox.showinfo("Sucesso", f"Usuário '{usuario['nome']}' editado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar: {e}")


# ===================== Modal Adicionar Usuário ===================== #

class ModalAdicionarUsuario:
    """Modal para adicionar novo usuário."""
    
    def __init__(self, master, parent):
        self.parent = parent
        self.window = tk.Toplevel(master)
        self.window.title("Adicionar Usuário")
        self.window.geometry("450x600")
        self.window.resizable(False, False)
        self.window.transient(master)
        self.window.grab_set()

        # Variáveis básicas
        self.var_nome = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_cpf = tk.StringVar()
        self.var_senha = tk.StringVar()
        self.var_tipo_usuario = tk.StringVar(value="recepcionista")
        
        # Variáveis específicas por tipo
        self.var_telefone = tk.StringVar()
        self.var_especialidade = tk.StringVar()
        self.var_matricula = tk.StringVar()
        self.var_clinica_id = tk.StringVar()

        # Referências para widgets dinâmicos
        self.widgets_dinamicos = {}

        self._criar_widgets()

    def _criar_widgets(self):
        """Cria widgets do modal."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        lbl_titulo = ttk.Label(main_frame, text="➕ Adicionar Usuário", 
                              font=("Segoe UI", 12, "bold"))
        lbl_titulo.pack(pady=(0, 20))

        # Campos básicos
        ttk.Label(main_frame, text="Nome:").pack(anchor=tk.W, pady=(0, 5))
        entry_nome = ttk.Entry(main_frame, textvariable=self.var_nome, width=40)
        entry_nome.pack(fill=tk.X, pady=(0, 10))
        entry_nome.focus()

        ttk.Label(main_frame, text="Email:").pack(anchor=tk.W, pady=(0, 5))
        entry_email = ttk.Entry(main_frame, textvariable=self.var_email, width=40)
        entry_email.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="CPF:").pack(anchor=tk.W, pady=(0, 5))
        entry_cpf = ttk.Entry(main_frame, textvariable=self.var_cpf, width=40)
        entry_cpf.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="Senha:").pack(anchor=tk.W, pady=(0, 5))
        entry_senha = ttk.Entry(main_frame, textvariable=self.var_senha, show="*", width=40)
        entry_senha.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="Tipo de Usuário:").pack(anchor=tk.W, pady=(0, 5))
        combo_tipo_usuario = ttk.Combobox(main_frame, textvariable=self.var_tipo_usuario, 
                                   values=list(TIPOS_USUARIO.keys()), 
                                   state="readonly", width=37)
        combo_tipo_usuario.pack(fill=tk.X, pady=(0, 10))
        combo_tipo_usuario.bind("<<ComboboxSelected>>", self._on_tipo_change)

        # Frame para campos dinâmicos
        self.frame_dinamicos = ttk.Frame(main_frame)
        self.frame_dinamicos.pack(fill=tk.X, pady=(0, 20))

        # Criar campos dinâmicos iniciais
        self._atualizar_campos_dinamicos()

        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X)

        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=self.window.destroy)
        btn_cancelar.pack(side=tk.RIGHT, padx=(5, 0))

        btn_salvar = ttk.Button(frame_botoes, text="Salvar", command=self._salvar)
        btn_salvar.pack(side=tk.RIGHT)

    def _on_tipo_change(self, event=None):
        """Callback quando o tipo de usuário muda."""
        self._atualizar_campos_dinamicos()

    def _atualizar_campos_dinamicos(self):
        """Atualiza campos dinâmicos baseado no tipo selecionado."""
        # Limpar widgets dinâmicos existentes
        for widget in self.widgets_dinamicos.values():
            widget.destroy()
        self.widgets_dinamicos.clear()

        tipo = self.var_tipo_usuario.get()
        
        if tipo == "recepcionista":
            self._criar_campo_telefone()
        elif tipo == "professor":
            self._criar_campo_especialidade()
            self._criar_campo_clinica()
        elif tipo == "aluno":
            # Matrícula será gerada automaticamente pelo sistema
            self._criar_campo_telefone()
            self._criar_campo_clinica()
        # Administrador não precisa de campos extras

    def _criar_campo_telefone(self):
        """Cria campo telefone."""
        lbl = ttk.Label(self.frame_dinamicos, text="Telefone:")
        lbl.pack(anchor=tk.W, pady=(0, 5))
        entry = ttk.Entry(self.frame_dinamicos, textvariable=self.var_telefone, width=40)
        entry.pack(fill=tk.X, pady=(0, 10))
        self.widgets_dinamicos["telefone_lbl"] = lbl
        self.widgets_dinamicos["telefone_entry"] = entry

    def _criar_campo_especialidade(self):
        """Cria campo especialidade."""
        lbl = ttk.Label(self.frame_dinamicos, text="Especialidade:")
        lbl.pack(anchor=tk.W, pady=(0, 5))
        entry = ttk.Entry(self.frame_dinamicos, textvariable=self.var_especialidade, width=40)
        entry.pack(fill=tk.X, pady=(0, 10))
        self.widgets_dinamicos["especialidade_lbl"] = lbl
        self.widgets_dinamicos["especialidade_entry"] = entry

    def _criar_campo_clinica(self):
        """Cria campo clínica."""
        lbl = ttk.Label(self.frame_dinamicos, text="ID da Clínica (opcional):")
        lbl.pack(anchor=tk.W, pady=(0, 5))
        entry = ttk.Entry(self.frame_dinamicos, textvariable=self.var_clinica_id, width=40)
        entry.pack(fill=tk.X, pady=(0, 10))
        self.widgets_dinamicos["clinica_lbl"] = lbl
        self.widgets_dinamicos["clinica_entry"] = entry

    def _salvar(self):
        """Salva novo usuário."""
        nome = self.var_nome.get().strip()
        email = self.var_email.get().strip()
        cpf = self.var_cpf.get().strip()
        senha = self.var_senha.get().strip()
        tipo_usuario = self.var_tipo_usuario.get()

        # Validações básicas
        if not nome or not email or not cpf or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        # Coletar campos específicos por tipo
        dados_extras = {}
        tipo_usuario = self.var_tipo_usuario.get()
        
        if tipo_usuario == "recepcionista":
            telefone = self.var_telefone.get().strip()
            if not telefone:
                messagebox.showerror("Erro", "Telefone é obrigatório para recepcionista.")
                return
            dados_extras["telefone"] = telefone
            
        elif tipo_usuario == "professor":
            especialidade = self.var_especialidade.get().strip()
            if not especialidade:
                messagebox.showerror("Erro", "Especialidade é obrigatória para professor.")
                return
            dados_extras["especialidade"] = especialidade
            clinica_id = self.var_clinica_id.get().strip()
            if clinica_id:
                try:
                    dados_extras["clinica_id"] = int(clinica_id)
                except ValueError:
                    messagebox.showerror("Erro", "ID da clínica deve ser um número.")
                    return
                    
        elif tipo_usuario == "aluno":
            telefone = self.var_telefone.get().strip()
            if not telefone:
                messagebox.showerror("Erro", "Telefone é obrigatório para aluno.")
                return
            # Matrícula será gerada automaticamente pelo sistema
            dados_extras["telefone"] = telefone
            clinica_id = self.var_clinica_id.get().strip()
            if clinica_id:
                try:
                    dados_extras["clinica_id"] = int(clinica_id)
                except ValueError:
                    messagebox.showerror("Erro", "ID da clínica deve ser um número.")
                    return

        # Salvar usuário
        self.parent.adicionar_usuario(nome, email, cpf, senha, tipo_usuario, **dados_extras)
        self.window.destroy()


# ===================== Modal Editar Usuário ===================== #

class ModalEditarUsuario:
    """Modal para editar usuário existente."""
    
    def __init__(self, master, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.window = tk.Toplevel(master)
        self.window.title("Editar Usuário")
        self.window.geometry("450x600")
        self.window.resizable(False, False)
        self.window.transient(master)
        self.window.grab_set()

        # Variáveis básicas
        self.var_nome = tk.StringVar(value=user_data.get("nome", ""))
        self.var_email = tk.StringVar(value=user_data.get("email", ""))
        self.var_tipo_usuario = tk.StringVar(value=user_data.get("tipo_usuario", "recepcionista"))
        
        # Variáveis específicas por tipo (carregadas dos dados existentes)
        self.var_telefone = tk.StringVar(value=user_data.get("telefone", ""))
        self.var_especialidade = tk.StringVar(value=user_data.get("especialidade", ""))
        self.var_matricula = tk.StringVar(value=user_data.get("matricula", ""))
        self.var_clinica_id = tk.StringVar(value=str(user_data.get("clinica_id", "")) if user_data.get("clinica_id") else "")

        # Referências para widgets dinâmicos
        self.widgets_dinamicos = {}

        self._criar_widgets()

    def _criar_widgets(self):
        """Cria widgets do modal."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        lbl_titulo = ttk.Label(main_frame, text="✏️ Editar Usuário", 
                              font=("Segoe UI", 12, "bold"))
        lbl_titulo.pack(pady=(0, 20))

        # Campos básicos
        ttk.Label(main_frame, text="Nome:").pack(anchor=tk.W, pady=(0, 5))
        entry_nome = ttk.Entry(main_frame, textvariable=self.var_nome, width=40)
        entry_nome.pack(fill=tk.X, pady=(0, 10))
        entry_nome.focus()

        ttk.Label(main_frame, text="Email:").pack(anchor=tk.W, pady=(0, 5))
        entry_email = ttk.Entry(main_frame, textvariable=self.var_email, width=40)
        entry_email.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="Tipo de Usuário:").pack(anchor=tk.W, pady=(0, 5))
        combo_tipo_usuario = ttk.Combobox(main_frame, textvariable=self.var_tipo_usuario, 
                                   values=list(TIPOS_USUARIO.keys()), 
                                   state="readonly", width=37)
        combo_tipo_usuario.pack(fill=tk.X, pady=(0, 10))
        combo_tipo_usuario.bind("<<ComboboxSelected>>", self._on_tipo_change)

        # Frame para campos dinâmicos
        self.frame_dinamicos = ttk.Frame(main_frame)
        self.frame_dinamicos.pack(fill=tk.X, pady=(0, 20))

        # Criar campos dinâmicos iniciais
        self._atualizar_campos_dinamicos()

        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X)

        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=self.window.destroy)
        btn_cancelar.pack(side=tk.RIGHT, padx=(5, 0))

        btn_salvar = ttk.Button(frame_botoes, text="Salvar", command=self._salvar)
        btn_salvar.pack(side=tk.RIGHT)

    def _on_tipo_change(self, event=None):
        """Callback quando o tipo de usuário muda."""
        self._atualizar_campos_dinamicos()

    def _atualizar_campos_dinamicos(self):
        """Atualiza campos dinâmicos baseado no tipo selecionado."""
        # Preservar valores atuais antes de destruir widgets
        valores_preservados = {}
        if hasattr(self, 'var_telefone'):
            valores_preservados['telefone'] = self.var_telefone.get()
        if hasattr(self, 'var_especialidade'):
            valores_preservados['especialidade'] = self.var_especialidade.get()
        if hasattr(self, 'var_matricula'):
            valores_preservados['matricula'] = self.var_matricula.get()
        if hasattr(self, 'var_clinica_id'):
            valores_preservados['clinica_id'] = self.var_clinica_id.get()
        
        # Limpar widgets dinâmicos existentes
        for widget in self.widgets_dinamicos.values():
            widget.destroy()
        self.widgets_dinamicos.clear()

        tipo = self.var_tipo_usuario.get()
        
        if tipo == "recepcionista":
            self._criar_campo_telefone()
        elif tipo == "professor":
            self._criar_campo_especialidade()
            self._criar_campo_clinica()
        elif tipo == "aluno":
            # Matrícula será gerada automaticamente pelo sistema
            self._criar_campo_telefone()
            self._criar_campo_clinica()
        # Administrador não precisa de campos extras
        
        # Restaurar valores preservados após recriar campos
        if hasattr(self, 'var_telefone') and 'telefone' in valores_preservados:
            self.var_telefone.set(valores_preservados['telefone'])
        if hasattr(self, 'var_especialidade') and 'especialidade' in valores_preservados:
            self.var_especialidade.set(valores_preservados['especialidade'])
        if hasattr(self, 'var_matricula') and 'matricula' in valores_preservados:
            self.var_matricula.set(valores_preservados['matricula'])
        if hasattr(self, 'var_clinica_id') and 'clinica_id' in valores_preservados:
            self.var_clinica_id.set(valores_preservados['clinica_id'])

    def _criar_campo_telefone(self):
        """Cria campo telefone."""
        lbl = ttk.Label(self.frame_dinamicos, text="Telefone:")
        lbl.pack(anchor=tk.W, pady=(0, 5))
        entry = ttk.Entry(self.frame_dinamicos, textvariable=self.var_telefone, width=40)
        entry.pack(fill=tk.X, pady=(0, 10))
        self.widgets_dinamicos["telefone_lbl"] = lbl
        self.widgets_dinamicos["telefone_entry"] = entry

    def _criar_campo_especialidade(self):
        """Cria campo especialidade."""
        lbl = ttk.Label(self.frame_dinamicos, text="Especialidade:")
        lbl.pack(anchor=tk.W, pady=(0, 5))
        entry = ttk.Entry(self.frame_dinamicos, textvariable=self.var_especialidade, width=40)
        entry.pack(fill=tk.X, pady=(0, 10))
        self.widgets_dinamicos["especialidade_lbl"] = lbl
        self.widgets_dinamicos["especialidade_entry"] = entry

    def _criar_campo_matricula(self):
        """Cria campo matrícula (readonly)."""
        lbl = ttk.Label(self.frame_dinamicos, text="Matrícula (gerada automaticamente):")
        lbl.pack(anchor=tk.W, pady=(0, 5))
        entry = ttk.Entry(self.frame_dinamicos, textvariable=self.var_matricula, width=40, state='readonly')
        entry.pack(fill=tk.X, pady=(0, 10))
        self.widgets_dinamicos["matricula_lbl"] = lbl
        self.widgets_dinamicos["matricula_entry"] = entry

    def _criar_campo_clinica(self):
        """Cria campo clínica."""
        lbl = ttk.Label(self.frame_dinamicos, text="ID da Clínica (opcional):")
        lbl.pack(anchor=tk.W, pady=(0, 5))
        entry = ttk.Entry(self.frame_dinamicos, textvariable=self.var_clinica_id, width=40)
        entry.pack(fill=tk.X, pady=(0, 10))
        self.widgets_dinamicos["clinica_lbl"] = lbl
        self.widgets_dinamicos["clinica_entry"] = entry

    def _salvar(self):
        """Salva alterações do usuário."""
        nome = self.var_nome.get().strip()
        email = self.var_email.get().strip()
        tipo_usuario = self.var_tipo_usuario.get()

        # Validações básicas
        if not nome or not email:
            messagebox.showerror("Erro", "Preencha nome e email.")
            return

        # Coletar campos específicos por tipo
        dados_extras = {}
        
        if tipo_usuario == "recepcionista":
            telefone = self.var_telefone.get().strip()
            if not telefone:
                messagebox.showerror("Erro", "Telefone é obrigatório para recepcionista.")
                return
            dados_extras["telefone"] = telefone
            
        elif tipo_usuario == "professor":
            especialidade = self.var_especialidade.get().strip()
            if not especialidade:
                messagebox.showerror("Erro", "Especialidade é obrigatória para professor.")
                return
            dados_extras["especialidade"] = especialidade
            clinica_id = self.var_clinica_id.get().strip()
            if clinica_id:
                try:
                    dados_extras["clinica_id"] = int(clinica_id)
                except ValueError:
                    messagebox.showerror("Erro", "ID da clínica deve ser um número.")
                    return
                    
        elif tipo_usuario == "aluno":
            matricula = self.var_matricula.get().strip()
            telefone = self.var_telefone.get().strip()
            if not telefone:
                messagebox.showerror("Erro", "Telefone é obrigatório para aluno.")
                return
            # Matrícula já existe e não pode ser alterada
            dados_extras["matricula"] = matricula
            dados_extras["telefone"] = telefone
            clinica_id = self.var_clinica_id.get().strip()
            if clinica_id:
                try:
                    dados_extras["clinica_id"] = int(clinica_id)
                except ValueError:
                    messagebox.showerror("Erro", "ID da clínica deve ser um número.")
                    return

        # Salvar alterações
        self.parent.editar_usuario(self.user_data["id"], nome, email, tipo_usuario, **dados_extras)
        self.window.destroy()


# ===================== Função Principal ===================== #

def main():
    """Função principal para testes."""
    root = tk.Tk()
    TelaGerenciamentoUsuarios(root)
    root.mainloop()


if __name__ == "__main__":
    main()