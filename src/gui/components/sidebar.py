import customtkinter as ctk
from ..theme import Theme

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, command=None):
        super().__init__(master, width=240, corner_radius=0, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER)
        self.command = command
        self.grid_propagate(False)
        
        # Logo / Title
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(pady=(30, 40), padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="OGT WATCHTOWER", 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=18, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(anchor="w")
        
        self.version_label = ctk.CTkLabel(
            self.title_frame, 
            text="ENTERPRISE SECURITY v1.2", 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=10, weight="bold"),
            text_color=Theme.GRAY
        )
        self.version_label.pack(anchor="w")
        
        # Navigation Buttons
        self.btn_dashboard = self._create_nav_button("Dashboard", "dashboard")
        self.btn_alerts = self._create_nav_button("Alerts", "alerts")
        self.btn_tree = self._create_nav_button("Attack Trees", "attack_tree")
        self.btn_map = self._create_nav_button("Live Attack Map", "threat_map")
        self.btn_feed = self._create_nav_button("Live Events", "live_feed")
        self.btn_vault = self._create_nav_button("Forensics Vault", "forensics")
        self.btn_intel = self._create_nav_button("Intelligence Center", "intelligence")
        
        # Spacer
        self.middle_spacer = ctk.CTkFrame(self, fg_color="transparent")
        self.middle_spacer.pack(fill="both", expand=True)
        
        self.btn_settings = self._create_nav_button("Settings", "settings")
        
        # Bottom status
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.bottom_frame.pack(side="bottom", fill="x", pady=20, padx=20)
        
        self.status_dot = ctk.CTkLabel(self.bottom_frame, text="●", text_color=Theme.GREEN, font=ctk.CTkFont(size=14))
        self.status_dot.pack(side="left")
        
        self.status_text = ctk.CTkLabel(self.bottom_frame, text="ENGINE ONLINE", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11, weight="bold"), text_color=Theme.GRAY)
        self.status_text.pack(side="left", padx=10)

    def _create_nav_button(self, text, view_name):
        btn = ctk.CTkButton(
            self, 
            text=text, 
            height=40,
            corner_radius=6,
            fg_color="transparent",
            text_color="#c9d1d9",
            hover_color="#1f242c",
            anchor="w",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=13, weight="normal"),
            command=lambda: self.command(view_name)
        )
        btn.pack(fill="x", padx=15, pady=4)
        return btn
