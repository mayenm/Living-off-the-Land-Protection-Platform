import customtkinter as ctk
import datetime
from ..theme import Theme

class LiveFeedView(ctk.CTkFrame):
    def __init__(self, master, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=Theme.BACKGROUND)
        self.on_select = on_select
        
        # Tools row (Pause, Resume, Clear)
        self.tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tools_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.btn_pause = ctk.CTkButton(self.tools_frame, text="PAUSE FEED", width=100, height=30, fg_color="#1f242c", font=(Theme.FONT_FAMILY_MAIN, 11, "bold"))
        self.btn_pause.pack(side="left", padx=(0, 10))
        
        self.btn_clear = ctk.CTkButton(self.tools_frame, text="CLEAR ALL", width=100, height=30, fg_color="#1f242c", font=(Theme.FONT_FAMILY_MAIN, 11, "bold"))
        self.btn_clear.pack(side="left")

        # Table Header
        self.header_frame = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR_BG, height=35, corner_radius=0, border_width=1, border_color=Theme.BORDER)
        self.header_frame.pack(fill="x", padx=30)
        
        cols = [("TIME", 100), ("ID", 50), ("TYPE", 80), ("IMAGE", 180), ("COMMAND LINE", 500)]
        for text, width in cols:
            lbl = ctk.CTkLabel(self.header_frame, text=text, font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=10, weight="bold"), text_color=Theme.GRAY, width=width, anchor="w")
            lbl.pack(side="left", padx=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER)
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        self.events = []

    def add_event(self, data, alert=False):
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        eid = data.get("event_id", "1")
        etype = "PROCESS" if eid == "1" else ("TERM" if eid == "5" else "FILE")
        image = data.get("image", "unknown").split("\\")[-1]
        cmd = data.get("command_line", "")
        
        bg_color = "#1a1b22" if len(self.events) % 2 == 0 else "transparent"
        text_color = Theme.RED if alert else (Theme.BLUE if eid == "1" else Theme.GRAY)
        
        row = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=30, corner_radius=0)
        row.pack(fill="x")
        
        # Click listener
        row.bind("<Button-1>", lambda e, d=data: self.on_select(d) if self.on_select else None)
        
        ctk.CTkLabel(row, text=ts, font=(Theme.FONT_FAMILY_MONO, 10), width=100, anchor="w", text_color=Theme.GRAY).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=eid, font=(Theme.FONT_FAMILY_MONO, 10), width=50, anchor="w", text_color=Theme.GRAY).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=etype, font=(Theme.FONT_FAMILY_MAIN, 10, "bold"), width=80, anchor="w", text_color=text_color).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=image, font=(Theme.FONT_FAMILY_MONO, 10), width=180, anchor="w", text_color=text_color).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=cmd[:120], font=(Theme.FONT_FAMILY_MONO, 10), text_color="#c9d1d9", anchor="w").pack(side="left", padx=10)

        self.events.append(row)
        if len(self.events) > 200:
            old = self.events.pop(0)
            old.destroy()
