"""
Demandas List & Search View for CustomTkinter UI.
"""
import customtkinter as ctk
from src.ui.theme import Colors, Fonts

MOCK_DEMANDAS = [
    {
        "id": "1",
        "status": "Em andamento",
        "alvo_motivo": "Esclarecimento Edital nº 04/2026",
        "origem_canal": "E-mail (MPF)",
        "data_limite": "20/08/2026",
        "remetente": "Proj. MPF Joinville",
        "entrada": "10/08/2026",
        "tags": ["MPF", "Urgente"],
        "observacoes": "Aguardando parecer final da Procuradoria para encaminhamento ao Reitor.",
    },
    {
        "id": "2",
        "status": "Em análise",
        "alvo_motivo": "Notificação Recomendatória Reitoria",
        "origem_canal": "SIGAA (Procuradoria)",
        "data_limite": "25/08/2026",
        "remetente": "Procuradoria Geral",
        "entrada": "12/08/2026",
        "tags": ["Edital"],
        "observacoes": "Aguardando análise preliminar da documentação recebida.",
    },
    {
        "id": "3",
        "status": "Concluída",
        "alvo_motivo": "Defesa Processo Trabalhista Terceirizados",
        "origem_canal": "Pessoalmente",
        "data_limite": "05/08/2026",
        "remetente": "Sindicato",
        "entrada": "29/07/2026",
        "tags": ["MPF"],
        "observacoes": "Demanda concluída e arquivada.",
    },
]

STATUS_COLORS = {
    "Em análise": (Colors.STATUS_PENDING_BG, Colors.STATUS_PENDING_FG),
    "Em andamento": (Colors.STATUS_ANALYSIS_BG, Colors.STATUS_ANALYSIS_FG),
    "Concluída": (Colors.STATUS_DONE_BG, Colors.STATUS_DONE_FG),
}

TAG_COLORS = {
    "MPF": ("#351515", "#EF5350"),
    "Urgente": ("#3A2412", "#FFB74D"),
    "Edital": ("#2E1738", "#BA68C8"),
}


