import win32evtlog
import win32evtlogutil
import win32con
import win32security
import logging
import json
import time
import threading
import io
import xml.etree.ElementTree as ET

class ProcessEvent:
    def __init__(self, event_data, event_id="1"):
        self.raw = event_data
        self.event_id = event_id
        self.image = event_data.get("Image", "")
        self.command_line = event_data.get("CommandLine", "")
        self.parent_image = event_data.get("ParentImage", "")
        self.parent_command_line = event_data.get("ParentCommandLine", "")
        self.process_id = event_data.get("ProcessId", "")
        self.user = event_data.get("User", "")
        self.hashes = event_data.get("Hashes", "")
        self.timestamp = event_data.get("UtcTime", "")
        
        # New Telemetry Fields
        self.dest_ip = event_data.get("DestinationIp", "")
        self.dest_port = event_data.get("DestinationPort", "")
        self.target_file = event_data.get("TargetFilename", "")

    def to_dict(self):
        return {
            "image": self.image,
            "command_line": self.command_line,
            "parent_image": self.parent_image,
            "parent_command_line": self.parent_command_line,
            "pid": self.process_id,
            "user": self.user,
            "hashes": self.hashes,
            "timestamp": self.timestamp,
            "event_id": self.event_id,
            "dest_ip": self.dest_ip,
            "dest_port": self.dest_port,
            "target_file": self.target_file
        }
    
    def __repr__(self):
        return f"<ProcessEvent pid={self.process_id} img={self.image}>"

class SysmonMonitor:
    def __init__(self, event_callback=None, error_callback=None):
        self.monitoring = False
        self.event_callback = event_callback
        self.error_callback = error_callback
        self.channel = "Microsoft-Windows-Sysmon/Operational"
        self.thread = None

    def start_monitoring(self):
        if self.monitoring:
            return
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logging.info("Sysmon monitoring thread started.")

    def stop_monitoring(self):
        self.monitoring = False

    def _monitor_loop(self):
        logging.info("Starting Sysmon Monitor Loop (Polling Mode)")
        
        flags = win32evtlog.EvtQueryChannelPath | win32evtlog.EvtQueryForwardDirection
        query = "*" 
        
        try:
            hQuery = win32evtlog.EvtQuery(self.channel, flags, query, None)
            
            # Seek to 50 events before the end to show immediate history
            try:
                win32evtlog.EvtSeek(hQuery, -50, win32evtlog.EvtSeekRelativeToLast)
            except Exception as e:
                logging.warning(f"EvtSeek failed (likely <50 events): {e}")
            
            self.monitoring = True
            while self.monitoring:
                # Poll for events
                events = win32evtlog.EvtNext(hQuery, 10, 1000, 0) # 1 sec timeout
                
                if events:
                    for event in events:
                        try:
                            # Render XML
                            xml_content = win32evtlog.EvtRender(event, win32evtlog.EvtRenderEventXml)
                            parsed = self._parse_xml(xml_content)
                            if parsed and self.event_callback:
                                self.event_callback(parsed)
                        except Exception as e:
                            logging.error(f"Render Error: {e}")
                else:
                    time.sleep(0.5)
                    
        except Exception as e:
            logging.error(f"Sysmon Monitor Failed: {e}")
            logging.warning("Falling back to psutil polling for new processes...")
            if self.error_callback:
                self.error_callback(f"Sysmon Unavailable: {e}. Falling back to polling mode.")
            
            self._polling_fallback()

    def _polling_fallback(self):
        """
        Fallback monitoring using psutil if Sysmon is not available.
        This provides basic process monitoring (Creation/Termination) without kernel-level telemetry.
        """
        import psutil
        known_pids = set(psutil.pids())
        
        while self.monitoring:
            try:
                current_pids = set(psutil.pids())
                
                # New PIDs
                new_pids = current_pids - known_pids
                for pid in new_pids:
                    try:
                        p = psutil.Process(pid)
                        with p.oneshot():
                            event_data = {
                                "Image": p.exe(),
                                "CommandLine": " ".join(p.cmdline()),
                                "ProcessId": str(pid),
                                "User": p.username(),
                                "UtcTime": time.strftime('%Y-%m-%d %H:%M:%S.000', time.gmtime(p.create_time())),
                                "ParentImage": "Unknown (Polling Mode)"
                            }
                            if self.event_callback:
                                self.event_callback(ProcessEvent(event_data, event_id="1"))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Terminated PIDs
                lost_pids = known_pids - current_pids
                for pid in lost_pids:
                    if self.event_callback:
                        # Minimal data for termination event
                        self.event_callback(ProcessEvent({"ProcessId": str(pid)}, event_id="5"))
                
                known_pids = current_pids
                time.sleep(1.0) # Poll every second
            except Exception as e:
                logging.error(f"Polling Fallback Error: {e}")
                time.sleep(2.0)

    def _parse_xml(self, xml_str):
        try:
            # Parse XML
            # xml_str might be string or bytes
            if not isinstance(xml_str, str):
                 xml_str = xml_str.decode('utf-8', errors='ignore')
                 
            # Strip namespaces
            it = ET.iterparse(io.StringIO(xml_str))
            for _, el in it:
                if '}' in el.tag:
                    el.tag = el.tag.split('}', 1)[1]
            root = it.root
            
            # Check for Event ID 1 (Create), 3 (Network), 5 (Terminate), 11 (File)
            event_id_node = root.find('.//EventID')
            if event_id_node is None:
                return None
                
            event_id = event_id_node.text
            if event_id not in ['1', '3', '5', '11']:
                return None
            
            data = {}
            # Metadata from System node
            system = root.find('.//System')
            if system is not None:
                time_node = system.find('.//TimeCreated')
                if time_node is not None:
                    data["UtcTime"] = time_node.attrib.get("SystemTime", "")

            # Event Specific Data
            event_data = root.find('.//EventData')
            if event_data is not None:
                for data_item in event_data.findall('Data'):
                    name = data_item.attrib.get('Name')
                    value = data_item.text
                    if name:
                        data[name] = value
                        
            # Map specific fields for normalization
            if event_id == "3":
                data["Image"] = data.get("Image", "")
                data["DestinationIp"] = data.get("DestinationIp", "")
                data["DestinationPort"] = data.get("DestinationPort", "")
            elif event_id == "11":
                data["Image"] = data.get("Image", "")
                data["TargetFilename"] = data.get("TargetFilename", "")

            return ProcessEvent(data, event_id=event_id)
            
        except Exception as e:
            # logging.error(f"XML Parse error: {e}") 
            return None
