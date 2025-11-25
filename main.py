#!/usr/bin/env python3
"""
CliniSys-Escola - Sistema Desktop
Launcher principal da aplicação desktop
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class CliniSysMain:
    """Interface principal do sistema CliniSys-Escola."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CliniSys-Escola - Sistema de Gestão")
        self.usuario_logado = None
        
        # Verificar se usuário já está logado
        from backend.controllers.auth_controller import AuthController
        self.usuario_logado = AuthController.usuario_logado()
        
        if self.usuario_logado:
            # Usuário já logado - mostrar tela principal
            self.root.geometry("600x400")
            self._centralizar_janela(600, 400)
            self._criar_interface()
        else:
            # Usuário não logado - mostrar tela de login
            self._mostrar_tela_login()
    
    def _centralizar_janela(self, largura: int, altura: int):
        """Centraliza a janela na tela."""
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw // 2) - (largura // 2)
        y = (sh // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def _get_permissoes(self) -> dict:
        """
        Retorna as permissões baseadas no tipo de usuário logado.
        
        Returns:
            Dicionário com permissões (gerenciar_usuarios, recepcao, fila_triagem, modulo_aluno)
        """
        if not self.usuario_logado:
            return {
                "gerenciar_usuarios": False,
                "recepcao": False,
                "fila_triagem": False,
                "modulo_aluno": False
            }
        
        tipo_usuario = self.usuario_logado.get("tipo_usuario", "").lower()
        
        # Admin: acesso completo
        if tipo_usuario == "administrador":
            return {
                "gerenciar_usuarios": True,
                "recepcao": True,
                "fila_triagem": True,
                "modulo_aluno": True
            }
        # Recepcionista: apenas recepção
        elif tipo_usuario == "recepcionista":
            return {
                "gerenciar_usuarios": False,
                "recepcao": True,
                "fila_triagem": False,
                "modulo_aluno": False
            }
        # Aluno: apenas consultar fila de triagem
        elif tipo_usuario == "aluno":
            return {
                "gerenciar_usuarios": False,
                "recepcao": False,
                "fila_triagem": True,
                "modulo_aluno": False
            }
        # Professor: Módulo do Aluno
        elif tipo_usuario == "professor":
            return {
                "gerenciar_usuarios": False,
                "recepcao": False,
                "fila_triagem": False,
                "modulo_aluno": True
            }
        # Padrão: sem permissões
        else:
            return {
                "gerenciar_usuarios": False,
                "recepcao": False,
                "fila_triagem": False,
                "modulo_aluno": False
            }
    
    def _criar_interface(self):
        """Cria a interface principal do sistema."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame, 
            text="🏥 CliniSys-Escola", 
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(pady=(0, 10))
        
        subtitulo = ttk.Label(
            main_frame, 
            text="Sistema de Gestão de Clínicas Odontológicas", 
            font=("Segoe UI", 12)
        )
        subtitulo.pack(pady=(0, 30))
        
        # Obter permissões do usuário
        permissoes = self._get_permissoes()
        
        # Frame dos botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill="x", pady=20)

        # Botão Gerenciamento de Usuários (apenas admin)
        if permissoes["gerenciar_usuarios"]:
            btn_usuarios = ttk.Button(
                botoes_frame,
                text="👥 Gerenciamento de Usuários",
                command=self._abrir_usuarios,
                style="Action.TButton"
            )
            btn_usuarios.pack(fill="x", pady=5, ipady=10)

        # Botão Recepção (admin e recepcionista)
        if permissoes["recepcao"]:
            btn_recepcao = ttk.Button(
                botoes_frame,
                text="🏥 Recepção - Cadastro de Pacientes",
                command=self._abrir_recepcao,
                style="Action.TButton"
            )
            btn_recepcao.pack(fill="x", pady=5, ipady=10)

        # Botão Fila de Triagem (admin e alunos)
        if permissoes["fila_triagem"]:
            btn_fila_triagem = ttk.Button(
                botoes_frame,
                text="👁️ Consultar Fila de Triagem",
                command=self._abrir_fila_triagem,
                style="Action.TButton"
            )
            btn_fila_triagem.pack(fill="x", pady=5, ipady=10)

        # Botão Módulo do Aluno (admin e professores)
        if permissoes["modulo_aluno"]:
            btn_aluno = ttk.Button(
                botoes_frame,
                text="👨‍⚕️ Módulo do Aluno - Agendamentos",
                command=self._abrir_modulo_aluno,
                style="Action.TButton"
            )
            btn_aluno.pack(fill="x", pady=5, ipady=10)

        # Verificar se há pelo menos um botão disponível
        if not any(permissoes.values()):
            mensagem_label = ttk.Label(
                botoes_frame,
                text="⚠️ Você não possui permissões para acessar nenhum módulo.",
                foreground="orange",
                font=("Segoe UI", 10)
            )
            mensagem_label.pack(pady=20)

        # Botão Sair
        btn_sair = ttk.Button(
            botoes_frame,
            text="❌ Sair",
            command=self._sair,
            style="Secondary.TButton"
        )
        btn_sair.pack(fill="x", pady=(20, 5), ipady=10)
        
        # Configurar estilos
        self._configurar_estilos()
        
        # Status com informações do usuário
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        if self.usuario_logado:
            usuario_info = f"👤 {self.usuario_logado.get('nome', 'Usuário')} ({self.usuario_logado.get('tipo_usuario', 'N/A')})"
            status_label = ttk.Label(
                status_frame,
                text=usuario_info,
                foreground="blue",
                font=("Segoe UI", 9)
            )
            status_label.pack()
        else:
            status_label = ttk.Label(
                status_frame,
                text="✅ Sistema pronto para uso",
                foreground="green"
            )
            status_label.pack()
    
    def _configurar_estilos(self):
        """Configura estilos personalizados."""
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=("Segoe UI", 11)
        )
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10)
        )
    
    def _abrir_usuarios(self):
        """Abre o módulo de gerenciamento de usuários."""
        try:
            from desktop.gerenciamento_usuarios import TelaGerenciamentoUsuarios
            usuarios_window = tk.Toplevel(self.root)
            TelaGerenciamentoUsuarios(usuarios_window)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir Gerenciamento de Usuários:\n{str(e)}"
            )
    
    def _abrir_recepcao(self):
        """Abre o módulo de recepção."""
        try:
            from desktop.recepcao import TelaRecepcao
            recepcao_window = tk.Toplevel(self.root)
            TelaRecepcao(recepcao_window)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir Recepção:\n{str(e)}"
            )
    
    def _abrir_fila_triagem(self):
        """Abre a tela de visualização da fila de triagem e pacientes cadastrados."""
        try:
            from desktop.visualizar_fila_triagem import TelaVisualizarFilaTriagem
            fila_window = tk.Toplevel(self.root)
            TelaVisualizarFilaTriagem(fila_window)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir Fila de Triagem/Pacientes:\n{str(e)}"
            )
    
    def _abrir_modulo_aluno(self):
        """Abre o módulo do aluno para agendamentos."""
        try:
            from desktop.tela_aluno import TelaAluno
            
            # Abrir tela do aluno permitindo a seleção manual do estudante
            TelaAluno(self.root)
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir Módulo do Aluno:\n{str(e)}"
            )
    
    def _mostrar_tela_login(self):
        """Mostra a tela de login."""
        from desktop.tela_login import TelaLogin
        TelaLogin(self.root, self._on_login_success)
    
    def _on_login_success(self, usuario_logado: dict):
        """Callback chamado quando login é bem-sucedido."""
        self.usuario_logado = usuario_logado
        
        # Limpar janela e mostrar tela principal
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("600x400")
        self._centralizar_janela(600, 400)
        self._criar_interface()
    
    def _sair(self):
        """Encerra a aplicação ou faz logout."""
        from backend.controllers.auth_controller import AuthController
        
        if self.usuario_logado:
            # Se estiver logado, perguntar se quer fazer logout ou sair
            resposta = messagebox.askyesnocancel(
                "Sair do Sistema",
                "Deseja fazer logout ou sair completamente?\n\n"
                "Sim = Logout (voltar para tela de login)\n"
                "Não = Sair completamente\n"
                "Cancelar = Cancelar"
            )
            
            if resposta is True:  # Logout
                AuthController.deslogar()
                self.usuario_logado = None
                # Limpar janela e mostrar tela de login
                for widget in self.root.winfo_children():
                    widget.destroy()
                self._mostrar_tela_login()
            elif resposta is False:  # Sair completamente
                self.root.destroy()
            # Se cancelar, não faz nada
        else:
            # Se não estiver logado, apenas sair
            if messagebox.askyesno("Confirmar", "Deseja realmente sair do sistema?"):
                self.root.destroy()
    
    def _on_closing(self):
        """Callback chamado ao fechar a aplicação."""
        from backend.controllers.auth_controller import AuthController
        
        # Fazer logout automático ao fechar
        if self.usuario_logado:
            AuthController.deslogar()
        
        self.root.destroy()
    
    def executar(self):
        """Executa a aplicação."""
        # Configurar callback para fechar janela
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()

def main():
    """Função principal do sistema."""
    try:
        app = CliniSysMain()
        app.executar()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro ao iniciar o sistema:\n{str(e)}")

if __name__ == "__main__":
    main()