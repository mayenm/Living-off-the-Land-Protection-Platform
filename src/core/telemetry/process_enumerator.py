import psutil
import datetime
import os
import logging

class ProcessEnumerator:
    """
    Utility to enumerate CURRENTLY running processes at startup.
    This complements Sysmon (which only captures NEW process creations).
    """
    def __init__(self):
        pass

    def get_current_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'exe', 'cmdline', 'create_time']):
            try:
                # Basic info
                pinfo = proc.info
                
                # Format similarly to Sysmon Event
                event_data = {
                    "Image": pinfo['exe'] if pinfo['exe'] else pinfo['name'],
                    "CommandLine": " ".join(pinfo['cmdline']) if pinfo['cmdline'] else "",
                    "ProcessId": str(pinfo['pid']),
                    "User": pinfo['username'] if pinfo['username'] else "Unknown",
                    "UtcTime": datetime.datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S.000'),
                    "ParentImage": "System/Unknown", # psutil can get parent, but keeping it simple
                    "Hashes": "" # No hashes for existing processes unless we scan them
                }
                processes.append(event_data)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes
