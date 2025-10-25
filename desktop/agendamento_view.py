"""
Tela de Agendamento de Atendimento - CliniSys Desktop
Interface gráfica Tkinter para agendamento de consultas
"""

from __future__ import annotations

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional, Callable
from tkcalendar import Calendar  # pip install tkcalendar

# Adiciona o backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Imports do backend - padrão MVC
from backend.controllers.agendamento_controller import AgendamentoController
from backend.db.init_db import create_tables_sync


class TelaAgendarAtendimento:
    """
    Tela modal para agendamento de novo atendimento.
    Segue o Diagrama de Atividades e Diagrama de Sequência.
    """

    def __init__(
        self,
        parent,
        paciente_id: int,
        aluno_id: int,
        *,
        on_success: Optional[Callable[[], None]] = None,
    ):
        """
        Inicializa a tela de agendamento.
        
        Args:
            parent: Janela pai (tk.Tk ou tk.Toplevel)
            paciente_id: ID do paciente a ser atendido
            aluno_id: ID do aluno que realizará o atendimento
        """
        # Garantir que as tabelas existem
        try:
            create_tables_sync()
        except Exception:
            pass  # Tabelas já existem
        
        self.window = tk.Toplevel(parent)
        self.window.title("Agendar Novo Atendimento")
        self.window.geometry("600x700")
        
        # Dados
        self.paciente_id = paciente_id
        self.aluno_id = aluno_id
        self.paciente_dados = {}
        self.on_success = on_success
        
        # Widgets
        self.data_selecionada: Optional[date] = None
        self.horario_combo: Optional[ttk.Combobox] = None
        self.status_label: Optional[ttk.Label] = None
        self.calendar: Optional[Calendar] = None
        
        # Criar interface primeiro
        self._criar_interface()
        
        # Centralizar depois de criar interface
        self._centralizar_janela(600, 700)
        
        # Carregar dados do paciente
        self._carregar_dados_paciente()
        
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

    def _criar_interface(self):
        """Cria a interface gráfica completa."""
        # Frame principal com padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # ==================== TÍTULO ====================
        titulo = ttk.Label(
            main_frame,
            text="🗓️ Agendar Novo Atendimento",
            font=("Segoe UI", 18, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # ==================== INFORMAÇÕES DO PACIENTE ====================
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Paciente", padding="10")
        info_frame.pack(fill="x", pady=(0, 20))
        
        # Nome do paciente
        nome_frame = ttk.Frame(info_frame)
        nome_frame.pack(fill="x", pady=5)
        ttk.Label(nome_frame, text="Nome:", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.paciente_nome_label = ttk.Label(nome_frame, text="Carregando...", font=("Segoe UI", 10))
        self.paciente_nome_label.pack(side="left", padx=10)
        
        # CPF do paciente
        cpf_frame = ttk.Frame(info_frame)
        cpf_frame.pack(fill="x", pady=5)
        ttk.Label(cpf_frame, text="CPF:", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.paciente_cpf_label = ttk.Label(cpf_frame, text="Carregando...", font=("Segoe UI", 10))
        self.paciente_cpf_label.pack(side="left", padx=10)
        
        # ==================== SELEÇÃO DE DATA ====================
        data_frame = ttk.LabelFrame(main_frame, text="Selecionar Data", padding="10")
        data_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Instruções
        instrucoes = ttk.Label(
            data_frame,
            text="Selecione a data do atendimento (apenas dias úteis - segunda a sexta):",
            font=("Segoe UI", 9)
        )
        instrucoes.pack(pady=(0, 10))
        
        # Widget de calendário
        try:
            self.calendar = Calendar(
                data_frame,
                selectmode='day',
                date_pattern='dd/mm/yyyy',
                mindate=datetime.now().date(),
                weekendbackground='lightgray',
                weekendforeground='gray',
                font=("Segoe UI", 10)
            )
            self.calendar.pack(pady=10)
            
            # Bind do evento de seleção de data
            self.calendar.bind("<<CalendarSelected>>", self._on_data_selecionada)
        except Exception as e:
            # Fallback: Entry manual se tkcalendar não estiver disponível
            messagebox.showwarning(
                "Aviso",
                "Widget de calendário não disponível. Use entrada manual.\n"
                "Para melhor experiência, instale: pip install tkcalendar"
            )
            
            entry_frame = ttk.Frame(data_frame)
            entry_frame.pack(pady=10)
            
            ttk.Label(entry_frame, text="Data (DD/MM/AAAA):").pack(side="left", padx=5)
            self.data_entry = ttk.Entry(entry_frame, width=15)
            self.data_entry.pack(side="left", padx=5)
            
            ttk.Button(
                entry_frame,
                text="Confirmar Data",
                command=self._on_data_manual
            ).pack(side="left", padx=5)
        
        # ==================== SELEÇÃO DE HORÁRIO ====================
        horario_frame = ttk.LabelFrame(main_frame, text="Selecionar Horário", padding="10")
        horario_frame.pack(fill="x", pady=(0, 20))
        
        horario_info = ttk.Label(
            horario_frame,
            text="Horários disponíveis (horário comercial: 08:00 às 18:00):",
            font=("Segoe UI", 9)
        )
        horario_info.pack(pady=(0, 10))
        
        self.horario_combo = ttk.Combobox(
            horario_frame,
            state="readonly",
            width=20,
            font=("Segoe UI", 11)
        )
        self.horario_combo.pack(pady=5)
        self.horario_combo['values'] = []  # Inicialmente vazio
        
        # ==================== BOTÕES DE AÇÃO ====================
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill="x", pady=(10, 0))
        
        # Botão Confirmar
        btn_confirmar = ttk.Button(
            botoes_frame,
            text="✓ Confirmar Agendamento",
            command=self._confirmar_agendamento,
            style="Accent.TButton"
        )
        btn_confirmar.pack(side="left", padx=5, expand=True, fill="x")
        
        # Botão Cancelar
        btn_cancelar = ttk.Button(
            botoes_frame,
            text="✗ Cancelar",
            command=self.window.destroy
        )
        btn_cancelar.pack(side="left", padx=5, expand=True, fill="x")
        
        # ==================== BARRA DE STATUS ====================
        self.status_label = ttk.Label(
            main_frame,
            text="Aguardando seleção de data...",
            foreground="gray",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(pady=(10, 0))
        
        # Configurar estilos
        self._configurar_estilos()

    def _configurar_estilos(self):
        """Configura estilos personalizados."""
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

    def _carregar_dados_paciente(self):
        """Carrega e exibe os dados do paciente via Controller."""
        try:
            resultado = AgendamentoController.obter_dados_paciente(self.paciente_id)
            
            if resultado["success"]:
                self.paciente_dados = resultado["data"]
                self.paciente_nome_label.config(text=self.paciente_dados["nome"])
                self.paciente_cpf_label.config(text=self.paciente_dados["cpf"])
            else:
                messagebox.showerror("Erro", resultado["message"])
                self.window.destroy()
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados do paciente:\n{str(e)}")
            self.window.destroy()

    def _on_data_selecionada(self, event=None):
        """Callback quando uma data é selecionada no calendário."""
        try:
            # Obter data selecionada
            data_str = self.calendar.get_date()  # Formato: dd/mm/yyyy
            self.data_selecionada = datetime.strptime(data_str, "%d/%m/%Y").date()
            
            # Atualizar status
            self.status_label.config(
                text=f"Data selecionada: {data_str}. Carregando horários...",
                foreground="blue"
            )
            
            # Carregar horários disponíveis
            self._carregar_horarios(data_str)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar data:\n{str(e)}")

    def _on_data_manual(self):
        """Callback para entrada manual de data (fallback)."""
        try:
            data_str = self.data_entry.get().strip()
            
            # Validar formato
            datetime.strptime(data_str, "%d/%m/%Y")
            self.data_selecionada = datetime.strptime(data_str, "%d/%m/%Y").date()
            
            # Atualizar status
            self.status_label.config(
                text=f"Data selecionada: {data_str}. Carregando horários...",
                foreground="blue"
            )
            
            # Carregar horários
            self._carregar_horarios(data_str)
        
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")

    def _carregar_horarios(self, data_str: str):
        """Carrega horários disponíveis via Controller."""
        try:
            # Passar o aluno_id para filtrar horários já ocupados
            resultado = AgendamentoController.listar_horarios_disponiveis(data_str, self.aluno_id)
            
            if resultado["success"]:
                horarios = resultado["data"]
                self.horario_combo['values'] = horarios
                
                if horarios:
                    self.horario_combo.current(0)  # Selecionar primeiro horário
                    self.status_label.config(
                        text=f"{len(horarios)} horários disponíveis. Selecione um horário.",
                        foreground="green"
                    )
                else:
                    self.status_label.config(
                        text="Nenhum horário disponível para esta data.",
                        foreground="red"
                    )
            else:
                self.horario_combo['values'] = []
                self.status_label.config(
                    text=resultado["message"],
                    foreground="red"
                )
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar horários:\n{str(e)}")

    def _confirmar_agendamento(self):
        """Confirma o agendamento e chama o Controller."""
        try:
            # Validar seleções
            if not self.data_selecionada:
                messagebox.showwarning("Atenção", "Por favor, selecione uma data.")
                return
            
            horario_selecionado = self.horario_combo.get()
            if not horario_selecionado:
                messagebox.showwarning("Atenção", "Por favor, selecione um horário.")
                return
            
            # Preparar dados
            data_str = self.data_selecionada.strftime("%d/%m/%Y")
            
            dados = {
                "paciente_id": self.paciente_id,
                "aluno_id": self.aluno_id,
                "data_hora": {
                    "data": data_str,
                    "horario": horario_selecionado
                },
                "tipo": "Consulta Odontológica",
                "status": "Agendado"
            }
            
            # Atualizar status
            self.status_label.config(
                text="Processando agendamento...",
                foreground="blue"
            )
            self.window.update()
            
            # Chamar Controller
            resultado = AgendamentoController.agendar_novo_atendimento(dados)
            
            if resultado["success"]:
                # Sucesso: exibir mensagem e fechar janela
                messagebox.showinfo(
                    "Sucesso",
                    f"{resultado['message']}\n\n"
                    f"Paciente: {resultado['data']['paciente_nome']}\n"
                    f"Data/Hora: {resultado['data']['data_hora']}\n"
                    f"Status: {resultado['data']['status']}"
                )
                if callable(self.on_success):
                    try:
                        self.on_success()
                    except Exception as callback_exc:  # pragma: no cover
                        print(f"[WARN] Callback pós-agendamento falhou: {callback_exc}")
                self.window.destroy()
            else:
                # Erro: exibir mensagem sem fechar janela
                self.status_label.config(
                    text=resultado["message"],
                    foreground="red"
                )
                messagebox.showerror(
                    "Erro no Agendamento",
                    resultado["message"] + "\n\nPor favor, selecione outro horário."
                )
        
        except Exception as e:
            self.status_label.config(
                text=f"Erro: {str(e)}",
                foreground="red"
            )
            messagebox.showerror("Erro", f"Erro ao confirmar agendamento:\n{str(e)}")


# ===================== Função de Teste ===================== #

def main():
    """Função principal para teste standalone."""
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal
    
    # Teste com IDs fictícios
    # Em produção, esses IDs viriam da tela anterior
    paciente_id = 1
    aluno_id = 1
    
    tela = TelaAgendarAtendimento(root, paciente_id, aluno_id)
    root.mainloop()


if __name__ == "__main__":
    main()
