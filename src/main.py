import os
import sys
import threading
import queue
import logging
import json

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from core.telemetry.sysmon_monitor import SysmonMonitor
from core.detection.engine import DetectionEngine
from core.detection.yara_scanner import YaraScanner
from core.intelligence.cloud_sentry import CloudSentry

# GUI
from gui.app import App

# Determine Base Path (Works for dev and PyInstaller)
if getattr(sys, 'frozen', False):
    # Running as a bundled executable
    base_dir = os.path.dirname(sys.executable)
else:
    # Running from source
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logging
log_dir = os.path.join(base_dir, "release", "logs")
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except:
        pass # Fallback or use temp

log_file = os.path.join(log_dir, "watchtower.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # src/.. -> Project Root

    return os.path.join(base_path, "src", relative_path) if not getattr(sys, 'frozen', False) else os.path.join(base_path, relative_path)

def load_settings():
    path = resource_path(os.path.join("config", "settings.json"))
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                return json.load(f)
            except:
                pass
    return {"api_keys": {}}

def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class EngineManager:
    def __init__(self, ui_queue, settings):
        self.ui_queue = ui_queue
        self.settings = settings
        
        rules_dir = resource_path(os.path.join("config", "rules"))
        yara_dir = resource_path(os.path.join("config", "yara"))
        
        self.sigma_engine = DetectionEngine(rules_dir)
        self.yara_engine = YaraScanner(yara_dir)
        self.cloud_sentry = CloudSentry(settings.get("api_keys"))
        
        self.monitor = SysmonMonitor(event_callback=self.event_callback, 
                                     error_callback=self.error_callback)

    def event_callback(self, process_event):
        try:
            # Send raw event to UI
            self.ui_queue.put(("event", process_event.to_dict()))
            
            # --- Detection Pipeline ---
            matches = self.sigma_engine.evaluate(process_event)
            alerts = []
            
            # 1. Sigma Rules
            for rule in matches:
                alerts.append({
                    "title": f"SIGMA: {rule.title}",
                    "level": rule.level,
                    "process": process_event.image,
                    "command": process_event.command_line,
                    "pid": process_event.process_id
                })

            # 2. YARA (Only for creations)
            if process_event.event_id == "1" and process_event.image and os.path.exists(process_event.image):
                yara_matches = self.yara_engine.scan_file(process_event.image)
                for match in yara_matches:
                    alerts.append({
                        "title": f"YARA: {match}",
                        "level": "high",
                        "process": process_event.image,
                        "command": "Static Hash/String Match Detected",
                        "pid": process_event.process_id
                    })

            # 3. Cloud IP Reputation (Event ID 3)
            if process_event.event_id == "3" and process_event.dest_ip:
                def ip_cb(result):
                    if result.get("abuse_score", 0) > 50:
                         self.ui_queue.put(("alert", {
                             "title": "ABUSE: Malicious Connection",
                             "level": "high",
                             "process": process_event.image,
                             "command": f"Target: {process_event.dest_ip} (Score: {result['abuse_score']})",
                             "pid": process_event.process_id
                         }))
                self.cloud_sentry.check_ip(process_event.dest_ip, callback=ip_cb)

            # 4. Cloud File Hash (Event ID 1 or 11)
            file_path = process_event.image or process_event.target_file
            if process_event.event_id in ["1", "11"] and file_path and os.path.exists(file_path):
                def cloud_cb(result):
                    if result.get("malicious_count", 0) > 3:
                         self.ui_queue.put(("alert", {
                             "title": "CLOUD: Known Malware",
                             "level": "critical",
                             "process": file_path,
                             "command": f"VT Detections: {result['malicious_count']}",
                             "pid": process_event.process_id
                         }))
                self.cloud_sentry.check_file_hash(file_path, callback=cloud_cb)

            # --- Push Alerts to UI ---
            for alert in alerts:
                self.ui_queue.put(("alert", alert))

            # --- Automated Response Logic ---
            critical_threat = any(a['level'] in ['high', 'critical'] for a in alerts)
            if critical_threat:
                from core.response.forensics import ForensicsCollector
                from core.response.containment import ContainmentUnit
                
                containment = ContainmentUnit()
                collector = ForensicsCollector(evidence_dir=os.path.join(base_dir, "release", "evidence"))

                # Snapshot
                try:
                    if process_event.process_id:
                        collector.capture_snapshot(int(process_event.process_id), process_event.image)
                except: pass
                
                # Containment
                try:
                    if process_event.process_id:
                        containment.suspend_process(int(process_event.process_id))
                except: pass
                
                # Extreme Isolation
                if any(a['level'] == 'critical' for a in alerts):
                    containment.isolate_host()

        except Exception as e:
            logging.error(f"Engine Error: {e}")

    def error_callback(self, error_msg):
        self.ui_queue.put(("error", error_msg))

    def start(self, app_instance):
        # --- Baseline Scan ---
        try:
            from core.telemetry.process_enumerator import ProcessEnumerator
            from core.telemetry.sysmon_monitor import ProcessEvent
            
            enumerator = ProcessEnumerator()
            current_procs = enumerator.get_current_processes()
            logging.info(f"Populating dashboard with {len(current_procs)} existing processes.")
            
            # Update app state
            app_instance.dashboard_view.active_processes = len(current_procs)
            # Ensure UI reflects this immediately even if queue is empty
            app_instance.dashboard_view.update_stats()
            
            for proc_data in current_procs:
                # Use class callback
                self.event_callback(ProcessEvent(proc_data, event_id="1"))
        except Exception as e:
            logging.error(f"Baseline Scan Failed: {e}")

        # --- Live Monitoring ---
        self.monitor.start_monitoring()
        logging.info("Engine Background Thread Started")

def main():
    if not is_admin():
        # Note: In production build, UAC-admin manifest should handle this, 
        # but kept for source/manual execution.
        pass

    ui_queue = queue.Queue()
    settings = load_settings()
    
    # Initialize Engine Manager
    engine = EngineManager(ui_queue, settings)
    
    # Launch GUI
    # Passing engine.start directly as the callback
    app = App(ui_queue, start_engine_callback=engine.start)
    
    # Initial Admin Warning (if needed)
    if not is_admin():
        ui_queue.put(("error", "CRITICAL: Not Running as Administrator. Monitoring will be disabled."))

    app.mainloop()
    
    # Cleanup
    engine.monitor.stop_monitoring()
    sys.exit()

if __name__ == "__main__":
    main()
