import customtkinter as ctk
from ..theme import Theme

class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=30, corner_radius=0, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER, **kwargs)
        
        self.sysmon_status = ctk.CTkLabel(self, text="SYSMON: RUNNING", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11, weight="bold"), text_color=Theme.GREEN)
        self.sysmon_status.pack(side="left", padx=20)
        
        self.ingestion_rate = ctk.CTkLabel(self, text="INGESTION: 12 EPS", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11), text_color=Theme.GRAY)
        self.ingestion_rate.pack(side="left", padx=20)
        
        self.rules_count = ctk.CTkLabel(self, text="RULES LOADED: 154", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11), text_color=Theme.GRAY)
        self.rules_count.pack(side="left", padx=20)
        
        self.threat_status = ctk.CTkLabel(self, text="THREAT LEVEL: LOW", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11, weight="bold"), text_color=Theme.BLUE)
        self.threat_status.pack(side="right", padx=20)
        
        self.uptime = ctk.CTkLabel(self, text="UPTIME: 04:20:15", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11), text_color=Theme.GRAY)
        self.uptime.pack(side="right", padx=20)
        
    def update_stats(self, eps, rules):
        self.ingestion_rate.configure(text=f"INGESTION: {eps} EPS")
        self.rules_count.configure(text=f"RULES LOADED: {rules}")
