import customtkinter as ctk
import datetime
from ..theme import Theme

class AlertsView(ctk.CTkFrame):
    def __init__(self, master, terminate_callback=None, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=Theme.BACKGROUND)
        self.terminate_callback = terminate_callback
        self.on_select = on_select
        
        # Filters Row
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(self.filter_frame, text="Severity:", font=(Theme.FONT_FAMILY_MAIN, 12, "bold"), text_color=Theme.GRAY).pack(side="left", padx=(0, 10))
        self.filter_sev = ctk.CTkOptionMenu(self.filter_frame, values=["All", "Critical", "High", "Medium", "Low"], width=100)
        self.filter_sev.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(self.filter_frame, text="Status:", font=(Theme.FONT_FAMILY_MAIN, 12, "bold"), text_color=Theme.GRAY).pack(side="left", padx=(0, 10))
        self.filter_status = ctk.CTkOptionMenu(self.filter_frame, values=["All", "New", "Investigating", "Resolved"], width=130)
        self.filter_status.pack(side="left")

        # Table Header
        self.header_frame = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR_BG, height=40, corner_radius=0, border_width=1, border_color=Theme.BORDER)
        self.header_frame.pack(fill="x", padx=30, pady=10)
        
        cols = [("TIME", 80), ("SEV", 80), ("STATE", 70), ("RULE NAME", 200), ("PROCESS", 180), ("LIFECYCLE", 130)]
        for text, width in cols:
            lbl = ctk.CTkLabel(self.header_frame, text=text, font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11, weight="bold"), text_color=Theme.GRAY, width=width, anchor="w")
            lbl.pack(side="left", padx=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        self.alert_items = {} # pid -> row_frame

    def add_alert(self, data):
        pid = data.get("pid", "unknown")
        if pid in self.alert_items:
            return
            
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        severity = data.get("level", "Medium").title()
        rule = data.get("title", "Unknown Rule")
        process = data.get("process", "unknown.exe")
        status = "NEW"
        
        sev_color = Theme.RED if severity.upper() in ["CRITICAL", "HIGH"] else Theme.ORANGE
        
        row = ctk.CTkFrame(self.scroll_frame, fg_color=Theme.SIDEBAR_BG, height=45, corner_radius=4, border_width=1, border_color=Theme.BORDER)
        row.pack(fill="x", pady=2)
        
        # Click listener
        row.bind("<Button-1>", lambda e, d=data: self.on_select(d) if self.on_select else None)
        
        ctk.CTkLabel(row, text=ts, font=(Theme.FONT_FAMILY_MONO, 11), width=80, anchor="w").pack(side="left", padx=10)
        
        sev_lbl = ctk.CTkLabel(row, text=severity, font=(Theme.FONT_FAMILY_MAIN, 10, "bold"), text_color="#ffffff", fg_color=sev_color, corner_radius=4, width=80)
        sev_lbl.pack(side="left", padx=10, pady=10)
        
        # Status Badge (NEW) with 'glow'
        status_badge = ctk.CTkLabel(
            row, 
            text="NEW", 
            font=(Theme.FONT_FAMILY_MAIN, 9, "bold"), 
            text_color="#ffffff", 
            fg_color="#0066cc", # Deep blue
            corner_radius=12,
            width=50,
            height=20
        )
        status_badge.pack(side="left", padx=(10, 5))
        
        # Rule Name
        ctk.CTkLabel(row, text=rule, font=(Theme.FONT_FAMILY_MAIN, 12, "bold"), width=200, anchor="w", text_color="#ffffff").pack(side="left", padx=10)
        
        # Process Path (Truncated)
        display_process = process if len(process) < 30 else "..." + process[-27:]
        proc_lbl = ctk.CTkLabel(row, text=display_process, font=(Theme.FONT_FAMILY_MONO, 11), width=180, anchor="w", text_color=Theme.GRAY)
        proc_lbl.pack(side="left", padx=10)
        
        # Bind hover to show full path (simple tooltip simulation)
        proc_lbl.bind("<Enter>", lambda e, p=process: proc_lbl.configure(text=p, text_color="#ffffff"))
        proc_lbl.bind("<Leave>", lambda e, dp=display_process: proc_lbl.configure(text=dp, text_color=Theme.GRAY))
        
        # Status Dropdown (Lifecycle)
        status_menu = ctk.CTkOptionMenu(
            row, 
            values=["NEW", "INVESTIGATING", "RESOLVED"],
            width=120, height=28,
            font=(Theme.FONT_FAMILY_MAIN, 10, "bold"),
            fg_color="#1f242c",
            button_color="#30363d",
            command=lambda v, p=pid: self._update_status(p, v)
        )
        status_menu.set(status)
        status_menu.pack(side="left", padx=10)
        
        # Actions - KILL Button (Red outline, solid on hover)
        btn_term = ctk.CTkButton(
            row, 
            text="KILL", 
            width=60, 
            height=28, 
            fg_color="transparent", 
            border_width=1, 
            border_color=Theme.RED, 
            text_color=Theme.RED, 
            hover_color=Theme.RED, # Fills with solid red on hover
            font=(Theme.FONT_FAMILY_MAIN, 10, "bold"),
            command=lambda p=pid: self.on_terminate(p)
        )
        # Ensure text color turns white on hover when background is red
        btn_term.bind("<Enter>", lambda e: btn_term.configure(text_color="#ffffff"))
        btn_term.bind("<Leave>", lambda e: btn_term.configure(text_color=Theme.RED))
        btn_term.pack(side="right", padx=10)

        self.alert_items[pid] = row
        
    def _update_status(self, pid, new_status):
        # In a real app, this would update a database or backend
        print(f"Alert {pid} status updated to {new_status}")
        if new_status == "RESOLVED":
             row = self.alert_items.get(pid)
             if row:
                 row.configure(border_color=Theme.GREEN)

    def remove_alert(self, pid):
        if pid in self.alert_items:
            self.alert_items[pid].destroy()
            del self.alert_items[pid]

    def on_terminate(self, pid):
        if self.terminate_callback:
            self.terminate_callback(pid)
