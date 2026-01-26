import customtkinter as ctk
from ..theme import Theme

class IntelligenceView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=Theme.BACKGROUND)
        
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="THREAT INTELLIGENCE CENTER", 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=Theme.TEXT_SIZE_H2, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_title.pack(pady=(30, 10), anchor="w", padx=30)
        
        # Scoring Row
        self.score_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.score_frame.pack(fill="x", padx=30, pady=20)
        
        self._create_score_card(self.score_frame, "VIRUSTOTAL", "0/72", "Detections", Theme.BLUE)
        self._create_score_card(self.score_frame, "ABUSEIPDB", "0%", "Confidence", Theme.ORANGE)
        self._create_score_card(self.score_frame, "MALWARE BAZAAR", "CLEAN", "Hash Check", Theme.GREEN)

        # Sources Frame
        self.sources_frame = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER)
        self.sources_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        ctk.CTkLabel(self.sources_frame, text="ENRICHMENT SOURCES", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=14, weight="bold"), text_color=Theme.GRAY).pack(pady=10)
        
        self.source_list = ctk.CTkScrollableFrame(self.sources_frame, fg_color="transparent")
        self.source_list.pack(fill="both", expand=True, padx=10, pady=10)

    def _create_score_card(self, parent, title, value, subtitle, color):
        card = ctk.CTkFrame(parent, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER, width=200, height=100)
        card.pack(side="left", padx=(0, 20))
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=title, font=(Theme.FONT_FAMILY_MAIN, 10, "bold"), text_color=Theme.GRAY).pack(pady=(10, 0))
        ctk.CTkLabel(card, text=value, font=(Theme.FONT_FAMILY_MAIN, 24, "bold"), text_color=color).pack()
        ctk.CTkLabel(card, text=subtitle, font=(Theme.FONT_FAMILY_MAIN, 9), text_color=Theme.GRAY).pack()
