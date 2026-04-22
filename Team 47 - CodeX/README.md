## Problem Statement

Modern cyberattacks on financial institutions rarely happen in a single event. An Advanced Persistent Threat (APT) attacker:
- Enters through a **low-security machine** using stolen credentials
- Moves **laterally** across systems over hours, staying below the radar
- Eventually reaches the most **sensitive financial data**

Traditional threshold-based alerting misses these attacks because each individual step looks legitimate. This system detects the **full attack pattern** — not just individual anomalies — by combining spatial, role-based, and temporal analysis.

---

## Overview
The APT Detection Engine identifies multi-step cyberattacks by analyzing user activity across a network.It:
- Models the system as a network graph
- Tracks user traversal paths
- Applies role-based, spatial, and time-based analysis
Detects patterns like unauthorized access, abnormal movement, and off-hour activity

Use Case
- Applicable to any organization with:
- Interconnected systems
- Role-based access
- Sensitive distributed data
> Examples:banks, hospitals, corporate IT systems, enterprises
---

## Data Structures and Algorithms Used

| # | DSA Component | Class | Responsibility |
|---|---------------|-------|----------------|
| 1 | **Graph** (Adjacency List) | `NetworkGraph` | Stores 8 nodes and 9 directed edges; models all network paths |
| 2 | **Hash Table** | `PermissionStore` | O(1) role and permission lookup per access event |
| 3 | **BFS** | `BFSAnalyzer` | Finds shortest path between devices; computes hop depth for lateral movement detection |
| 4 | **Trie** | `TrieEngine` | Stores known APT signatures as device sequences; matches session paths in O(m) |
| 5 | **Segment Tree** | `SegmentTree` | Divides the day into 24 hourly buckets; detects off-hours login bursts via range queries |
| 6 | **Priority Queue** (Max-Heap) | `AlertEngine` | Ranks all users by risk score; highest threat surfaces first |

---

##  System Flow

```
Input: User sessions (device, hour, minute per event)
         │
         ▼
┌─────────────────────────────────────────────────┐
│  For each event in session:                     │
│  ├── Graph check  → Does this edge exist?       │
│  ├── Hash Table   → Is this node permitted?     │
│  └── Segment Tree → Log event in hourly bucket  │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  BFS Analysis                                   │
│  └── Compute path from first → last device      │
│      Flag if hop depth exceeds role threshold   │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  Trie Matching                                  │
│  └── Convert session path to device sequence    │
│      Match against all preloaded APT signatures │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  Segment Tree Query                             │
│  └── Query buckets 22–23 and 0–2 (off-hours)    │
│      Flag if burst count ≥ 2                    │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  Risk Score Computed → Pushed to Max-Heap       │
└─────────────────────────────────────────────────┘
         │
         ▼
Output: Ranked alert dashboard + securebank_apt.log
```

---

##  Features

- **Graph-based network model** — Directed adjacency list with node metadata (zone, sensitivity, required role)
- **Role-based access control** — Hash table enforces permissions at O(1) per event
- **Lateral movement detection** — BFS identifies shortest path and flags excessive hop depth per role
- **APT signature matching** — Trie engine preloads 4 known bank breach patterns for O(m) matching
- **Temporal burst detection** — Segment Tree catches off-hours activity (10 PM – 2 AM) that graph analysis alone cannot see
- **Risk-ranked alerting** — Max-heap priority queue always surfaces the highest-threat user first
- **Colour-coded terminal dashboard** — ANSI-formatted threat intelligence report
- **Persistent log file** — Plain-text `securebank_apt.log` generated after every run

---

## Input Format

Network topology, nodes, edges, users, and APT signatures are defined in `config_final.txt`. Below is an example of session inputs used for demonstration:
| User | Role | Session Path |
|------|------|--------------|
| Priya | TELLER | WS-TELLER-01 → INTRA-SRV-01 (business hours) |
| Sneha | LOAN | WS-LOAN-03 → INTRA-SRV-01 → REPORT-SRV-01 (business hours) |
| Rajan | OPS | WS-OPS-02 → INTRA-SRV-01 → AUDIT-SRV-01 → VAULT-DB-01 (10 PM – 2 AM) |

---

## Output

After every run, the system produces two outputs:

**Terminal dashboard** — a colour-coded threat intelligence report showing each user’s session analysis (authorized/unauthorized access, path analysis, pattern matching, and activity bursts), followed by a ranked alert table and a score summary indicating risk levels (e.g., Critical, Suspicious, Clear).

**Log file** (`securebank_apt.log`) — the same report in plain text, saved to disk without ANSI codes.

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

> Alert fires when score exceeds threshold (default: **30**)

---

### Files

| File | Description |
|------|-------------|
| `apt_detection.cpp` | Full C++17 source — single file, no dependencies |
| `config_final.txt` | Network topology, users, and APT signatures |
| `securebank_apt.log` | Plain-text session log generated after each run |
| `securebank_apt` | Compiled binary (after running g++ command) |

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **C++17** | Core implementation |
| **STL** (`unordered_map`, `queue`, `priority_queue`) | All DSA components |
| **ANSI escape codes** | Colour-coded terminal output |
| **pybind11 + Python** *(optional)* | Python bindings via `bindings.cpp` |
| **PowerShell** *(optional)* | Alert notification via `send_alert.ps1` |

---
## Vedio link

---

*Cummins College of Engineering · DSA Competition Project 2025*
README.md
Displaying README.md.
