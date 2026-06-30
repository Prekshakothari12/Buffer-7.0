# SECUREBANK APT DETECTION ENGINE

Team Name: CodeX
Team Members: Preksha Kothari, Akshita Pahade
Theme: Cybersecurity and Digital Defence
Language: C++ (core engine), Python (server, dashboard, bindings)

## Demo video
https://drive.google.com/file/d/1neuQGZlI4xv3aLVqiM6ExmGwrxXZiZaM/view?usp=sharing

## Problem Statement

Modern cyberattacks on financial institutions rarely happen in a single event. An Advanced Persistent Threat (APT) attacker:
- Enters through a **low-security machine** using stolen credentials
- Moves **laterally** across systems over hours, staying below the radar
- Eventually reaches the most **sensitive financial data**

Traditional threshold-based alerting misses these attacks because each individual step looks legitimate. This system detects the **full attack pattern** — not just individual anomalies — by combining spatial, role-based, and temporal analysis, and now does so **live**, across real networked machines, rather than only on static input files.

---

## Overview

The APT Detection Engine identifies multi-step cyberattacks by analyzing live user activity streamed from client machines across a network. It:
- Models the bank's internal network as a graph
- Tracks user traversal paths in real time
- Applies role-based, spatial, and time-based analysis
- Scores and ranks users by risk, with automatic account lockout above a threshold
- Surfaces results on a live SOC analyst dashboard, backed by a persistent database

**Use Case** — Applicable to any organization with interconnected systems, role-based access, and sensitive distributed data (banks, hospitals, corporate IT systems, enterprises).

---

## What's New in This Version

The project has evolved from a single-binary CLI tool into a full client-server security platform:

- **Live client-server architecture** — multiple client agents (`client.py`) run on separate physical machines and stream real-time security events over HTTP to a central detection server, instead of reading a static config file.
- **Flask REST API server** (`server.py` / `app.py`) — receives events at `/events`, exposes `/ping` and `/status/<username>` for health checks and account status, and runs the C++ detection engine live on incoming data.
- **Automatic account lockout** — when a user's risk score crosses the alert threshold, the server returns **HTTP 403** on subsequent events, and the client agent terminates itself, simulating a real-time SOC response.
- **Streamlit SOC Dashboard** (`app.py`) — a dark-themed, live-updating analyst dashboard for monitoring events, alerts, and risk scores, embedding the Flask API in the same process.
- **MySQL persistence layer** — all incoming events and generated alerts are stored in a MySQL database (`events`, `alerts` tables) instead of a flat log file, queryable via a CLI utility (`db_viewer.py`).
- **Python bindings via pybind11** (`bindings.cpp`) — the C++ detection core (Graph, Trie, Segment Tree, BFS, Priority Queue) is compiled into a Python extension module (`apt_engine`) and called directly from the Flask/Streamlit layer, removing the need for file-based handoff between C++ and Python.
- **Bug fixes for production-grade scoring** — corrected a phantom self-loop edge defect in the graph traversal logic and fixed an incorrect verdict-threshold calculation in `live_verdict_label()`, improving live detection accuracy.

---

## Data Structures and Algorithms Used

| # | DSA Component | Class | Responsibility |
|---|---------------|-------|----------------|
| 1 | **Graph** (Adjacency List) | `NetworkGraph` | Stores network nodes and directed edges; models all valid access paths |
| 2 | **Hash Table** | `PermissionStore` | O(1) role and permission lookup per access event |
| 3 | **BFS** | `BFSAnalyzer` | Finds shortest path between devices; computes hop depth for lateral movement detection |
| 4 | **Trie** | `TrieEngine` | Stores known APT signatures as device sequences; matches session paths in O(m) |
| 5 | **Segment Tree** | `SegmentTree` | Divides the day into 24 hourly buckets; detects off-hours login bursts via range queries |
| 6 | **Priority Queue** (Max-Heap) | `AlertEngine` | Ranks all users by live risk score; highest threat surfaces first |

---

## System Architecture

```
   LAPTOP A (Client)            LAPTOP B (Server)
 ┌──────────────────┐         ┌────────────────────────────────────┐
 │   client.py        │         │            app.py / server.py       │
 │  generates &        │  HTTP   │  ┌────────────────────────────┐   │
 │  streams events  │ ──────▶ │  │   Flask REST API            │   │
 │  (per user agent)│  POST    │  │   /events  /ping  /status   │   │
 └──────────────────┘  /events │  └──────────────┬─────────────┘   │
                                 │                 ▼                    │
                                 │  ┌────────────────────────────┐   │
                                 │  │  apt_engine (C++ via         │   │
                                 │  │  pybind11): Graph, Trie,     │   │
                                 │  │  Segment Tree, BFS, Heap     │   │
                                 │  └──────────────┬─────────────┘   │
                                 │                 ▼                    │
                                 │  ┌────────────────────────────┐   │
                                 │  │  MySQL (events, alerts)      │   │
                                 │  └──────────────┬─────────────┘   │
                                 │                 ▼                    │
                                 │  ┌────────────────────────────┐   │
                                 │  │  Streamlit SOC Dashboard     │   │
                                 │  └────────────────────────────┘   │
                                 └────────────────────────────────────┘

  Risk score ≥ threshold → server returns HTTP 403 → client locks out
```

