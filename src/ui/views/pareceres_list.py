"""
Pareceres List & Search View for CustomTkinter UI.
"""
import customtkinter as ctk
from src.ui.theme import Colors, Fonts

MOCK_PARECERES = [
    {
        "id": "1",
        "numero": "PJ-042/2026",
        "demanda": "23350.001234/2024-11",
        "relator": "Dr. Carlos Eduardo",
        "data_emissao": "12/08/2026",
        "conclusao": "Favorável com ressalva",
        "ementa": "Análise jurídica de termo aditivo contratual. Observância da Lei nº 14.133/2021."
    },
    {
        "id": "2",
        "numero": "PJ-039/2026",
        "demanda": "23350.005678/2024-88",
        "relator": "Dra. Ana Paula",
        "data_emissao": "08/08/2026",
        "conclusao": "Deferido",
        "ementa": "Concessão de uso de espaço físico. Minuta aprovada conforme exigências legais."
    },
    {
        "id": "3",
        "numero": "PJ-015/2026",
        "demanda": "23350.009012/2024-55",
        "relator": "Dr. Roberto Silva",
        "data_emissao": "28/07/2026",
        "conclusao": "Indeferido",
        "ementa": "Recurso administrativo interposto fora do prazo legal. Intempestividade configurada."
    }
]

