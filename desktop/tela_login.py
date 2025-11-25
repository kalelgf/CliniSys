"""
Tela de Login - CliniSys Desktop
Interface de autenticação baseada no clinica_odonto-main
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable


class TelaLogin:
    """Tela de login do sistema CliniSys."""
    
    def __init__(self, parent: tk.Tk, on_login_success: Callable):
        """
        Inicializa a tela de login.
        
        Args:
            parent: Janela pai (tk.Tk)
            on_login_success: Callback chamado quando login é bem-sucedido
                              Recebe um dicionário com dados do usuário logado
        """
        self.parent = parent
        self.on_login_success = on_login_success
        self.usuario_logado = None
        
        self._criar_interface()
        self._configurar_estilos()
    
    def _criar_interface(self):
        """Cria a interface da tela de login."""
        # Limpar janela principal
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Configurar janela
        self.parent.title("CliniSys-Escola - Login")
        self.parent.geometry("500x400")
        self._centralizar_janela(500, 400)
        
        # Frame principal com fundo
        main_frame = ttk.Frame(self.parent, padding="20", style='Main.TFrame')
        main_frame.pack(fill="both", expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame, 
            text="🏥 CliniSys-Escola", 
            font=("Segoe UI", 24, "bold"),
            style='Title.TLabel'
        )
        titulo.pack(pady=(20, 10))
        
        subtitulo = ttk.Label(
            main_frame, 
            text="Sistema de Gestão de Clínicas Odontológicas", 
            font=("Segoe UI", 11),
            style='Subtitle.TLabel'
        )
        subtitulo.pack(pady=(0, 40))
        
        # Frame de login (card)
        login_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="40 30")
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Subtítulo do login
        subtitle_label = ttk.Label(
            login_frame, 
            text="Faça login na sua conta:", 
            style='Custom.TLabel',
            font=("Segoe UI", 11)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Campo CPF
        cpf_label = ttk.Label(
            login_frame, 
            text="CPF:", 
            style='Custom.TLabel',
            font=("Segoe UI", 10)
        )
        cpf_label.pack(anchor='w', pady=(0, 5))
        
        self.cpf_entry = ttk.Entry(
            login_frame, 
            width=35,
            font=("Segoe UI", 10)
        )
        self.cpf_entry.pack(pady=(0, 15))
        self.cpf_entry.bind('<Return>', lambda e: self.senha_entry.focus())
        
        # Campo Senha
        senha_label = ttk.Label(
            login_frame, 
            text="Senha:", 
            style='Custom.TLabel',
            font=("Segoe UI", 10)
        )
        senha_label.pack(anchor='w', pady=(0, 5))
        
        self.senha_entry = ttk.Entry(
            login_frame, 
            show='*', 
            width=35,
            font=("Segoe UI", 10)
        )
        self.senha_entry.pack(pady=(0, 25))
        self.senha_entry.bind('<Return>', lambda e: self.handle_login())
        
        # Botão de login
        self.login_button = ttk.Button(
            login_frame, 
            text="Entrar", 
            style='Login.TButton', 
            command=self.handle_login,
            cursor="hand2"
        )
        self.login_button.pack(fill='x', pady=(0, 10))
        
        # Focar no campo CPF ao iniciar
        self.cpf_entry.focus()
    
    def _configurar_estilos(self):
        """Configura estilos personalizados."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores
        light_blue = "#5D8DFF"
        dark_blue = "#2C5BB5"
        light_grey = "#F0F0F0"
        white = "#FFFFFF"
        
        # Estilos
        style.configure('Main.TFrame', background=light_grey)
        style.configure('Card.TFrame', background=white, relief='flat')
        style.configure('TLabel', background=light_grey)
        style.configure('Title.TLabel', background=light_grey, foreground=dark_blue)
        style.configure('Subtitle.TLabel', background=light_grey)
        style.configure('Custom.TLabel', background=white)
        
        style.configure(
            'Login.TButton', 
            background=light_blue, 
            foreground='white', 
            font=('Segoe UI', 11, 'bold'), 
            borderwidth=0, 
            relief="flat", 
            padding=(10, 8)
        )
        style.map('Login.TButton', background=[('active', dark_blue)])
        style.map('TEntry', fieldbackground=[('focus', '#E8F0FE')])
    
    def _centralizar_janela(self, largura: int, altura: int):
        """Centraliza a janela na tela."""
        self.parent.update_idletasks()
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw // 2) - (largura // 2)
        y = (sh // 2) - (altura // 2)
        self.parent.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def handle_login(self):
        """Processa o login do usuário."""
        from backend.controllers.auth_controller import AuthController
        
        cpf = self.cpf_entry.get().strip()
        senha = self.senha_entry.get()
        
        # Validar CPF
        if not AuthController.validar_cpf(cpf):
            messagebox.showerror(
                "Erro de Validação", 
                "CPF inválido! Digite 11 dígitos numéricos."
            )
            self.cpf_entry.focus()
            return
        
        # Validar senha
        if not AuthController.validar_senha(senha):
            messagebox.showerror(
                "Erro de Validação", 
                "Senha inválida! Mínimo de 6 caracteres."
            )
            self.senha_entry.focus()
            return
        
        # Preparar dados de login
        dados_login = {
            "cpf": cpf.replace(".", "").replace("-", ""),  # Remove formatação
            "senha": senha
        }
        
        # Tentar fazer login
        usuario_logado = AuthController.fazer_login(dados_login)
        
        if usuario_logado:
            self.usuario_logado = usuario_logado
            # Chamar callback de sucesso
            self.on_login_success(usuario_logado)
        else:
            messagebox.showerror(
                "Erro no Login", 
                "CPF ou senha inválidos!\n\nVerifique suas credenciais e tente novamente."
            )
            self.senha_entry.delete(0, tk.END)
            self.cpf_entry.focus()

