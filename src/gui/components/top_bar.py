import customtkinter as ctk
from ..theme import Theme

class TopBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=60, corner_radius=0, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER, **kwargs)
        
        # Left side: View Title / Breadcrumbs
        self.title_label = ctk.CTkLabel(
            self, 
            text="DASHBOARD", 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=Theme.TEXT_SIZE_H2, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left", padx=30)
        
        # Right side: Actions
        self.actions_container = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_container.pack(side="right", padx=20)
        
        # Global Search
        self.search_entry = ctk.CTkEntry(
            self.actions_container,
            placeholder_text="Global search (Process, PID, Hashes...)",
            width=300,
            height=32,
            fg_color="#161b22",
            border_color=Theme.BORDER,
            font=(Theme.FONT_FAMILY_MAIN, Theme.TEXT_SIZE_BODY)
        )
        self.search_entry.pack(side="left", padx=10)
        
        # Time Range
        self.time_selector = ctk.CTkOptionMenu(
            self.actions_container,
            values=["Last 15m", "Last 1h", "Last 24h", "Live Feed"],
            width=120,
            height=32,
            fg_color="#161b22",
            button_color="#1f242c",
            button_hover_color="#30363d",
            dropdown_fg_color="#161b22",
            font=(Theme.FONT_FAMILY_MAIN, Theme.TEXT_SIZE_BODY)
        )
        self.time_selector.pack(side="left", padx=10)
        
        # Export Button
        self.btn_export = ctk.CTkButton(
            self.actions_container,
            text="EXPORT DATA",
            width=100,
            height=32,
            fg_color="transparent",
            border_width=1,
            border_color=Theme.BORDER,
            hover_color="#1f242c",
            font=(Theme.FONT_FAMILY_MAIN, Theme.TEXT_SIZE_BODY, "bold")
        )
        self.btn_export.pack(side="left", padx=10)

    def set_title(self, title):
        self.title_label.configure(text=title.upper())
