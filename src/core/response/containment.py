import psutil
import logging

class ContainmentUnit:
    def __init__(self):
        pass

    def suspend_process(self, pid):
        try:
            p = psutil.Process(pid)
            p.suspend()
            logging.info(f"Suspended process {pid} ({p.name()})")
            return True
        except Exception as e:
            logging.error(f"Failed to suspend {pid}: {e}")
            return False

    def terminate_process(self, pid):
        try:
            p = psutil.Process(pid)
            p.kill() # SIGKILL
            logging.info(f"Terminated process {pid} ({p.name()})")
            return True
        except Exception as e:
            logging.error(f"Failed to terminate {pid}: {e}")
            return False
            
    def isolate_host(self):
        """
        Emergency isolation of the host using Windows Firewall.
        Blocks all inbound and outbound traffic.
        """
        import subprocess
        try:
            logging.warning("ATTEMPTING HOST ISOLATION...")
            # Block all traffic
            subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "on"], check=True)
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name='WATCHTOWER_ISOLATION_IN'", "dir=in", "action=block"], check=True)
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name='WATCHTOWER_ISOLATION_OUT'", "dir=out", "action=block"], check=True)
            
            logging.info("Host Isolate Successfully.")
            return True
        except Exception as e:
            logging.error(f"Host Isolation Failed: {e}. Ensure running as Administrator.")
            return False

    def restore_network(self):
        import subprocess
        try:
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", "name='WATCHTOWER_ISOLATION_IN'"], check=True)
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", "name='WATCHTOWER_ISOLATION_OUT'"], check=True)
            logging.info("Host Network Restored.")
            return True
        except Exception as e:
            logging.error(f"Network Restoration Failed: {e}")
            return False
