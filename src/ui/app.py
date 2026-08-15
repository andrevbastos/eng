"""
Main CustomTkinter Application Window for Assessoria Jurídica IFC.
Manages top navigation tabs and active view containers.
"""
import customtkinter as ctk
from src.ui.theme import Colors, Fonts

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure Window
        self.title("Assessoria Jurídica IFC - Gestão de Demandas & Pareceres")
        self.geometry("1000" + "x700")
        self.minsize(920, 640)
        self.configure(fg_color=Colors.BG_APP)
        
        # Navigation State
        self.active_tab = "demandas"
        self.current_view = None
        
        # Build UI layout
        self._build_header()
        self._build_content_area()
        
        # Initialize default view
        self.show_demandas_list()
        
    def _build_header(self):
        """Top Header Bar with Title and Navigation Tabs."""
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_HEADER,
            corner_radius=0,
            height=60,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE
        )
        self.header_frame.pack(fill="x", side="top")
        
        # Inner layout for header
        self.header_inner = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_inner.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title Label
        self.title_label = ctk.CTkLabel(
            self.header_inner,
            text="ASSESSORIA JURÍDICA IFC",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_MAIN
        )
        self.title_label.pack(side="left", padx=(0, 20))
        
        # Navigation Tabs Segmented Control / Buttons Container
        self.tabs_frame = ctk.CTkFrame(
            self.header_inner,
            fg_color=Colors.BG_HEADER,
            border_width=1,
            border_color=Colors.BORDER_SUBTLE,
            corner_radius=8
        )
        self.tabs_frame.pack(side="left")
        
        self.btn_tab_demandas = ctk.CTkButton(
            self.tabs_frame,
            text="Demandas",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.BG_INPUT,
            text_color=Colors.TEXT_MAIN,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            corner_radius=6,
            height=32,
            width=120,
            command=self.show_demandas_list
        )
        self.btn_tab_demandas.pack(side="left", padx=3, pady=3)
        
        self.btn_tab_pareceres = ctk.CTkButton(
            self.tabs_frame,
            text="Pareceres",
            font=Fonts.BODY,
            fg_color="transparent",
            text_color=Colors.TEXT_MUTED,
            hover_color=Colors.BG_BTN_SEC_HOVER,
            corner_radius=6,
            height=32,
            width=120,
            command=self.show_pareceres_list
        )
        self.btn_tab_pareceres.pack(side="left", padx=3, pady=3)

    def _build_content_area(self):
        """Main view container frame."""
        self.content_container = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_APP,
            corner_radius=0
        )
        self.content_container.pack(fill="both", expand=True, padx=20, pady=16)

    def _clear_content(self):
        """Remove current view widget if exists."""
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None

    def _update_tab_buttons(self, active_tab: str):
        """Highlight active tab button."""
        self.active_tab = active_tab
        if active_tab == "demandas":
            self.btn_tab_demandas.configure(fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_MAIN, font=Fonts.BODY_BOLD)
            self.btn_tab_pareceres.configure(fg_color="transparent", text_color=Colors.TEXT_MUTED, font=Fonts.BODY)
        else:
            self.btn_tab_demandas.configure(fg_color="transparent", text_color=Colors.TEXT_MUTED, font=Fonts.BODY)
            self.btn_tab_pareceres.configure(fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_MAIN, font=Fonts.BODY_BOLD)

    def show_demandas_list(self):
        """Switch to Demandas List View."""
        self._clear_content()
        self._update_tab_buttons("demandas")
        from src.ui.views.demandas_list import DemandasListView
        self.current_view = DemandasListView(self.content_container, app=self)
        self.current_view.pack(fill="both", expand=True)

    def show_demanda_form(self, demanda_data=None):
        """Switch to Demanda Form View (New/Edit)."""
        self._clear_content()
        self._update_tab_buttons("demandas")
        from src.ui.views.demanda_form import DemandaFormView
        self.current_view = DemandaFormView(self.content_container, app=self, demanda_data=demanda_data)
        self.current_view.pack(fill="both", expand=True)

    def show_pareceres_list(self):
        """Switch to Pareceres List View."""
        self._clear_content()
        self._update_tab_buttons("pareceres")
        from src.ui.views.pareceres_list import PareceresListView
        self.current_view = PareceresListView(self.content_container, app=self)
        self.current_view.pack(fill="both", expand=True)

    def show_parecer_form(self, parecer_data=None):
        """Switch to Parecer Form View (New/Edit)."""
        self._clear_content()
        self._update_tab_buttons("pareceres")
        from src.ui.views.parecer_form import ParecerFormView
        self.current_view = ParecerFormView(self.content_container, app=self, parecer_data=parecer_data)
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
