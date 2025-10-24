"""
Tela de Triagem - Interface para triagem de pacientes
Implementada seguindo o padrão MVC do projeto
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Callable

from backend.controllers.triagem_controller_desktop import TriagemController
from backend.controllers.paciente_controller_desktop import PacienteController


class TelaTriagem(tk.Toplevel):
    def __init__(self, parent, paciente_id: int, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.paciente_id = paciente_id
        self.on_save = on_save
        self.title("Realizar Triagem de Paciente")
        self.geometry("800x700")
        self._criar_layout()
        self._carregar_paciente()
        self.transient(parent)
        self.grab_set()

    def _criar_layout(self):
        # Container principal
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        # Area scrollable: canvas + inner frame + scrollbar
        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(canvas_frame, borderwidth=0, highlightthickness=0)
        v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        # inner frame dentro do canvas onde os widgets serão colocados
        self._inner = ttk.Frame(self._canvas)
        self._window = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        # Bind para atualizar a região de scroll quando conteúdo mudar
        def _on_frame_configure(event):
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        def _on_canvas_configure(event):
            # Fazer com que o inner frame tenha a mesma largura do canvas
            canvas_width = event.width
            try:
                self._canvas.itemconfigure(self._window, width=canvas_width)
            except Exception:
                pass

        self._inner.bind("<Configure>", _on_frame_configure)
        self._canvas.bind("<Configure>", _on_canvas_configure)

        # suportar scroll com mouse wheel (Windows)
        def _on_mousewheel(event):
            # event.delta positivo/negativo dependendo da direção
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind apenas ao canvas para evitar interferência com outros widgets
        self._canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Cabeçalho com dados do paciente
        self.header = ttk.LabelFrame(self._inner, text="Paciente em Triagem", padding=10)
        self.header.pack(fill="x", pady=(0, 10))
        self.lbl_nome = ttk.Label(self.header, text="Nome: -")
        self.lbl_nome.grid(row=0, column=0, sticky="w")
        self.lbl_cpf = ttk.Label(self.header, text="CPF: -")
        self.lbl_cpf.grid(row=0, column=1, sticky="w", padx=20)
        self.lbl_idade = ttk.Label(self.header, text="Idade: -")
        self.lbl_idade.grid(row=0, column=2, sticky="w", padx=20)

        # Anamnese
        ana = ttk.LabelFrame(self._inner, text="Anamnese e Queixa Principal", padding=10)
        ana.pack(fill="x", pady=(0, 10))
        ttk.Label(ana, text="Queixa Principal Detalhada").pack(anchor="w")
        self.txt_queixa = tk.Text(ana, height=4)
        self.txt_queixa.pack(fill="x", pady=4)

        ttk.Label(ana, text="História da Doença Atual").pack(anchor="w")
        self.txt_historia = tk.Text(ana, height=3)
        self.txt_historia.pack(fill="x", pady=4)

        meds_frame = ttk.Frame(ana)
        meds_frame.pack(fill="x", pady=(4, 0))
        ttk.Label(meds_frame, text="Medicamentos em Uso:").grid(row=0, column=0, sticky="w")
        self.entry_meds = ttk.Entry(meds_frame)
        self.entry_meds.grid(row=0, column=1, sticky="ew", padx=(8,0))
        ttk.Label(meds_frame, text="Alergias Conhecidas:").grid(row=1, column=0, sticky="w", pady=(6,0))
        self.entry_alerg = ttk.Entry(meds_frame)
        self.entry_alerg.grid(row=1, column=1, sticky="ew", padx=(8,0), pady=(6,0))
        meds_frame.columnconfigure(1, weight=1)

        # Sinais vitais
        vitais = ttk.LabelFrame(self._inner, text="Sinais Vitais", padding=10)
        vitais.pack(fill="x", pady=(0, 10))
        vitais_inner = ttk.Frame(vitais)
        vitais_inner.pack(fill="x")
        ttk.Label(vitais_inner, text="Pressão (Sistólica/Diastólica):").grid(row=0, column=0, sticky="w")
        self.entry_pressao = ttk.Entry(vitais_inner)
        self.entry_pressao.grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(vitais_inner, text="Frequência Cardíaca (bpm):").grid(row=0, column=2, sticky="w", padx=(20,0))
        self.entry_fc = ttk.Entry(vitais_inner, width=8)
        self.entry_fc.grid(row=0, column=3, sticky="w", padx=8)

        ttk.Label(vitais_inner, text="Temperatura (°C):").grid(row=1, column=0, sticky="w", pady=(8,0))
        self.entry_temp = ttk.Entry(vitais_inner, width=8)
        self.entry_temp.grid(row=1, column=1, sticky="w", pady=(8,0), padx=8)

        ttk.Label(vitais_inner, text="Freq. Respiratória:").grid(row=1, column=2, sticky="w", padx=(20,0), pady=(8,0))
        self.entry_fr = ttk.Entry(vitais_inner, width=8)
        self.entry_fr.grid(row=1, column=3, sticky="w", pady=(8,0), padx=8)

        ttk.Label(vitais_inner, text="Saturação O₂ (%):").grid(row=2, column=0, sticky="w", pady=(8,0))
        self.entry_spo2 = ttk.Entry(vitais_inner, width=8)
        self.entry_spo2.grid(row=2, column=1, sticky="w", pady=(8,0), padx=8)

        ttk.Label(vitais_inner, text="Dor (0-10):").grid(row=2, column=2, sticky="w", padx=(20,0), pady=(8,0))
        self.entry_dor = ttk.Entry(vitais_inner, width=8)
        self.entry_dor.grid(row=2, column=3, sticky="w", pady=(8,0), padx=8)

        # Sintomas (categorias com checkboxes)
        sintomas = ttk.LabelFrame(self._inner, text="Sintomas e Sinais Presentes", padding=10)
        sintomas.pack(fill="both", pady=(0, 10), expand=True)

        # Simplificar com algumas categorias e opções
        self.sym_vars = {}
        categorias = {
            'Cardiovascular': ['Dor no peito', 'Palpitações', 'Falta de ar'],
            'Neurológico': ['Dor de cabeça', 'Tontura/vertigem', 'Confusão mental'],
            'Respiratório': ['Tosse', 'Falta de ar', 'Chiado no peito'],
            'Gastrointestinal': ['Náuseas/vômitos', 'Dor abdominal', 'Diarréia']
        }
        row = 0
        for cat, items in categorias.items():
            frame_cat = ttk.LabelFrame(sintomas, text=cat, padding=8)
            frame_cat.grid(row=row//2, column=row%2, padx=6, pady=6, sticky="nsew")
            for it in items:
                var = tk.BooleanVar(value=False)
                chk = ttk.Checkbutton(frame_cat, text=it, variable=var)
                chk.pack(anchor='w')
                self.sym_vars[it] = var
            row += 1
        sintomas.columnconfigure(0, weight=1)
        sintomas.columnconfigure(1, weight=1)

        # Prioridade
        pri = ttk.LabelFrame(self._inner, text="Prioridade", padding=10)
        pri.pack(fill="x", pady=(0, 10))
        self.pri_var = tk.StringVar(value="Média")
        pri_opts = ("Alta", "Média", "Baixa")
        self.pri_combo = ttk.Combobox(pri, values=pri_opts, textvariable=self.pri_var, state='readonly')
        self.pri_combo.pack(anchor='w')

        # Botões
        btns = ttk.Frame(self._inner)
        btns.pack(fill="x", pady=(6,0))
        ttk.Button(btns, text="Salvar Triagem", command=self._salvar_triagem, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="left", padx=6)

    def _carregar_paciente(self):
        # Buscar dados do paciente
        result = PacienteController.get_patient_by_id(self.paciente_id)
        if not result["success"]:
            messagebox.showerror("Erro", result["message"])
            self.destroy()
            return
        
        paciente = result["data"]
        nome = paciente["nome"]
        cpf = paciente["cpf"]
        data_str = paciente["data_nascimento"]
        idade = '-'
        try:
            # data_nascimento em formato ISO
            dt = datetime.strptime(data_str, "%Y-%m-%d").date()
            today = datetime.today().date()
            idade = f"{today.year - dt.year} anos"
        except:
            pass

        self.lbl_nome.config(text=f"Nome: {nome}")
        self.lbl_cpf.config(text=f"CPF: {cpf}")
        self.lbl_idade.config(text=f"Idade: {idade}")

        # Carregar triagem anterior se existir
        triagem = TriagemController.get_paciente_triagem(self.paciente_id)
        if triagem["success"]:
            try:
                dados = triagem["data"]
                # Preencher form com dados da última triagem
                self.txt_queixa.insert("1.0", dados.get("queixa", ""))
                self.txt_historia.insert("1.0", dados.get("historia", ""))
                self.entry_meds.insert(0, dados.get("medicamentos", ""))
                self.entry_alerg.insert(0, dados.get("alergias", ""))
                self.entry_pressao.insert(0, dados.get("pressao", ""))
                self.entry_fc.insert(0, dados.get("fc", ""))
                self.entry_temp.insert(0, dados.get("temp", ""))
                self.entry_fr.insert(0, dados.get("fr", ""))
                self.entry_spo2.insert(0, dados.get("spo2", ""))
                self.entry_dor.insert(0, dados.get("dor", ""))
                
                prioridade = dados.get("prioridade")
                if prioridade in ("Alta", "Média", "Baixa"):
                    self.pri_var.set(prioridade)
                
                sintomas = dados.get("sintomas", "").split(",")
                for sintoma in sintomas:
                    if sintoma and sintoma in self.sym_vars:
                        self.sym_vars[sintoma].set(True)
            except:
                pass  # Ignora erros ao carregar triagem anterior

    def _salvar_triagem(self):
        # Coletar dados do form
        queixa = self.txt_queixa.get("1.0", "end-1c").strip()
        dados = {
            'paciente_id': self.paciente_id,
            'queixa': queixa,
            'historia': self.txt_historia.get("1.0", "end-1c").strip(),
            'medicamentos': self.entry_meds.get().strip(),
            'alergias': self.entry_alerg.get().strip(),
            'pressao': self.entry_pressao.get().strip(),
            'fc': self.entry_fc.get().strip(),
            'temp': self.entry_temp.get().strip(),
            'fr': self.entry_fr.get().strip(),
            'spo2': self.entry_spo2.get().strip(),
            'dor': self.entry_dor.get().strip(),
            'prioridade': self.pri_var.get(),
            'sintomas': [k for k, v in self.sym_vars.items() if v.get()]
        }

        # Tentar salvar via controller
        result = TriagemController.realizar_triagem(dados)
        if result["success"]:
            messagebox.showinfo("Sucesso", result["message"])
            # Callback para atualizar tela pai
            try:
                self.on_save()
            except:
                pass
            self.destroy()
        else:
            messagebox.showerror("Erro", result["message"])
