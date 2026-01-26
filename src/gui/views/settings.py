import customtkinter as ctk
from ..theme import Theme

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=Theme.BACKGROUND)
        
        # Sidebar for settings tabs
        self.tab_sidebar = ctk.CTkFrame(self, width=180, fg_color=Theme.SIDEBAR_BG, corner_radius=0)
        self.tab_sidebar.pack(side="left", fill="y")
        
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)
        
        self.tabs = {}
        self._create_tab_button("General", "general")
        self._create_tab_button("Telemetry", "telemetry")
        self._create_tab_button("Detection", "detection")
        self._create_tab_button("YARA", "yara")
        self._create_tab_button("Integrations", "integrations")
        self._create_tab_button("Response", "response")
        
        self.show_tab("general")

    def _create_tab_button(self, text, tab_id):
        btn = ctk.CTkButton(
            self.tab_sidebar, 
            text=text, 
            height=40,
            fg_color="transparent",
            text_color=Theme.GRAY,
            anchor="w",
            hover_color="#1f242c",
            font=(Theme.FONT_FAMILY_MAIN, 12, "bold"),
            command=lambda: self.show_tab(tab_id)
        )
        btn.pack(fill="x", padx=10, pady=5)
        self.tabs[tab_id] = btn

    def show_tab(self, tab_id):
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Highlight active button
        for tid, btn in self.tabs.items():
            if tid == tab_id:
                btn.configure(fg_color="#1f242c", text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=Theme.GRAY)
        
        method_name = f"_draw_{tab_id}"
        if hasattr(self, method_name):
            getattr(self, method_name)()

    def _draw_general(self):
        self._add_section_title("GENERAL SETTINGS")
        self._add_toggle("Dark Mode Only", True)
        self._add_slider("UI Refresh Rate (ms)", 50, 500, 100)
        self._add_input("Data Retention (Days)", "30")

    def _draw_telemetry(self):
        self._add_section_title("TELEMETRY CONFIGURATION")
        self._add_toggle("Sysmon Monitoring", True)
        self._add_input("Log Path", "C:\\Windows\\System32\\winevt\\Logs\\Microsoft-Windows-Sysmon%4Operational.evtx")
        self._add_input("Enabled Event IDs", "1,2,3,5,7,11,12,13,22")

    def _draw_detection(self):
        self._add_section_title("DETECTION ENGINE")
        self._add_toggle("Sigma Engine", True)
        self._add_input("Rules Path", "./config/rules")
        self._add_toggle("Auto-update Rules", True)

    def _draw_yara(self):
        self._add_section_title("YARA SCANNING")
        self._add_toggle("Memory Injection Scanning", True)
        self._add_toggle("Disk File Scanning", False)
        self._add_input("YARA Ruleset Path", "./config/yara")

    def _draw_integrations(self):
        self._add_section_title("EXTERNAL INTEGRATIONS")
        self._add_input("VirusTotal API Key", "****-****-****-****")
        self._add_input("AbuseIPDB API Key", "****-****-****-****")
        self._add_slider("API Rate Limit (req/min)", 1, 60, 4)

    def _draw_response(self):
        self._add_section_title("INCIDENT RESPONSE")
        self._add_toggle("Auto-kill Malicious Processes", False)
        self._add_toggle("Forensics-before-terminate (Mandatory)", True)
        self._add_toggle("Isolate Endpoint on Critical", False)

    def _add_section_title(self, title):
        ctk.CTkLabel(self.content_area, text=title, font=(Theme.FONT_FAMILY_MAIN, 18, "bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))

    def _add_toggle(self, label, default_val):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        ctk.CTkLabel(frame, text=label, font=(Theme.FONT_FAMILY_MAIN, 13), text_color=Theme.GRAY).pack(side="left")
        switch = ctk.CTkSwitch(frame, text="", progress_color=Theme.BLUE)
        if default_val: switch.select()
        switch.pack(side="right")

    def _add_slider(self, label, min_v, max_v, val):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        ctk.CTkLabel(frame, text=f"{label}: {val}", font=(Theme.FONT_FAMILY_MAIN, 13), text_color=Theme.GRAY).pack(side="left")
        slider = ctk.CTkSlider(frame, from_=min_v, to=max_v, number_of_steps=100, width=200, progress_color=Theme.BLUE)
        slider.set(val)
        slider.pack(side="right")

    def _add_input(self, label, default_v):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        ctk.CTkLabel(frame, text=label, font=(Theme.FONT_FAMILY_MAIN, 13), text_color=Theme.GRAY).pack(side="left")
        entry = ctk.CTkEntry(frame, width=300, fg_color=Theme.SIDEBAR_BG, border_color=Theme.BORDER)
        entry.insert(0, default_v)
        entry.pack(side="right")
