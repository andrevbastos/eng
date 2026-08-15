"""
Form View for New / Edit Demanda in CustomTkinter UI.
"""
import customtkinter as ctk
from tkinter import filedialog
from src.ui.theme import Colors, Fonts

class DemandaFormView(ctk.CTkFrame):
    def __init__(self, parent, app, demanda_data=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.demanda_data = demanda_data or {}
        
        self.is_edit = bool(demanda_data)
        self._build_ui()
        
    def _build_ui(self):
        # Section Label
        lbl_section = ctk.CTkLabel(
            self,
            text="FORMULÁRIO DE DEMANDA JURÍDICA",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED
        )
        lbl_section.pack(anchor="w", pady=(0, 8))
        
        # Action / Control Header Bar
        control_bar = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_HEADER,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=8,
            height=46
        )
        control_bar.pack(fill="x", pady=(0, 12))
        
        control_inner = ctk.CTkFrame(control_bar, fg_color="transparent")
        control_inner.pack(fill="x", padx=12, pady=8)
        
        btn_back = ctk.CTkButton(
            control_inner,
            text="← Cancelar e Voltar",
            font=Fonts.BODY,
            fg_color=Colors.BG_BTN_SEC,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            height=32,
            width=150,
            command=self.app.show_demandas_list
        )
        btn_back.pack(side="left")
        
        title_text = "Editar Demanda" if self.is_edit else "Cadastrar Nova Demanda"
        lbl_title = ctk.CTkLabel(
            control_inner,
            text=title_text,
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_MAIN
        )
        lbl_title.pack(side="left", expand=True)
        
        btn_save = ctk.CTkButton(
            control_inner,
            text="💾 Salvar Demanda",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            text_color="#FFFFFF",
            height=32,
            width=150,
            command=self.save_demanda
        )
        btn_save.pack(side="right")
        
        # Scrollable Form Card
        form_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.BG_CARD,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=10
        )
        form_scroll.pack(fill="both", expand=True)
        
        form_inner = ctk.CTkFrame(form_scroll, fg_color="transparent")
        form_inner.pack(fill="x", padx=16, pady=16)
        
        # -------------------------------------------------------------
        # SEÇÃO 1: Dados Principais
        # -------------------------------------------------------------
        sec1_title = ctk.CTkLabel(
            form_inner,
            text="1. DADOS PRINCIPAIS DA DEMANDA",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED
        )
        sec1_title.pack(anchor="w", pady=(0, 6))
        
        # Alvo / Motivo da Requisição
        lbl_alvo = ctk.CTkLabel(form_inner, text="Alvo / Motivo da Requisição *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_alvo.pack(anchor="w")
        self.entry_assunto = ctk.CTkEntry(
            form_inner,
            placeholder_text="Ex: Esclarecimento sobre o Edital de Licitação nº 04/2026...",
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER
        )
        self.entry_assunto.pack(fill="x", pady=(2, 10))
        if self.is_edit:
            self.entry_assunto.insert(0, self.demanda_data.get("assunto", ""))
            
        # 3 Column Row: Data Entrada, Data Limite, Status
        grid_row1 = ctk.CTkFrame(form_inner, fg_color="transparent")
        grid_row1.pack(fill="x", pady=(0, 12))
        
        # Data Entrada
        col1 = ctk.CTkFrame(grid_row1, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        lbl_de = ctk.CTkLabel(col1, text="Data de Entrada *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_de.pack(anchor="w")
        self.entry_data_entrada = ctk.CTkEntry(col1, placeholder_text="AAAA-MM-DD", font=Fonts.BODY, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER)
        self.entry_data_entrada.pack(fill="x", pady=(2, 0))
        if self.is_edit:
            self.entry_data_entrada.insert(0, self.demanda_data.get("data_entrada", "2026-08-10"))
        else:
            self.entry_data_entrada.insert(0, "2026-08-12")
            
        # Data Limite
        col2 = ctk.CTkFrame(grid_row1, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=6)
        lbl_dl = ctk.CTkLabel(col2, text="Data Limite para Resposta *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_dl.pack(anchor="w")
        self.entry_data_limite = ctk.CTkEntry(col2, placeholder_text="AAAA-MM-DD", font=Fonts.BODY, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER)
        self.entry_data_limite.pack(fill="x", pady=(2, 0))
        self.entry_data_limite.insert(0, "2026-08-22")
        
        # Status
        col3 = ctk.CTkFrame(grid_row1, fg_color="transparent")
        col3.pack(side="left", fill="x", expand=True, padx=(6, 0))
        lbl_st = ctk.CTkLabel(col3, text="Status *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_st.pack(anchor="w")
        self.combo_status = ctk.CTkComboBox(
            col3,
            values=["Em Análise", "Em Andamento", "Concluída"],
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            button_color=Colors.BG_BTN_SEC
        )
        self.combo_status.pack(fill="x", pady=(2, 0))
        if self.is_edit:
            self.combo_status.set(self.demanda_data.get("status", "Em Análise"))

        # -------------------------------------------------------------
        # SEÇÃO 2: Origem & Arquivos
        # -------------------------------------------------------------
        sec2_title = ctk.CTkLabel(
            form_inner,
            text="2. INFORMAÇÕES DE ORIGEM E ARQUIVOS",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED
        )
        sec2_title.pack(anchor="w", pady=(10, 6))
        
        grid_row2 = ctk.CTkFrame(form_inner, fg_color="transparent")
        grid_row2.pack(fill="x", pady=(0, 12))
        
        # Canal de Origem
        c2_1 = ctk.CTkFrame(grid_row2, fg_color="transparent")
        c2_1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        lbl_canal = ctk.CTkLabel(c2_1, text="Canal de Origem", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_canal.pack(anchor="w")
        self.combo_canal = ctk.CTkComboBox(c2_1, values=["E-mail", "SIGAA", "Pessoalmente", "Outros"], font=Fonts.BODY, fg_color=Colors.BG_INPUT, button_color=Colors.BG_BTN_SEC)
        self.combo_canal.pack(fill="x", pady=(2, 0))
        
        # Remetente
        c2_2 = ctk.CTkFrame(grid_row2, fg_color="transparent")
        c2_2.pack(side="left", fill="x", expand=True, padx=6)
        lbl_rem = ctk.CTkLabel(c2_2, text="Remetente (Quem enviou)", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_rem.pack(anchor="w")
        self.entry_remetente = ctk.CTkEntry(c2_2, placeholder_text="Ex: Proj. MPF Joinville", font=Fonts.BODY, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER)
        self.entry_remetente.pack(fill="x", pady=(2, 0))
        if self.is_edit:
            self.entry_remetente.insert(0, self.demanda_data.get("solicitante", ""))
            
        # Destinatário
        c2_3 = ctk.CTkFrame(grid_row2, fg_color="transparent")
        c2_3.pack(side="left", fill="x", expand=True, padx=(6, 0))
        lbl_dest = ctk.CTkLabel(c2_3, text="Destinatário (Quem recebeu)", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_dest.pack(anchor="w")
        self.entry_destinatario = ctk.CTkEntry(c2_3, placeholder_text="Ex: Assessoria Jurídica IFC", font=Fonts.BODY, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER)
        self.entry_destinatario.pack(fill="x", pady=(2, 0))
        self.entry_destinatario.insert(0, "Assessoria Jurídica IFC")

        # Caminho da Pasta Local
        lbl_path = ctk.CTkLabel(form_inner, text="Caminho da Pasta Local dos Documentos", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_path.pack(anchor="w")
        
        path_row = ctk.CTkFrame(form_inner, fg_color="transparent")
        path_row.pack(fill="x", pady=(2, 12))
        
        self.entry_path = ctk.CTkEntry(
            path_row,
            placeholder_text="Selecione o diretório local...",
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER
        )
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_browse = ctk.CTkButton(
            path_row,
            text="📁 Procurar Pasta...",
            font=Fonts.BODY,
            fg_color=Colors.BG_BTN_SEC,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            width=140,
            command=self.browse_folder
        )
        btn_browse.pack(side="right")

        # -------------------------------------------------------------
        # SEÇÃO 3: Tags & Observações
        # -------------------------------------------------------------
        sec3_title = ctk.CTkLabel(
            form_inner,
            text="3. TAGS E OBSERVAÇÕES",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED
        )
        sec3_title.pack(anchor="w", pady=(10, 6))
        
        lbl_tags = ctk.CTkLabel(form_inner, text="Tags de Organização", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_tags.pack(anchor="w")
        
        tags_frame = ctk.CTkFrame(form_inner, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, border_width=1, corner_radius=6)
        tags_frame.pack(fill="x", pady=(2, 12))
        
        tags_inner = ctk.CTkFrame(tags_frame, fg_color="transparent")
        tags_inner.pack(fill="x", padx=10, pady=8)
        
        self.chk_mpf = ctk.CTkCheckBox(tags_inner, text="MPF", font=Fonts.SMALL, text_color="#ef5350")
        self.chk_mpf.pack(side="left", padx=8)
        
        self.chk_urgente = ctk.CTkCheckBox(tags_inner, text="Urgente", font=Fonts.SMALL, text_color="#ffb74d")
        self.chk_urgente.pack(side="left", padx=8)
        
        self.chk_edital = ctk.CTkCheckBox(tags_inner, text="Edital", font=Fonts.SMALL, text_color="#ba68c8")
        self.chk_edital.pack(side="left", padx=8)
        
        if self.is_edit:
            tags = self.demanda_data.get("tags", [])
            if "MPF" in tags: self.chk_mpf.select()
            if "Urgente" in tags: self.chk_urgente.select()
            if "Edital" in tags: self.chk_edital.select()
            
        # Observações
        lbl_obs = ctk.CTkLabel(form_inner, text="Observações e Resumo da Demanda", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_obs.pack(anchor="w")
        
        self.txt_obs = ctk.CTkTextbox(
            form_inner,
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            border_width=1,
            height=100
        )
        self.txt_obs.pack(fill="x", pady=(2, 10))
        if self.is_edit:
            self.txt_obs.insert("1.0", self.demanda_data.get("detalhes", ""))

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Selecione o diretório local dos documentos")
        if folder:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, folder)

    def save_demanda(self):
        # UI Mock Action
        print("Demanda Salva com Sucesso!")
        self.app.show_demandas_list()
