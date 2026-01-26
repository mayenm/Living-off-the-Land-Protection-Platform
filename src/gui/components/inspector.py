import customtkinter as ctk
from ..theme import Theme

class InspectorPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=380, corner_radius=0, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER, **kwargs)
        self.grid_propagate(False)
        
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="NODE INSPECTOR", 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=14, weight="bold"),
            text_color="#ffffff",
            anchor="w"
        )
        self.header.pack(pady=(20, 10), padx=20, fill="x")
        
        # Placeholder for when nothing is selected
        self.placeholder = ctk.CTkLabel(
            self, 
            text="SELECT OBJECT TO INSPECT", 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11, slant="italic"),
            text_color=Theme.GRAY
        )
        self.placeholder.pack(expand=True)
        
        # Container for details (initially hidden)
        self.details_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        
    def show_details(self, data):
        self.placeholder.pack_forget()
        self.details_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Clear old details
        for widget in self.details_container.winfo_children():
            widget.destroy()
            
        # Title / Image
        img_name = data.get("image", "Unknown").split("\\")[-1]
        title = ctk.CTkLabel(self.details_container, text=img_name.upper(), font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=16, weight="bold"), text_color=Theme.BLUE, anchor="w")
        title.pack(pady=(10, 5), padx=15, fill="x")
        
        status = "MALICIOUS" if data.get("alert") else "BENIGN"
        status_color = Theme.RED if data.get("alert") else Theme.GREEN
        ctk.CTkLabel(self.details_container, text=status, font=(Theme.FONT_FAMILY_MAIN, 10, "bold"), text_color=status_color, anchor="w").pack(padx=15, fill="x")

        # Field Factory
        self._add_field("Process ID", data.get("pid", "N/A"))
        self._add_field("Parent Process ID", data.get("parent_pid", "N/A"))
        self._add_field("User Context", data.get("user", "SYSTEM"))
        self._add_field("Command Line", data.get("command_line", "N/A"), wrap=True, show_copy=True)
        self._add_field("Image Hash (SHA256)", "e3b0c44298fc1c149afbf4... (Mock)", wrap=True, show_copy=True)
        
        # Intelligence Section
        self._add_separator()
        ctk.CTkLabel(self.details_container, text="THREAT INTELLIGENCE", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11, weight="bold"), text_color=Theme.ORANGE, anchor="w").pack(padx=15, fill="x", pady=(10, 5))
        
        self._add_field("VirusTotal Detections", "12/72", color=Theme.RED)
        self._add_field("AbuseIPDB Score", "0.0 (Clean)", color=Theme.GREEN)

        # Detection Matches
        self._add_separator()
        ctk.CTkLabel(self.details_container, text="DETECTION MATCHES", font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=11, weight="bold"), text_color=Theme.ORANGE, anchor="w").pack(padx=15, fill="x", pady=(10, 5))
        
        sigma_matches = data.get("sigma_matches", ["Suspicious Process Creation"])
        for match in sigma_matches:
            self._add_match("SIGMA", match, Theme.ORANGE)

    def _add_field(self, label, value, wrap=False, color="#ffffff", show_copy=False):
        frame = ctk.CTkFrame(self.details_container, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=8)
        
        # Label: font-size 10px, uppercase, color gray-400 (#94a3b8)
        lbl = ctk.CTkLabel(
            frame, 
            text=label.upper(), 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MAIN, size=10, weight="bold"), 
            text_color="#94a3b8", 
            anchor="w"
        )
        lbl.pack(fill="x")
        
        # Value Container (to hold value + copy button)
        val_container = ctk.CTkFrame(frame, fg_color="transparent")
        val_container.pack(fill="x")

        # Value: font-size 13px, font-weight bold, color white
        val = ctk.CTkLabel(
            val_container, 
            text=str(value), 
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=13, weight="bold"), 
            text_color=color, 
            anchor="w",
            wraplength=300 if wrap else 0,
            justify="left"
        )
        val.pack(side="left", fill="x", expand=True)

        if show_copy:
            copy_btn = ctk.CTkButton(
                val_container,
                text="📋",
                width=24,
                height=24,
                fg_color="transparent",
                hover_color="#1f242c",
                text_color=Theme.GRAY,
                command=lambda: self._copy_to_clipboard(value)
            )
            copy_btn.pack(side="right", padx=(5, 0))

    def _copy_to_clipboard(self, text):
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        # Optional: show a small notification or change button color briefly

    def _add_match(self, tech, rule, color):
        frame = ctk.CTkFrame(self.details_container, fg_color="#1a1b22", corner_radius=4)
        frame.pack(fill="x", padx=15, pady=4)
        
        text = f"[{tech}] {rule}"
        lbl = ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=10), text_color=color, anchor="w")
        lbl.pack(fill="x", padx=10, pady=5)

    def _add_separator(self):
        sep = ctk.CTkFrame(self.details_container, height=1, fg_color=Theme.BORDER)
        sep.pack(fill="x", pady=15, padx=15)
