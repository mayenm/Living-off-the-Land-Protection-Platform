import customtkinter as ctk
import os
from PIL import Image

from .theme import Theme
from .views.dashboard import DashboardView
from .views.live_feed import LiveFeedView
from .views.alerts import AlertsView
from .views.attack_tree import AttackTreeView
from .views.forensics import ForensicsView
from .views.intelligence import IntelligenceView
from .views.threat_map import ThreatMapView
from .views.settings import SettingsView
from .components.sidebar import Sidebar
from .components.top_bar import TopBar
from .components.inspector import InspectorPanel
from .components.status_bar import StatusBar

class App(ctk.CTk):
    def __init__(self, queue, start_engine_callback):
        super().__init__()
        
        self.queue = queue
        self.start_engine_callback = start_engine_callback

        self.title("OGT WATCHTOWER v1.2 // ENTERPRISE")
        self.geometry("1650x950")
        
        # Appearance
        ctk.set_appearance_mode("Dark")

        # Set Icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            else:
                # Fallback for development if paths differ
                self.iconbitmap("assets/icon.ico")
        except Exception as e:
            print(f"Icon Error: {e}")
        
        # Grid Layout
        self.grid_rowconfigure(1, weight=1) # Main area
        self.grid_rowconfigure(2, weight=0) # Status bar
        self.grid_columnconfigure(1, weight=1)
        
        # -- Top Bar (New) --
        self.top_bar = TopBar(self)
        self.top_bar.grid(row=0, column=1, columnspan=2, sticky="ew")
        
        # -- Sidebar --
        self.sidebar = Sidebar(self, command=self.change_view)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # -- Center Area (Analysis Workspace) --
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color=Theme.BACKGROUND)
        self.main_container.grid(row=1, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # -- Right Panel (Context Inspector) --
        self.inspector = InspectorPanel(self)
        self.inspector.grid(row=1, column=2, sticky="nsew")
        
        # -- Bottom Status Bar --
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky="ew")
        
        # Views
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        evidence_path = os.path.join(base_dir, "release", "evidence")
        
        self.dashboard_view = DashboardView(self.main_container)
        self.live_feed_view = LiveFeedView(self.main_container, on_select=self.inspect_event)
        self.alerts_view = AlertsView(self.main_container, terminate_callback=self.terminate_process, on_select=self.inspect_event)
        self.attack_tree_view = AttackTreeView(self.main_container)
        self.forensics_view = ForensicsView(self.main_container, evidence_dir=evidence_path)
        self.intelligence_view = IntelligenceView(self.main_container)
        self.threat_map_view = ThreatMapView(self.main_container)
        self.settings_view = SettingsView(self.main_container)
        
        self.views = {
            "dashboard": self.dashboard_view,
            "live_feed": self.live_feed_view,
            "alerts": self.alerts_view,
            "attack_tree": self.attack_tree_view,
            "threat_map": self.threat_map_view,
            "forensics": self.forensics_view,
            "intelligence": self.intelligence_view,
            "settings": self.settings_view
        }
        
        # Start View
        self.change_view("dashboard")
        
        # Start Engine
        if self.start_engine_callback:
            self.start_engine_callback(self)
        
        # Poll Queue
        self.after(100, self.check_queue)
        
        # Keyboard Shortcuts
        self.bind("<Control-Key-1>", lambda e: self.change_view("dashboard"))
        self.bind("<Control-Key-2>", lambda e: self.change_view("alerts"))
        self.bind("<Control-Key-3>", lambda e: self.change_view("attack_tree"))
        self.bind("<Control-Key-4>", lambda e: self.change_view("live_feed"))
        self.bind("<Control-Key-5>", lambda e: self.change_view("threat_map"))
        self.bind("<Control-Key-6>", lambda e: self.change_view("forensics"))
        self.bind("<Control-Key-7>", lambda e: self.change_view("intelligence"))
        self.bind("<Escape>", lambda e: self.inspector.placeholder.pack(expand=True) or self.inspector.details_container.pack_forget())

    def change_view(self, view_name):
        for name, view in self.views.items():
            view.grid_forget()
        
        if view_name in self.views:
            self.views[view_name].grid(row=0, column=0, sticky="nsew")
            self.top_bar.set_title(view_name)
            if view_name == "forensics":
                self.forensics_view.refresh_vault()

    def inspect_event(self, data):
        self.inspector.show_details(data)

    def terminate_process(self, pid):
        try:
            import psutil
            p = psutil.Process(int(pid))
            p.terminate()
            # Log termination
            term_event = {
                "title": "PROCESS TERMINATED", 
                "level": "info",
                "process": "User Action",
                "command": f"Manually killed PID {pid}",
                "pid": pid,
                "image": "UserAction.exe",
                "command_line": f"Killed PID {pid}"
            }
            self.live_feed_view.add_event(term_event, alert=False)
            self.alerts_view.remove_alert(pid)
        except Exception as e:
            print(f"Termination Error: {e}")

    def check_queue(self):
        try:
            count = 0
            while not self.queue.empty() and count < 100:
                msg_type, data = self.queue.get_nowait()
                count += 1
                
                if msg_type == "event":
                    self.live_feed_view.add_event(data)
                    self.attack_tree_view.update_from_event(data)
                    self.threat_map_view.update_from_event(data)
                    self.dashboard_view.total_events += 1
                    
                    eid = data.get("event_id", "1")
                    if eid == "1":
                        self.dashboard_view.active_processes += 1
                    elif eid == "5":
                        self.dashboard_view.active_processes = max(0, self.dashboard_view.active_processes - 1)
                        self.alerts_view.remove_alert(data.get("pid"))
                        
                elif msg_type == "alert":
                    self.live_feed_view.add_event(data, alert=True)
                    self.attack_tree_view.update_from_event({**data, "alert": True})
                    self.threat_map_view.update_from_event({**data, "alert": True})
                    self.alerts_view.add_alert(data)
                    self.dashboard_view.total_alerts += 1
                    # Auto-inspect alerts
                    self.inspect_event(data)
                    
                elif msg_type == "error":
                     self.dashboard_view.set_system_status("OFFLINE / ERROR", "red")
                     self.sidebar.status_dot.configure(text_color=Theme.RED)
                     self.sidebar.status_text.configure(text=str(data)[:20] + "...")
                
            if count > 0:
                self.dashboard_view.update_stats()
                eps = count * 10
                self.status_bar.update_stats(eps, 154) # Simplified EPS
                self.dashboard_view.update_telemetry(eps)
                
        except Exception as e:
            print(f"Queue Error: {e}")
        finally:
            self.after(50, self.check_queue)
