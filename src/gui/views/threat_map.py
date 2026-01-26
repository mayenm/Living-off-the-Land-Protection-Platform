import customtkinter as ctk
import random

class ThreatMapView(ctk.CTkFrame):
    """
    A stylized 'Live Attack Map' visualization.
    For this version, it's a dynamic animation showing nodes connecting.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#0a0b10")
        
        # Header with Toolbar
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=30, pady=(20, 10))
        
        self.lbl_title = ctk.CTkLabel(
            self.toolbar, 
            text="LIVE ATTACK MAP // CLUSTERED TELEMETRY", 
            font=ctk.CTkFont(family="Orbitron", size=18, weight="bold"),
            text_color="#00f2ff"
        )
        self.lbl_title.pack(side="left")

        self.btn_zoom_fit = ctk.CTkButton(
            self.toolbar, 
            text="ZOOM TO FIT", 
            width=100, 
            height=30, 
            fg_color="#1f242c", 
            font=(Theme.FONT_FAMILY_MAIN, 10, "bold"),
            command=self._zoom_to_fit
        )
        self.btn_zoom_fit.pack(side="right")
        
        self.canvas = ctk.CTkCanvas(self, bg="#0d1117", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.nodes = {} # pid -> node_data
        self.links = []
        self.selected_node = None
        
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        self.after(50, self._update_physics)

    def update_from_event(self, event_data):
        pid = event_data.get("pid", str(random.randint(1000, 9999)))
        ppid = event_data.get("parent_pid")
        img = event_data.get("image", "unknown").split("\\")[-1]
        is_alert = event_data.get("alert", False)
        
        if pid in self.nodes:
            return

        # Initial Position
        parent_node = self.nodes.get(ppid)
        if parent_node:
            x = parent_node["x"] + random.randint(-50, 50)
            y = parent_node["y"] + random.randint(-50, 50)
        else:
            x = random.randint(100, 700)
            y = random.randint(100, 400)

        color = "#ff003c" if is_alert else "#00f2ff"
        
        node_id = self.canvas.create_oval(x-8, y-8, x+8, y+8, fill=color, outline="#ffffff", width=1)
        text_id = self.canvas.create_text(x, y+18, text=img, fill="#8b949e", font=("Consolas", 8))
        
        self.nodes[pid] = {
            "id": node_id,
            "text": text_id,
            "x": x, "y": y,
            "vx": 0, "vy": 0,
            "ppid": ppid,
            "color": color,
            "is_alert": is_alert,
            "label": img
        }
        
        if ppid and ppid in self.nodes:
            line_id = self.canvas.create_line(x, y, parent_node["x"], parent_node["y"], fill="#30363d", width=1)
            self.links.append({"id": line_id, "source": pid, "target": ppid})

    def _update_physics(self):
        # Constants
        k = 0.05  # Spring constant
        repulsion = 4000
        damping = 0.9
        center_x = self.canvas.winfo_width() / 2 or 400
        center_y = self.canvas.winfo_height() / 2 or 300

        pids = list(self.nodes.keys())
        for i, pid1 in enumerate(pids):
            n1 = self.nodes[pid1]
            
            # Repulsion between all nodes
            for j in range(i+1, len(pids)):
                pid2 = pids[j]
                n2 = self.nodes[pid2]
                dx = n1["x"] - n2["x"]
                dy = n1["y"] - n2["y"]
                dist_sq = dx*dx + dy*dy + 0.1
                force = repulsion / dist_sq
                ax = dx * force / 10
                ay = dy * force / 10
                n1["vx"] += ax
                n1["vy"] += ay
                n2["vx"] -= ax
                n2["vy"] -= ay
            
            # Attraction to center (gravity)
            n1["vx"] += (center_x - n1["x"]) * 0.001
            n1["vy"] += (center_y - n1["y"]) * 0.001

        # Spring forces for links
        for link in self.links:
            s = self.nodes.get(link["source"])
            t = self.nodes.get(link["target"])
            if s and t:
                dx = s["x"] - t["x"]
                dy = s["y"] - t["y"]
                dist = (dx*dx + dy*dy)**0.5
                force = (dist - 100) * k
                ax = dx * force / dist if dist > 0 else 0
                ay = dy * force / dist if dist > 0 else 0
                s["vx"] -= ax
                s["vy"] -= ay
                t["vx"] += ax
                t["vy"] += ay

        # Apply velocity and update canvas
        for pid, n in self.nodes.items():
            n["vx"] *= damping
            n["vy"] *= damping
            n["x"] += n["vx"]
            n["y"] += n["vy"]
            
            self.canvas.coords(n["id"], n["x"]-8, n["y"]-8, n["x"]+8, n["y"]+8)
            self.canvas.coords(n["text"], n["x"], n["y"]+18)

        for link in self.links:
            s = self.nodes.get(link["source"])
            t = self.nodes.get(link["target"])
            if s and t:
                self.canvas.coords(link["id"], s["x"], s["y"], t["x"], t["y"])

        self.after(30, self._update_physics)

    def _zoom_to_fit(self):
        if not self.nodes: return
        
        # Simple center-gravity pull to bring everything back into view
        center_x = self.canvas.winfo_width() / 2
        center_y = self.canvas.winfo_height() / 2
        
        for pid, n in self.nodes.items():
            n["x"] = center_x + (n["x"] - center_x) * 0.5
            n["y"] = center_y + (n["y"] - center_y) * 0.5
            n["vx"] = 0
            n["vy"] = 0

    def _on_canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if not item: return
        
        clicked_pid = None
        for pid, n in self.nodes.items():
            if n["id"] == item[0]:
                clicked_pid = pid
                break
        
        if clicked_pid:
            self._highlight_node(clicked_pid)
        else:
            self._reset_highlight()

    def _highlight_node(self, target_pid):
        self.selected_node = target_pid
        connected = {target_pid}
        for link in self.links:
            if link["source"] == target_pid: connected.add(link["target"])
            if link["target"] == target_pid: connected.add(link["source"])
            
        for pid, n in self.nodes.items():
            alpha = 1.0 if pid in connected else 0.2
            self.canvas.itemconfigure(n["id"], state="normal" if alpha > 0.5 else "disabled")
            color = n["color"] if alpha > 0.5 else "#1f242c"
            self.canvas.itemconfigure(n["id"], fill=color)
            self.canvas.itemconfigure(n["text"], fill="#8b949e" if alpha > 0.5 else "#1f242c")

    def _reset_highlight(self):
        self.selected_node = None
        for pid, n in self.nodes.items():
            self.canvas.itemconfigure(n["id"], fill=n["color"])
            self.canvas.itemconfigure(n["text"], fill="#8b949e")
