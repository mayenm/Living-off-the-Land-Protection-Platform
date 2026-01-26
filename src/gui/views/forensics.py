import customtkinter as ctk
import os
from ..theme import Theme

class ForensicsView(ctk.CTkFrame):
    def __init__(self, master, evidence_dir="evidence", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=Theme.BACKGROUND)
        self.evidence_dir = evidence_dir
        
        # Tools row (Search, Refresh, Export All)
        self.tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tools_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.btn_refresh = ctk.CTkButton(self.tools_frame, text="REFRESH VAULT", width=120, height=32, fg_color="#1f242c", font=(Theme.FONT_FAMILY_MAIN, 11, "bold"), command=self.refresh_vault)
        self.btn_refresh.pack(side="left", padx=(0, 10))
        
        self.btn_export_all = ctk.CTkButton(self.tools_frame, text="GENERATE INCIDENT REPORT", width=200, height=32, fg_color=Theme.BLUE, text_color=Theme.BACKGROUND, font=(Theme.FONT_FAMILY_MAIN, 11, "bold"))
        self.btn_export_all.pack(side="right")

        # Table Header
        self.header_frame = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR_BG, height=40, corner_radius=0, border_width=1, border_color=Theme.BORDER)
        self.header_frame.pack(fill="x", padx=30, pady=10)
        
        cols = [("TIMESTAMP", 150), ("PROCESS IMAGE", 200), ("EVIDENCE TYPE", 150), ("HASH (SHA256)", 300), ("ACTIONS", 100)]
        for text, width in cols:
            lbl = ctk.CTkLabel(self.header_frame, text=text, font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11, weight="bold"), text_color=Theme.GRAY, width=width, anchor="w")
            lbl.pack(side="left", padx=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        self.refresh_vault()

    def refresh_vault(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        if not os.path.exists(self.evidence_dir):
            os.makedirs(self.evidence_dir, exist_ok=True)
            
        files = os.listdir(self.evidence_dir)
        if not files:
            empty_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1b22", corner_radius=12)
            empty_frame.pack(expand=True, pady=100, padx=100, fill="both")
            
            ctk.CTkLabel(
                empty_frame, 
                text="📂", 
                font=ctk.CTkFont(size=64),
                text_color=Theme.GRAY
            ).pack(pady=(40, 10))
            
            ctk.CTkLabel(
                empty_frame, 
                text="VAULT IS EMPTY", 
                font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=18, weight="bold"),
                text_color="#ffffff"
            ).pack(pady=5)
            
            ctk.CTkLabel(
                empty_frame, 
                text="Evidence collected during process termination will appear here.", 
                font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=12),
                text_color=Theme.GRAY
            ).pack(pady=(0, 40))
            return

        for f in sorted(files, reverse=True):
            if f.endswith(".dmp") or f.endswith(".json") or f.endswith(".cap"):
                parts = f.split("_")
                img = parts[0] if len(parts) > 0 else "unknown"
                ext_type = "MEMORY DUMP" if f.endswith(".dmp") else ("METADATA" if f.endswith(".json") else "NETWORK CAP")
                ts = parts[-1].split(".")[0] if "_" in f else "Unknown"
                mock_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # Just a placeholder
                
                row = ctk.CTkFrame(self.scroll_frame, fg_color=Theme.SIDEBAR_BG, height=45, corner_radius=4, border_width=1, border_color=Theme.BORDER)
                row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row, text=ts, font=(Theme.FONT_FAMILY_MONO, 11), width=150, anchor="w", text_color=Theme.GRAY).pack(side="left", padx=10)
                ctk.CTkLabel(row, text=img, font=(Theme.FONT_FAMILY_MAIN, 12, "bold"), width=200, anchor="w", text_color="#ffffff").pack(side="left", padx=10)
                ctk.CTkLabel(row, text=ext_type, font=(Theme.FONT_FAMILY_MAIN, 10, "bold"), text_color=Theme.ORANGE, width=150, anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(row, text=mock_hash[:32] + "...", font=(Theme.FONT_FAMILY_MONO, 10), text_color=Theme.GRAY, width=300, anchor="w").pack(side="left", padx=10)
                
                btn = ctk.CTkButton(row, text="DOWNLOAD", width=80, height=28, fg_color="transparent", border_width=2, border_color=Theme.BLUE, text_color=Theme.BLUE, font=(Theme.FONT_FAMILY_MAIN, 10, "bold"))
                btn.pack(side="right", padx=10)
