# OGT WatchTower V2 - Upgrade Proposal

## Executive Summary
Version 1 of OGT WatchTower established a solid foundation for behavioral monitoring. Version 2 will transition the tool from a "proof of concept" to a **professional-grade security tool** by adopting industry-standard detection engines, enhancing visibility with kernel-level telemetry (via Sysmon), and adding forensic capabilities.

## 1. Core Architecture: The "Eagle Eye" Engine
**Current:** Relies on WMI/polling which can be slow and bypassed.
**V2 Upgrade:** **Sysmon Integration + ETW (Event Tracing for Windows)**
-   **Why:** Sysmon provides kernel-level visibility into process creation, network connections, and file changes that WMI misses.
-   **How:** WatchTower will ingest Windows Event Logs (specifically Sysmon Event ID 1, 3, 11) in real-time.
-   **Benefit:** impossible to evade by simple speed; captures parent-child relationships perfectly.

## 2. Detection Engine: "Sigma" Integration
**Current:** Hardcoded Python `if` statements (e.g., `if "urlcache" in cmd`).
**V2 Upgrade:** **Sigma Rule Support**
-   **Why:** Hardcoded rules are hard to maintain. Sigma is the "standard" for detection rules (like Snort for firewalls).
-   **How:** Implement a parser to load `.yml` Sigma rules.
-   **Benefit:** You can instantly import thousands of community-created rules for new threats without writing code.

## 3. File Analysis: YARA Scanning
**Current:** Only looks at command line arguments.
**V2 Upgrade:** **YARA Rule Engine**
-   **Why:** Attackers rename binaries (e.g., renaming `powershell.exe` to `notepad.exe`). Command line analysis fails here.
-   **How:** When a process starts, scan its memory/disk image against YARA signatures to identify the *true* identity of the tool.

## 4. Threat Intelligence: "Cloud Sentry"
**Current:** Local analysis only.
**V2 Upgrade:** **VirusTotal / AbuseIPDB Integration**
-   **Why:** Leverages global intelligence.
-   **How:** Automatically hash the binary and query VirusTotal API. Check connection IPs against AbuseIPDB.

## 5. Response: Forensic Snapshots
**Current:** Suspends process.
**V2 Upgrade:** **Automated Forensics**
-   **Why:** Killing a process destroys evidence.
-   **How:** Before killing:
    1.  Dump process memory (`minidump`).
    2.  Copy the suspicious command line and parent tree to a secured report.
    3.  *Then* terminate/isolate.

## 6. UI: "Command Center"
**Current:** Simple Tkinter Dashboard.
**V2 Upgrade:** **Modern Cyberpunk/Glassmorphism UI**
-   **How:** Enhanced CustomTkinter with animated graphs, attack trees (visualizing parent-child process chains), and a "Live Attack Map".

---

## Roadmap for Implementation

### Phase 1: The Engine Swap
- [ ] Replace `behavior_analyzer.py` with a **Sigma Rule Parser**.
- [ ] Replace `process_monitor.py` logic to consume **Windows Event Logs**.

### Phase 2: The Eyes
- [ ] Implement **YARA** scanning for every new process.
- [ ] Add **VirusTotal API** checks (async to allow execution but flag later).

### Phase 3: The Shield
- [ ] Implement **Process Memory Dumping**.
- [ ] Create the new **Advanced Dashboard**.

## User Decision Point
Which of these "Big Improvements" excites you the most? I recommend starting with **Phase 1 (Sigma & Event Logs)** as it fundamentally changes the power of the tool.
