import os
import ctypes
import logging
import json
import time
from ctypes import wintypes

# Windows API constants for MiniDumpWriteDump
class MINIDUMP_EXCEPTION_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("ThreadId", wintypes.DWORD),
        ("ExceptionPointers", ctypes.c_void_p),
        ("ClientPointers", wintypes.BOOL),
    ]

# MiniDumpWithFullMemory = 0x00000002
MiniDumpWithFullMemory = 2

class ForensicsCollector:
    def __init__(self, evidence_dir="evidence"):
        self.evidence_dir = evidence_dir
        if not os.path.exists(self.evidence_dir):
            os.makedirs(self.evidence_dir)

    def capture_snapshot(self, process_id, image_name="unknown"):
        """
        Captures process memory and metadata.
        """
        timestamp = int(time.time())
        base_name = f"{image_name}_{process_id}_{timestamp}"
        
        # 1. Capture Metadata
        self._save_metadata(process_id, image_name, base_name)
        
        # 2. Dump Memory
        dump_path = os.path.join(self.evidence_dir, f"{base_name}.dmp")
        success = self._create_minidump(process_id, dump_path)
        
        if success:
            logging.info(f"Forensic snapshot saved to {dump_path}")
            return dump_path
        else:
            logging.error(f"Failed to create memory dump for PID {process_id}")
            return None

    def _save_metadata(self, pid, image_name, base_name):
        meta = {
            "pid": pid,
            "image_name": image_name,
            "timestamp": time.time(),
            # In a real tool, we'd grab OpenHandles, LoadedDLLs, etc.
            "note": "Automated snapshot triggered by OGT WatchTower"
        }
        path = os.path.join(self.evidence_dir, f"{base_name}.json")
        try:
            with open(path, 'w') as f:
                json.dump(meta, f, indent=2)
        except Exception:
            pass

    def _create_minidump(self, pid, output_path):
        try:
            # Get handle to process
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010
            PROCESS_DUP_HANDLE = 0x0040 # Often needed
            
            # We need broader rights for Full Memory dump usually
            # But let's try with standard rights first. 
            # Actually, we need handle with PROCESS_QUERY_INFORMATION and PROCESS_VM_READ at least.
            
            hProcess = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                False,
                pid
            )
            
            if not hProcess:
                logging.error(f"Could not open process {pid} for dumping. Error: {ctypes.windll.kernel32.GetLastError()}")
                return False

            # Create file
            hFile = ctypes.windll.kernel32.CreateFileW(
                output_path,
                0xC0000000, # GENERIC_READ | GENERIC_WRITE
                0,
                None,
                2, # CREATE_ALWAYS
                0x00000080, # FILE_ATTRIBUTE_NORMAL
                None
            )
            
            if hFile == -1:
                logging.error("Could not create dump file.")
                ctypes.windll.kernel32.CloseHandle(hProcess)
                return False

            # Call MiniDumpWriteDump (DbgHelp.dll)
            dbghelp = ctypes.windll.LoadLibrary("DbgHelp.dll")
            
            # BOOL MiniDumpWriteDump(
            #   HANDLE hProcess,
            #   DWORD ProcessId,
            #   HANDLE hFile,
            #   MINIDUMP_TYPE DumpType,
            #   PMINIDUMP_EXCEPTION_INFORMATION ExceptionParam,
            #   PMINIDUMP_USER_STREAM_INFORMATION UserStreamParam,
            #   PMINIDUMP_CALLBACK_INFORMATION CallbackParam
            # );
            
            success = dbghelp.MiniDumpWriteDump(
                hProcess,
                pid,
                hFile,
                MiniDumpWithFullMemory, 
                None,
                None,
                None
            )
            
            ctypes.windll.kernel32.CloseHandle(hFile)
            ctypes.windll.kernel32.CloseHandle(hProcess)
            
            return success != 0

        except Exception as e:
            logging.error(f"Minidump exception: {e}")
            return False
