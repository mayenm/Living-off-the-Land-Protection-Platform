# SOP – OGT WatchTower V2 Development

## 1. Purpose

This Standard Operating Procedure (SOP) defines the **step-by-step development process** for upgrading **OGT WatchTower** from Version 1 (Proof of Concept) to **Version 2 (Professional-Grade Security Tool)**.

## 2. Scope

This SOP covers:
* Core engine refactor
* Detection logic modernization
* Telemetry and visibility enhancement
* Threat intelligence integration
* Incident response and forensics
* UI/UX evolution

## 3. Guiding Principles

1. **Detection before UI** – Engine power is more important than visuals
2. **Standards over custom logic** – Prefer Sigma, YARA, Sysmon over hardcoded rules
3. **Evidence preservation** – Never terminate a process before collecting artifacts
4. **Extensibility** – Any logic must support future rule expansion

## 4. Architecture Overview (V2 Target)

* Telemetry Layer (Sysmon + Windows Event Logs)
* Detection Engine (Sigma Rule Processor)
* File Identity Engine (YARA)
* Threat Intelligence Module (Cloud APIs)
* Response & Forensics Module
* Command Center UI

## 5. Phase 1 – Core Engine Swap (MANDATORY FIRST PHASE)

### 5.1 Objective
Replace polling-based logic and hardcoded detections with **event-driven, rule-based detection**.

### 5.2 Tasks
#### 5.2.1 Sysmon Deployment
* Install Sysmon with a hardened configuration
* Enable at minimum:
  * Event ID 1 – Process Creation
  * Event ID 3 – Network Connection
  * Event ID 11 – File Creation

#### 5.2.2 Event Log Ingestion
* Implement a real-time Windows Event Log consumer
* Parse Sysmon events into structured internal objects
* Preserve:
  * Parent/Child relationships
  * Command line arguments
  * Hashes (if available)

#### 5.2.3 Sigma Rule Engine
* Implement Sigma rule loader (.yml files)
* Convert Sigma logic into executable detection conditions
* Support at minimum:
  * process_creation
  * command_line matching
  * parent_image matching

## 6. Phase 2 – Visibility & Intelligence Expansion

### 6.1 YARA File Analysis
* Integrate YARA engine
* On each new process creation:
  * Extract binary path
  * Scan disk image or memory
  * Match against YARA rule set

### 6.2 Cloud Threat Intelligence ("Cloud Sentry")
* Hash suspicious binaries (SHA256)
* Query VirusTotal API asynchronously
* Check destination IPs against AbuseIPDB

## 7. Phase 3 – Response & Forensics (DO NOT SKIP ORDER)

### 7.1 Forensic Snapshot Collection
1. Capture full command line
2. Capture parent-child process tree
3. Dump process memory (minidump)
4. Store artifacts in secured directory

### 7.2 Containment
* Only after forensic capture:
  * Suspend
  * Terminate
  * Isolate process

## 8. Phase 4 – Command Center UI

### 8.1 UI Principles
* UI reflects engine output, not replaces it
* Zero clutter
* Dark-theme first

### 8.8 UI Development Rule (CRITICAL)
**UI must consume engine output only. UI must never implement detection logic.**

## 10. Final Success Criteria
* Detection logic is 100% rule-based
* Sysmon is the primary telemetry source
* YARA confirms binary identity
* Forensic artifacts are preserved
* UI accurately visualizes attack chains