---

## Features

- **Live event streaming** — client agents on real machines post security events over HTTP in real time
- **Graph-based network model** — directed adjacency list with node metadata (zone, sensitivity, required role)
- **Role-based access control** — hash table enforces permissions at O(1) per event
- **Lateral movement detection** — BFS identifies shortest path and flags excessive hop depth per role
- **APT signature matching** — Trie engine preloads known bank breach patterns for O(m) matching
- **Temporal burst detection** — Segment Tree catches off-hours activity that graph analysis alone cannot see
- **Risk-ranked alerting** — max-heap priority queue always surfaces the highest-threat user first
- **Live account lockout** — HTTP 403 enforcement when a user's score crosses the threshold
- **Streamlit SOC dashboard** — dark cybersecurity-themed, live-updating analyst view
- **MySQL-backed persistence** — durable storage for all events and alerts, queryable via `db_viewer.py`
- **PowerShell alerting** — `send_alert.ps1` for native Windows notification on critical alerts

---

## Demo Users

| User | Role | Base City | Allowed Devices |
|------|------|-----------|------------------|
| PRIYA | TELLER | Mumbai | WS-TELLER-01, INTRA-SRV-01 |
| SNEHA | OPS | Pune | WS-LOAN-03, INTRA-SRV-01, REPORT-SRV-01 |
| RAJAN | OPS | Mumbai | WS-OPS-02, INTRA-SRV-01 |
| VIKRAM | SENIOR | Delhi | INTRA-SRV-01, AUDIT-SRV-01, CORE-TXN-SRV, REPORT-SRV-01 |

Each user is simulated by a separate `client.py` agent instance, generating realistic events (device, location, time, records accessed, failed login attempts) and posting them to the server at a configurable interval.

---

### Risk Scoring

| Trigger                                              | Points |
|------------------------------------------------------|--------|
| Unauthorized access to HIGH-security zone            | +40    |
| Unauthorized access to MEDIUM-security zone          | +25    |
| Unauthorized access to LOW-security zone             | +10    |
| Phantom Edge                                         | +40    |
| Initial Phantom Edge                                 | +40    |
| Unknown Device                                       | +20    |
| Off-hours burst (≥ 2 events between 23:00–04:00)     | +20    |
| Weekend Activity                                     | +10    |
| Holiday Activity                                     | +10    |
| APT Signature Match                                  | +30    |
| BFS Depth Exceeded                                   | +5     |

> Alert fires when score exceeds threshold (default: **30**); account lockout (HTTP 403) fires at score ≥ **75**

---

### Files

| File | Description |
|------|-------------|
| `apt_detection.cpp` | C++17 core detection engine — Graph, Trie, Segment Tree, BFS, Priority Queue |
| `bindings.cpp` | pybind11 bindings exposing the C++ engine as the `apt_engine` Python module |
| `setup.py` | Build script to compile `apt_engine` from `bindings.cpp` |
| `app.py` | Streamlit SOC dashboard + embedded Flask API (main entry point) |
| `server.py` | Standalone Flask API launcher (no dashboard) |
| `client.py` | Client monitoring agent run on each machine, streams live events |
| `db_viewer.py` | CLI utility to inspect `events` and `alerts` tables in MySQL |
| `send_alert.ps1` | PowerShell script for native Windows alert notifications |

---

## How to Run (Multi-Laptop Setup)

1. **Server laptop (Laptop B):**
   ```
   streamlit run app.py
   ```
   This starts both the Flask API (port 5000) and the SOC dashboard.

2. **Client laptop(s) (Laptop A, etc.):**
   - Edit `SERVER_IP` in `client.py` to Laptop B's IP address (`ipconfig`)
   - Run one terminal per simulated user:
     ```
     py client.py --user PRIYA --machine LAPTOP-A --interval 30
     ```
   - All laptops must be on the same WiFi network.

3. **View stored data:**
   ```
   python db_viewer.py --table alerts --limit 10
   ```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **C++17** | Core detection engine (Graph, Trie, Segment Tree, BFS, Priority Queue) |
| **STL** (`unordered_map`, `queue`, `priority_queue`) | All DSA components |
| **pybind11** | Python bindings exposing the C++ engine as `apt_engine` |
| **Flask** | REST API for live event ingestion and account status |
| **Streamlit** | SOC analyst dashboard (dark cybersecurity theme) |
| **MySQL** | Persistent storage for events and alerts |
| **Requests** | HTTP client library used by `client.py` agents |
| **PowerShell** | Native alert notification via `send_alert.ps1` |

---
*Cummins College of Engineering · DSA Competition Project, extended into a full client-server security platform 2025*
