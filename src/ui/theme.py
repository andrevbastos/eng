"""
Theme and design system constants for the CustomTkinter UI.
Derived from the HTML mockups for Assessoria Jurídica IFC.
"""
import customtkinter as ctk

# Appearance Mode & Default Color Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class Colors:
    BG_APP = "#1a1d21"
    BG_HEADER = "#13161a"
    BG_CARD = "#181b20"
    BG_CARD_HOVER = "#20242b"
    BG_INPUT = "#252930"
    
    BG_BTN_SEC = "#2e333b"
    BG_BTN_SEC_HOVER = "#363b44"
    
    ACCENT_BLUE = "#3d7ef8"
    ACCENT_BLUE_HOVER = "#5590ff"
    
    TEXT_MAIN = "#D9E1E8"
    TEXT_MUTED = "#8A94A0"
    TEXT_DIM = "#525B66"
    
    BORDER = "#2A2E35"
    BORDER_SUBTLE = "#23262C"
    
    # Badges / Statuses
    STATUS_PENDING_FG = "#F59E0B"
    STATUS_PENDING_BG = "#2A2011"
    
    STATUS_ANALYSIS_FG = "#3B82F6"
    STATUS_ANALYSIS_BG = "#12243E"
    
    STATUS_DONE_FG = "#10B981"
    STATUS_DONE_BG = "#0D2B22"
    
    STATUS_URGENT_FG = "#EF4444"
    STATUS_URGENT_BG = "#351515"

class Fonts:
    MAIN_FAMILY = "Segoe UI"
    
    TITLE = (MAIN_FAMILY, 18, "bold")
    SUBTITLE = (MAIN_FAMILY, 14, "bold")
    SECTION_HEADER = (MAIN_FAMILY, 11, "bold")
    BODY = (MAIN_FAMILY, 12, "normal")
    BODY_BOLD = (MAIN_FAMILY, 12, "bold")
    SMALL = (MAIN_FAMILY, 11, "normal")
    BADGE = (MAIN_FAMILY, 10, "bold")
