"""
Form View for New / Edit Parecer in CustomTkinter UI.
"""
import customtkinter as ctk
from tkinter import filedialog
from src.ui.theme import Colors, Fonts

class ParecerFormView(ctk.CTkFrame):
    def __init__(self, parent, app, parecer_data=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.parecer_data = parecer_data or {}
        self.is_edit = bool(parecer_data)
        
        self._build_ui()
        
    def _build_ui(self):
        # Section Label
        lbl_section = ctk.CTkLabel(
            self,
            text="FORMULÁRIO DE PARECER JURÍDICO",
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
            command=self.app.show_pareceres_list
        )
        btn_back.pack(side="left")
        
        title_text = "Editar Parecer" if self.is_edit else "Cadastrar Novo Parecer"
        lbl_title = ctk.CTkLabel(
            control_inner,
            text=title_text,
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_MAIN
        )
        lbl_title.pack(side="left", expand=True)
        
        btn_save = ctk.CTkButton(
            control_inner,
            text="💾 Salvar Parecer",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            text_color="#FFFFFF",
            height=32,
            width=150,
            command=self.save_parecer
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
        # SEÇÃO 1: Dados do Parecer
        # -------------------------------------------------------------
        sec1_title = ctk.CTkLabel(
            form_inner,
            text="1. DADOS DO PARECER DA PROCURADORIA",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED
        )
        sec1_title.pack(anchor="w", pady=(0, 6))
        
        grid_row1 = ctk.CTkFrame(form_inner, fg_color="transparent")
        grid_row1.pack(fill="x", pady=(0, 12))
        
        # Nº Parecer
        col1 = ctk.CTkFrame(grid_row1, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        lbl_num = ctk.CTkLabel(col1, text="Nº do Parecer *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_num.pack(anchor="w")
        self.entry_num = ctk.CTkEntry(col1, placeholder_text="Ex: PJ-045/2026", font=Fonts.BODY, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER)
        self.entry_num.pack(fill="x", pady=(2, 0))
        if self.is_edit:
            self.entry_num.insert(0, self.parecer_data.get("numero", ""))
        else:
            self.entry_num.insert(0, "PJ-045/2026")

        # Demanda Vinculada
        col2 = ctk.CTkFrame(grid_row1, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=6)
        lbl_dem = ctk.CTkLabel(col2, text="Demanda Vinculada", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_dem.pack(anchor="w")
        self.entry_demanda = ctk.CTkEntry(col2, placeholder_text="Ex: 23350.001234/2024-11", font=Fonts.BODY, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER)
        self.entry_demanda.pack(fill="x", pady=(2, 0))
        if self.is_edit:
            self.entry_demanda.insert(0, self.parecer_data.get("demanda", ""))
            
        # Data Emissão
        col3 = ctk.CTkFrame(grid_row1, fg_color="transparent")
        col3.pack(side="left", fill="x", expand=True, padx=(6, 0))
        lbl_dt = ctk.CTkLabel(col3, text="Data de Emissão *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_dt.pack(anchor="w")
        self.entry_data = ctk.CTkEntry(col3, placeholder_text="AAAA-MM-DD", font=Fonts.BODY, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER)
        self.entry_data.pack(fill="x", pady=(2, 0))
        if self.is_edit:
            self.entry_data.insert(0, self.parecer_data.get("data_emissao", "2026-08-12"))
        else:
            self.entry_data.insert(0, "2026-08-12")

        # Relator
        lbl_rel = ctk.CTkLabel(form_inner, text="Procurador / Relator *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_rel.pack(anchor="w")
        self.entry_relator = ctk.CTkEntry(form_inner, placeholder_text="Ex: Dr. Carlos Eduardo", font=Fonts.BODY, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER)
        self.entry_relator.pack(fill="x", pady=(2, 12))
        if self.is_edit:
            self.entry_relator.insert(0, self.parecer_data.get("relator", ""))

        # -------------------------------------------------------------
        # SEÇÃO 2: Conclusão Jurídica & Ementa
        # -------------------------------------------------------------
        sec2_title = ctk.CTkLabel(
            form_inner,
            text="2. CONCLUSÃO JURÍDICA E EMENTA",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED
        )
        sec2_title.pack(anchor="w", pady=(6, 6))
        
        lbl_conc = ctk.CTkLabel(form_inner, text="Conclusão *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_conc.pack(anchor="w")
        self.combo_conclusao = ctk.CTkComboBox(
            form_inner,
            values=["Deferido", "Favorável com ressalva", "Indeferido"],
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            button_color=Colors.BG_BTN_SEC
        )
        self.combo_conclusao.pack(fill="x", pady=(2, 10))
        if self.is_edit:
            self.combo_conclusao.set(self.parecer_data.get("conclusao", "Deferido"))

        lbl_ementa = ctk.CTkLabel(form_inner, text="Ementa / Fundamentação Legal *", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_ementa.pack(anchor="w")
        
        self.txt_ementa = ctk.CTkTextbox(
            form_inner,
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            border_width=1,
            height=100
        )
        self.txt_ementa.pack(fill="x", pady=(2, 12))
        if self.is_edit:
            self.txt_ementa.insert("1.0", self.parecer_data.get("ementa", ""))

        # -------------------------------------------------------------
        # SEÇÃO 3: Anexo em PDF
        # -------------------------------------------------------------
        sec3_title = ctk.CTkLabel(
            form_inner,
            text="3. DOCUMENTO / ANEXO",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED
        )
        sec3_title.pack(anchor="w", pady=(6, 6))
        
        lbl_file = ctk.CTkLabel(form_inner, text="Arquivo PDF do Parecer Assinado", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_file.pack(anchor="w")
        
        file_row = ctk.CTkFrame(form_inner, fg_color="transparent")
        file_row.pack(fill="x", pady=(2, 12))
        
        self.entry_pdf = ctk.CTkEntry(
            file_row,
            placeholder_text="Selecione o arquivo PDF...",
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER
        )
        self.entry_pdf.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_browse = ctk.CTkButton(
            file_row,
            text="📄 Selecionar PDF...",
            font=Fonts.BODY,
            fg_color=Colors.BG_BTN_SEC,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            width=140,
            command=self.browse_pdf
        )
        btn_browse.pack(side="right")

    def browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="Selecione o parecer em PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.entry_pdf.delete(0, "end")
            self.entry_pdf.insert(0, filename)

    def save_parecer(self):
        print("Parecer Salvo com Sucesso!")
        self.app.show_pareceres_list()
