import customtkinter as ctk
from ..theme import Theme

class AttackTreeView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=Theme.BACKGROUND)
        
        # Controls Row
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.btn_reset = ctk.CTkButton(self.controls_frame, text="RESET ZOOM", width=100, height=30, fg_color="#1f242c", font=(Theme.FONT_FAMILY_MAIN, 11, "bold"))
        self.btn_reset.pack(side="left", padx=(0, 10))
        
        # Canvas Container
        self.canvas_container = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR_BG, border_width=1, border_color=Theme.BORDER)
        self.canvas_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.canvas = ctk.CTkCanvas(self.canvas_container, bg=Theme.SIDEBAR_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Timeline Scrubber (Mandatory Polish)
        self.timeline_frame = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR_BG, height=60, border_width=1, border_color=Theme.BORDER)
        self.timeline_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        ctk.CTkLabel(self.timeline_frame, text="ATTACK TIMELINE", font=(Theme.FONT_FAMILY_MAIN, 10, "bold"), text_color=Theme.GRAY).pack(pady=(5, 0))
        self.scrubber = ctk.CTkSlider(self.timeline_frame, from_=0, to=100, number_of_steps=100, height=15)
        self.scrubber.pack(fill="x", padx=40, pady=10)
        
        self.processes = {} # pid -> {node_id, x, y, parent_pid}

    def add_process(self, pid, ppid, name, color=Theme.BLUE):
        if pid in self.processes:
            return
            
        x = 500
        y = 100
        
        if ppid in self.processes:
            parent = self.processes[ppid]
            x = parent["x"] + len([p for p in self.processes.values() if p["parent_pid"] == ppid]) * 150 - 75
            y = parent["y"] + 120
            self.canvas.create_line(parent["x"], parent["y"], x, y, fill=Theme.BORDER, width=2)
            
        # Draw Node
        node_id = self.canvas.create_rectangle(x-50, y-25, x+50, y+25, fill=Theme.BACKGROUND, outline=color, width=2)
        self.canvas.create_text(x, y-5, text=name[:15], fill="#ffffff", font=(Theme.FONT_FAMILY_MAIN, 10, "bold"))
        self.canvas.create_text(x, y+15, text=f"PID: {pid}", fill=Theme.GRAY, font=(Theme.FONT_FAMILY_MONO, 8))
        
        self.processes[pid] = {"id": node_id, "x": x, "y": y, "parent_pid": ppid}

    def update_from_event(self, event_data):
        eid = str(event_data.get("event_id"))
        if eid == "1" or event_data.get("alert"):
            pid = event_data.get("pid")
            ppid = event_data.get("parent_pid")
            image = event_data.get("image", "unknown").split("\\")[-1]
            color = Theme.RED if event_data.get("alert") else Theme.BLUE
            self.add_process(pid, ppid, image, color)