class DemandasListView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.demandas = list(MOCK_DEMANDAS)
        self.filters_visible = False

        self._build_ui()
        self.filter_demandas()

    def _build_ui(self):
        self.search_card = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_HEADER,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=8,
        )
        self.search_card.pack(fill="x", pady=(0, 14))

        lbl_section = ctk.CTkLabel(
            self.search_card,
            text="PESQUISA DE DEMANDAS",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED,
        )
        lbl_section.pack(anchor="w", padx=14, pady=(12, 6))

        search_row = ctk.CTkFrame(self.search_card, fg_color="transparent")
        search_row.pack(fill="x", padx=14, pady=(0, 10))

        self.entry_search = ctk.CTkEntry(
            search_row,
            placeholder_text="🔍  Digite para pesquisar em todos os campos...",
            font=Fonts.BODY,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            border_width=1,
            text_color=Colors.TEXT_MAIN,
            height=34,
            corner_radius=6,
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda _event: self.filter_demandas())

        self.btn_toggle_filter = ctk.CTkButton(
            search_row,
            text="+ Adicionar Filtro  ▼",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.BG_BTN_SEC,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            text_color=Colors.TEXT_MAIN,
            height=34,
            width=155,
            corner_radius=6,
            command=self.toggle_filters,
        )
        self.btn_toggle_filter.pack(side="right")

        self.filter_panel = ctk.CTkFrame(
            self.search_card,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=8,
        )
        self._build_filter_panel()

        self.chips_row = ctk.CTkFrame(self.search_card, fg_color="transparent")
        self.chips_row.pack(fill="x", padx=14, pady=(0, 12))

        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", pady=(0, 10))

        self.lbl_count = ctk.CTkLabel(
            action_bar,
            text="RESULTADOS ENCONTRADOS (0)",
            font=Fonts.SECTION_HEADER,
            text_color=Colors.TEXT_MUTED,
        )
        self.lbl_count.pack(side="left")

        btn_new_demanda = ctk.CTkButton(
            action_bar,
            text="+ Nova Demanda",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            text_color="#FFFFFF",
            height=32,
            width=145,
            corner_radius=7,
            command=lambda: self.app.show_demanda_form(),
        )
        btn_new_demanda.pack(side="right")

        self.table_card = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            border_color=Colors.BORDER_SUBTLE,
            border_width=1,
            corner_radius=8,
        )
        self.table_card.pack(fill="both", expand=True)

        self._build_table_header()

        self.scroll_list = ctk.CTkScrollableFrame(
            self.table_card,
            fg_color=Colors.BG_APP,
            corner_radius=0,
            border_width=0,
        )
        self.scroll_list.pack(fill="both", expand=True)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", pady=(6, 0))

        ctk.CTkLabel(
            footer,
            text="Clique em editar para abrir a demanda.",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_DIM,
        ).pack(side="left")

        ctk.CTkLabel(
            footer,
            text="Página 1 de 1",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_DIM,
        ).pack(side="right")

    def _build_filter_panel(self):
        grid = ctk.CTkFrame(self.filter_panel, fg_color="transparent")
        grid.pack(fill="x", padx=12, pady=10)
        grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="filters")

        self.combo_status = self._build_filter_combo(
            grid,
            column=0,
            label="Filtrar por Status",
            values=["Todos", "Em análise", "Em andamento", "Concluída"],
        )
        self.combo_tag = self._build_filter_combo(
            grid,
            column=1,
            label="Filtrar por Tag",
            values=["Todas", "MPF", "Urgente", "Edital"],
        )
        self.combo_canal = self._build_filter_combo(
            grid,
            column=2,
            label="Canal de Origem",
            values=["Todos", "E-mail", "SIGAA", "Pessoalmente"],
        )

    def _build_filter_combo(self, parent, column, label, values):
        ctk.CTkLabel(
            parent,
            text=label,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_MUTED,
        ).grid(row=0, column=column, sticky="w", padx=5, pady=(0, 4))

        combo = ctk.CTkComboBox(
            parent,
            values=values,
            font=Fonts.SMALL,
            fg_color=Colors.BG_CARD,
            button_color=Colors.BG_BTN_SEC,
            button_hover_color=Colors.BG_BTN_SEC_HOVER,
            border_color=Colors.BORDER,
            dropdown_fg_color=Colors.BG_CARD,
            dropdown_hover_color=Colors.BG_BTN_SEC_HOVER,
            dropdown_text_color=Colors.TEXT_MAIN,
            text_color=Colors.TEXT_MAIN,
            height=30,
            command=lambda _value: self.filter_demandas(),
        )
        combo.grid(row=1, column=column, sticky="ew", padx=5)
        combo.set(values[0])
        return combo

    def _build_table_header(self):
        header = ctk.CTkFrame(
            self.table_card,
            fg_color=Colors.BG_HEADER,
            corner_radius=8,
            height=36,
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        header.grid_columnconfigure(0, weight=12, uniform="demandas_table")
        header.grid_columnconfigure(1, weight=25, uniform="demandas_table")
        header.grid_columnconfigure(2, weight=15, uniform="demandas_table")
        header.grid_columnconfigure(3, weight=12, uniform="demandas_table")
        header.grid_columnconfigure(4, weight=15, uniform="demandas_table")
        header.grid_columnconfigure(5, weight=10, uniform="demandas_table")

        headers = ["STATUS", "ALVO / MOTIVO", "ORIGEM / CANAL", "DATA LIMITE", "TAGS", "AÇÕES"]
        for index, title in enumerate(headers):
            ctk.CTkLabel(
                header,
                text=title,
                font=Fonts.SECTION_HEADER,
                text_color=Colors.TEXT_MUTED,
                anchor="w",
            ).grid(row=0, column=index, sticky="ew", padx=(14 if index == 0 else 6, 6), pady=8)

    def toggle_filters(self):
        self.filters_visible = not self.filters_visible
        if self.filters_visible:
            self.filter_panel.pack(fill="x", padx=14, pady=(0, 10), before=self.chips_row)
            self.btn_toggle_filter.configure(fg_color=Colors.ACCENT_BLUE, text="− Ocultar Filtros  ▲")
        else:
            self.filter_panel.pack_forget()
            self.btn_toggle_filter.configure(fg_color=Colors.BG_BTN_SEC, text="+ Adicionar Filtro  ▼")

    def filter_demandas(self):
        query = self.entry_search.get().lower().strip()
        status_filter = self.combo_status.get()
        tag_filter = self.combo_tag.get()
        canal_filter = self.combo_canal.get()

        filtered = []
        for demanda in MOCK_DEMANDAS:
            searchable_text = " ".join(
                [
                    demanda["status"],
                    demanda["alvo_motivo"],
                    demanda["origem_canal"],
                    demanda["data_limite"],
                    demanda["remetente"],
                    demanda["entrada"],
                    " ".join(demanda["tags"]),
                ]
            ).lower()

            match_query = not query or query in searchable_text
            match_status = status_filter == "Todos" or demanda["status"] == status_filter
            match_tag = tag_filter == "Todas" or tag_filter in demanda["tags"]
            match_canal = canal_filter == "Todos" or demanda["origem_canal"].startswith(canal_filter)

            if match_query and match_status and match_tag and match_canal:
                filtered.append(demanda)

        self.lbl_count.configure(text=f"RESULTADOS ENCONTRADOS ({len(filtered)})")
        self._render_filter_chips()
        self.render_rows(filtered)

    def _render_filter_chips(self):
        for child in self.chips_row.winfo_children():
            child.destroy()

        ctk.CTkLabel(
            self.chips_row,
            text="Filtros aplicados:",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_DIM,
        ).pack(side="left", padx=(0, 8))

        chips = []
        if self.combo_status.get() != "Todos":
            chips.append(("Status", self.combo_status.get(), lambda: self._clear_combo(self.combo_status, "Todos")))
        if self.combo_tag.get() != "Todas":
            chips.append(("Tag", self.combo_tag.get(), lambda: self._clear_combo(self.combo_tag, "Todas")))
        if self.combo_canal.get() != "Todos":
            chips.append(("Canal", self.combo_canal.get(), lambda: self._clear_combo(self.combo_canal, "Todos")))

        if not chips:
            ctk.CTkLabel(
                self.chips_row,
                text="Nenhum filtro adicional.",
                font=Fonts.SMALL,
                text_color=Colors.TEXT_DIM,
            ).pack(side="left")
            return

        for label, value, clear_command in chips:
            chip = ctk.CTkButton(
                self.chips_row,
                text=f"{label}: {value}  ✕",
                font=Fonts.SMALL,
                fg_color="#12243E",
                hover_color=Colors.BG_BTN_SEC_HOVER,
                text_color="#82B1FF",
                height=24,
                corner_radius=14,
                command=clear_command,
            )
            chip.pack(side="left", padx=(0, 6))

    def _clear_combo(self, combo, default_value):
        combo.set(default_value)
        self.filter_demandas()

    def render_rows(self, items):
        for child in self.scroll_list.winfo_children():
            child.destroy()

        if not items:
            ctk.CTkLabel(
                self.scroll_list,
                text="Nenhuma demanda encontrada.",
                font=Fonts.BODY,
                text_color=Colors.TEXT_MUTED,
            ).pack(pady=40)
            return

        for demanda in items:
            row = ctk.CTkFrame(
                self.scroll_list,
                fg_color=Colors.BG_APP,
                border_color=Colors.BORDER_SUBTLE,
                border_width=1,
                corner_radius=0,
                height=48,
            )
            row.pack(fill="x")
            row.pack_propagate(False)

            row.grid_columnconfigure(0, weight=12, uniform="demandas_table")
            row.grid_columnconfigure(1, weight=25, uniform="demandas_table")
            row.grid_columnconfigure(2, weight=15, uniform="demandas_table")
            row.grid_columnconfigure(3, weight=12, uniform="demandas_table")
            row.grid_columnconfigure(4, weight=15, uniform="demandas_table")
            row.grid_columnconfigure(5, weight=10, uniform="demandas_table")

            self._add_status_badge(row, demanda["status"], column=0)
            self._add_text_cell(row, demanda["alvo_motivo"], column=1, bold=True)
            self._add_text_cell(row, demanda["origem_canal"], column=2, muted=True)
            self._add_text_cell(
                row,
                demanda["data_limite"],
                column=3,
                text_color="#FFB74D" if demanda["status"] != "Concluída" else Colors.TEXT_MUTED,
            )
            self._add_tags_cell(row, demanda["tags"], column=4)

            btn_edit = ctk.CTkButton(
                row,
                text="Editar",
                font=Fonts.SMALL,
                fg_color=Colors.BG_BTN_SEC,
                hover_color=Colors.BG_BTN_SEC_HOVER,
                text_color=Colors.TEXT_MAIN,
                width=68,
                height=26,
                corner_radius=6,
                command=lambda item=demanda: self.app.show_demanda_form(item),
            )
            btn_edit.grid(row=0, column=5, sticky="e", padx=(6, 12), pady=10)

    def _add_text_cell(self, parent, text, column, bold=False, muted=False, text_color=None):
        ctk.CTkLabel(
            parent,
            text=text,
            font=Fonts.BODY_BOLD if bold else Fonts.BODY,
            text_color=text_color or (Colors.TEXT_MUTED if muted else Colors.TEXT_MAIN),
            anchor="w",
        ).grid(row=0, column=column, sticky="ew", padx=6, pady=12)

    def _add_status_badge(self, parent, status, column):
        bg, fg = STATUS_COLORS.get(status, (Colors.BG_BTN_SEC, Colors.TEXT_MAIN))
        ctk.CTkLabel(
            parent,
            text=status,
            font=Fonts.BADGE,
            fg_color=bg,
            text_color=fg,
            corner_radius=12,
            width=96,
            height=22,
        ).grid(row=0, column=column, sticky="w", padx=(14, 6), pady=12)

    def _add_tags_cell(self, parent, tags, column):
        tags_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tags_frame.grid(row=0, column=column, sticky="w", padx=6, pady=11)

        if not tags:
            ctk.CTkLabel(
                tags_frame,
                text="—",
                font=Fonts.SMALL,
                text_color=Colors.TEXT_DIM,
            ).pack(side="left")
            return

        for tag in tags:
            bg, fg = TAG_COLORS.get(tag, (Colors.BG_BTN_SEC, Colors.TEXT_MAIN))
            pill = ctk.CTkFrame(tags_frame, fg_color=bg, corner_radius=4)
            pill.pack(side="left", padx=(0, 4))

            ctk.CTkLabel(
                pill,
                text=tag,
                font=Fonts.BADGE,
                text_color=fg,
                height=20,
            ).pack(padx=7)