class PareceresListView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.pareceres = list(MOCK_PARECERES)
        
        self.filters_visible = False
        
        self._build_ui()
        
    def _build_ui(self):
        # Section Label
        lbl_section = ctk.CTkLabel(
            self,
            text="BANCO DE PARECERES JURÍDICOS",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED
        )
        lbl_section.pack(anchor="w", pady=(0, 8))
        
        # Search & Filter Container Card
        self.search_card = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=10
        )
        self.search_card.pack(fill="x", pady=(0, 12), ipady=4)
        
        # Search Main Row
        search_row = ctk.CTkFrame(self.search_card, fg_color="transparent")
        search_row.pack(fill="x", padx=12, pady=10)
        
        self.entry_search = ctk.CTkEntry(
            search_row,
            placeholder_text="🔍 Buscar por Nº do Parecer, Relator, Demanda ou Ementa...",
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            border_width=1,
            text_color=Colors.TEXT_MAIN,
            height=38
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_pareceres())
        
        self.btn_toggle_filter = ctk.CTkButton(
            search_row,
            text="⚙ Filtros Avançados",
            font=Fonts.BODY,
            fg_color=Colors.BG_BTN_SEC,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            height=38,
            width=140,
            command=self.toggle_filters
        )
        self.btn_toggle_filter.pack(side="right")
        
        # Expandable Filters Panel
        self.filter_panel = ctk.CTkFrame(self.search_card, fg_color=Colors.BG_INPUT, corner_radius=8)
        
        f_grid = ctk.CTkFrame(self.filter_panel, fg_color="transparent")
        f_grid.pack(fill="x", padx=12, pady=10)
        
        # Conclusão Filter
        lbl_conc = ctk.CTkLabel(f_grid, text="Conclusão:", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_conc.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.combo_conc = ctk.CTkComboBox(
            f_grid,
            values=["Todas", "Deferido", "Favorável com ressalva", "Indeferido"],
            font=Fonts.SMALL,
            fg_color=Colors.BG_CARD,
            button_color=Colors.BG_BTN_SEC,
            width=180,
            command=lambda v: self.filter_pareceres()
        )
        self.combo_conc.grid(row=1, column=0, padx=5, pady=(0, 5))
        
        # Relator Filter
        lbl_rel = ctk.CTkLabel(f_grid, text="Relator:", font=Fonts.SMALL, text_color=Colors.TEXT_MUTED)
        lbl_rel.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.entry_relator_filter = ctk.CTkEntry(
            f_grid,
            placeholder_text="Ex: Carlos, Ana...",
            font=Fonts.SMALL,
            fg_color=Colors.BG_CARD,
            border_color=Colors.BORDER,
            width=180
        )
        self.entry_relator_filter.grid(row=1, column=1, padx=5, pady=(0, 5))
        self.entry_relator_filter.bind("<KeyRelease>", lambda e: self.filter_pareceres())

        # Action Bar (Header Count + New Parecer Button)
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", pady=(0, 10))
        
        self.lbl_count = ctk.CTkLabel(
            action_bar,
            text=f"PARECERES REGISTRADOS ({len(self.pareceres)})",
            font=Fonts.BODY_BOLD,
            text_color=Colors.TEXT_MAIN
        )
        self.lbl_count.pack(side="left")
        
        btn_new_parecer = ctk.CTkButton(
            action_bar,
            text="+ Novo Parecer",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            text_color="#FFFFFF",
            height=36,
            width=150,
            corner_radius=8,
            command=lambda: self.app.show_parecer_form()
        )
        btn_new_parecer.pack(side="right")
        
        # Table Header
        tbl_header = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_HEADER,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=8,
            height=36
        )
        tbl_header.pack(fill="x", pady=(0, 4))
        
        headers = [
            ("Nº PARECER", 0.18),
            ("DEMANDA VINCULADA", 0.22),
            ("EMENTA / SÍNTESE", 0.35),
            ("RELATOR", 0.15),
            ("AÇÕES", 0.10)
        ]
        
        header_inner = ctk.CTkFrame(tbl_header, fg_color="transparent")
        header_inner.pack(fill="x", padx=12, pady=6)
        
        for title, weight in headers:
            col_lbl = ctk.CTkLabel(
                header_inner,
                text=title,
                font=Fonts.SECTION_HEADER,
                text_color=Colors.TEXT_MUTED,
                anchor="w"
            )
            col_lbl.pack(side="left", fill="x", expand=True)

        # Scrollable Table List Frame
        self.scroll_list = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.BG_CARD,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=8
        )
        self.scroll_list.pack(fill="both", expand=True)
        
        self.render_rows(self.pareceres)

    def toggle_filters(self):
        self.filters_visible = not self.filters_visible
        if self.filters_visible:
            self.filter_panel.pack(fill="x", padx=12, pady=(0, 10))
            self.btn_toggle_filter.configure(fg_color=Colors.ACCENT_BLUE)
        else:
            self.filter_panel.pack_forget()
            self.btn_toggle_filter.configure(fg_color=Colors.BG_BTN_SEC)

    def filter_pareceres(self):
        query = self.entry_search.get().lower().strip()
        conc_filter = self.combo_conc.get()
        rel_filter = self.entry_relator_filter.get().lower().strip()
        
        filtered = []
        for p in MOCK_PARECERES:
            match_q = (
                query in p["numero"].lower() or
                query in p["demanda"].lower() or
                query in p["relator"].lower() or
                query in p["ementa"].lower()
            )
            match_conc = (conc_filter == "Todas" or p["conclusao"] == conc_filter)
            match_rel = (not rel_filter or rel_filter in p["relator"].lower())
            
            if match_q and match_conc and match_rel:
                filtered.append(p)
                
        self.lbl_count.configure(text=f"PARECERES REGISTRADOS ({len(filtered)})")
        self.render_rows(filtered)

    def render_rows(self, items):
        for child in self.scroll_list.winfo_children():
            child.destroy()
            
        if not items:
            empty_lbl = ctk.CTkLabel(
                self.scroll_list,
                text="Nenhum parecer encontrado.",
                font=Fonts.BODY,
                text_color=Colors.TEXT_MUTED
            )
            empty_lbl.pack(pady=40)
            return

        for item in items:
            row_frame = ctk.CTkFrame(
                self.scroll_list,
                fg_color=Colors.BG_APP,
                border_color=Colors.BORDER_SUBTLE,
                border_width=1,
                corner_radius=6
            )
            row_frame.pack(fill="x", pady=3, padx=4)
            
            inner = ctk.CTkFrame(row_frame, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=8)
            
            # Parecer Num
            lbl_num = ctk.CTkLabel(
                inner,
                text=item["numero"],
                font=Fonts.BODY_BOLD,
                text_color=Colors.ACCENT_BLUE,
                width=130,
                anchor="w"
            )
            lbl_num.pack(side="left", padx=(0, 10))
            
            # Demanda
            lbl_dem = ctk.CTkLabel(
                inner,
                text=item["demanda"],
                font=Fonts.BODY,
                text_color=Colors.TEXT_MAIN,
                width=170,
                anchor="w"
            )
            lbl_dem.pack(side="left", padx=(0, 10))
            
            # Ementa & Conclusão
            info_sub = ctk.CTkFrame(inner, fg_color="transparent")
            info_sub.pack(side="left", fill="x", expand=True)
            
            lbl_ementa = ctk.CTkLabel(
                info_sub,
                text=item["ementa"],
                font=Fonts.SMALL,
                text_color=Colors.TEXT_MAIN,
                anchor="w"
            )
            lbl_ementa.pack(anchor="w")
            
            conc = item["conclusao"]
            lbl_conc = ctk.CTkLabel(
                info_sub,
                text=f"Conclusão: {conc}",
                font=Fonts.BADGE,
                text_color=Colors.TEXT_MUTED,
                anchor="w"
            )
            lbl_conc.pack(anchor="w")
            
            # Relator
            lbl_rel = ctk.CTkLabel(
                inner,
                text=item["relator"],
                font=Fonts.SMALL,
                text_color=Colors.TEXT_MUTED,
                width=130,
                anchor="w"
            )
            lbl_rel.pack(side="left", padx=10)
            
            # Action Buttons
            btn_edit = ctk.CTkButton(
                inner,
                text="✏ Editar",
                font=Fonts.SMALL,
                fg_color=Colors.BG_BTN_SEC,
                hover_color=Colors.BG_BTN_SEC_HOVER,
                text_color=Colors.TEXT_MAIN,
                width=75,
                height=28,
                command=lambda p=item: self.app.show_parecer_form(p)
            )
            btn_edit.pack(side="right", padx=2)
