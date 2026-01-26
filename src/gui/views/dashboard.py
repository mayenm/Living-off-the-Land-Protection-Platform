import customtkinter as ctk
from ..theme import Theme

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=Theme.BACKGROUND)
        
        self.total_alerts = 0
        self.active_processes = 0
        self.total_events = 0
        
        # Stats Container
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.pack(fill="x", padx=30, pady=(30, 20))
        
        # Grid for cards
        self.stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1, pad=15)
        
        self.card_events = self._create_card(self.stats_container, "TOTAL EVENTS", "0", Theme.BLUE, 0)
        self.card_alerts = self._create_card(self.stats_container, "ACTIVE ALERTS", "0", Theme.RED, 1)
        self.card_processes = self._create_card(self.stats_container, "ACTIVE PROCESSES", "0", Theme.ORANGE, 2)
        self.card_sysmon = self._create_card(self.stats_container, "SYSTEM STATUS", "OPTIMAL", Theme.GREEN, 3)

        # Center Row - Situational Awareness
        self.middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.middle_frame.pack(fill="both", expand=True, padx=30, pady=10)
        self.middle_frame.grid_columnconfigure(0, weight=2)
        self.middle_frame.grid_columnconfigure(1, weight=1)
        
        # Activity Timeline / Live Feed Mini
        self.timeline_frame = ctk.CTkFrame(self.middle_frame, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER)
        self.timeline_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(
            self.timeline_frame, 
            text="SYSTEM HEARTBEAT / REAL-TIME TELEMETRY", 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=12, weight="bold"),
            text_color=Theme.GRAY
        ).pack(pady=15, padx=20, anchor="w")
        
        # Telemetry Data
        self.telemetry_data = [0] * 50
        
        # Spacer for graph
        self.graph_frame = ctk.CTkFrame(self.timeline_frame, fg_color="transparent")
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.canvas = ctk.CTkCanvas(self.graph_frame, bg="#0d1117", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.after(1000, self._animate_telemetry)
        
        # Right Side - Top Detections
        self.detections_frame = ctk.CTkFrame(self.middle_frame, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER)
        self.detections_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(
            self.detections_frame, 
            text="TOP THREAT VECTORS", 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=12, weight="bold"),
            text_color=Theme.GRAY
        ).pack(pady=15, padx=20, anchor="w")
        
        self.rules_list = ctk.CTkFrame(self.detections_frame, fg_color="transparent")
        self.rules_list.pack(fill="both", expand=True, padx=15)
        
        self._add_rule_item("living_off_the_land", "Certutil Abuse", Theme.RED)
        self._add_rule_item("credential_access", "LSASS Memory Dump", Theme.RED)
        self._add_rule_item("persistence", "Registry Run Key", Theme.ORANGE)
        self._add_rule_item("defense_evasion", "Masquerading", Theme.ORANGE)

    def _animate_telemetry(self):
        self._draw_telemetry()
        self.after(100, self._animate_telemetry)

    def _draw_telemetry(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10: return
        
        # Draw grid
        for i in range(0, w, 40):
            self.canvas.create_line(i, 0, i, h, fill="#1f242c", width=1)
        for i in range(0, h, 40):
            self.canvas.create_line(0, i, w, i, fill="#1f242c", width=1)

        points = []
        step = w / (len(self.telemetry_data) - 1)
        
        for i, val in enumerate(self.telemetry_data):
            x = i * step
            # Scale val (0-1000) to height (0-h)
            y = h - (val / 1000 * h * 0.8) - 10
            points.extend([x, y])
            
        if len(points) >= 4:
            self.canvas.create_line(points, fill=Theme.BLUE, width=2, smooth=True)
            # Add glow effect
            self.canvas.create_line(points, fill=Theme.BLUE, width=4, smooth=True, stipple="gray50")

    def update_telemetry(self, eps):
        # Simulate fluctuation if eps > 0
        if eps > 0:
            import random
            fluctuation = random.randint(-50, 50)
            val = max(0, min(1000, eps + fluctuation))
        else:
            val = 0
            
        self.telemetry_data.pop(0)
        self.telemetry_data.append(val)

    def _create_card(self, parent, title, value, color, col):
        frame = ctk.CTkFrame(parent, fg_color=Theme.SIDEBAR_BG, corner_radius=8, border_width=1, border_color=Theme.BORDER)
        frame.grid(row=0, column=col, sticky="nsew", padx=10)
        
        lbl_t = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=10, weight="bold"), text_color=Theme.GRAY)
        lbl_t.pack(pady=(15, 0), padx=20, anchor="w")
        
        lbl_v = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=28, weight="bold"), text_color=color)
        lbl_v.pack(pady=(5, 15), padx=20, anchor="w")
        
        frame.value_label = lbl_v
        return frame

    def _add_rule_item(self, rule, hits, color):
        item = ctk.CTkFrame(self.rules_list, fg_color="transparent", height=40)
        item.pack(fill="x", pady=2)
        
        dot = ctk.CTkLabel(item, text="■", text_color=color, font=("Arial", 14))
        dot.pack(side="left", padx=(5, 10))
        
        ctk.CTkLabel(item, text=rule.upper(), font=(Theme.FONT_FAMILY_MONO, 11), text_color="#c9d1d9").pack(side="left")
        ctk.CTkLabel(item, text=hits, font=(Theme.FONT_FAMILY_MAIN, 11, "bold"), text_color=Theme.GRAY).pack(side="right", padx=10)

    def update_stats(self):
        self.card_events.value_label.configure(text=str(self.total_events))
        self.card_alerts.value_label.configure(text=str(self.total_alerts))
        self.card_processes.value_label.configure(text=str(self.active_processes))
        
    def set_system_status(self, status, color_val=None):
        color = Theme.GREEN if color_val == "green" else Theme.RED if color_val == "red" else Theme.ORANGE
        self.card_sysmon.value_label.configure(text=status, text_color=color)

