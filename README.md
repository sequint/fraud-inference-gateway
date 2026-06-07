# Fraud Inference Gateway

An enterprise-grade API gateway and middleware abstraction layer built to bridge modern, high-concurrency client demands with low-concurrency, legacy core banking backends. 

This microservice acts as an asynchronous traffic controller and inline security proxy—normalizing transactional payloads, enforcing data sanitization, and routing outbound transactions based on real-time vector inference.

## Architecture Overview

In a typical community financial institution, the core ledger system (mainframe) is incapable of scaling to meet real-time web or mobile app traffic, nor can it execute sub-millisecond fraud analysis. 

This gateway solves that bottleneck by executing a split-path architecture:
1. **Inline Inference Guard:** Transactions are intercepted and routed to a secured, private AWS high-performance C++ vector engine (`NanoHD`) via a secure API handshake (`X-API-KEY`).
2. **Asynchronous Ledger Ingestion:** Cleared transactions are translated into legacy-compliant layouts and safely queued to prevent transactional bottlenecks or core vendor fatigue.

[ Modern Mobile Transaction ]
│
▼
+---------------------------------------+
|        fraud-inference-gateway        |
|          (Python / Flask)             |
+---------------------------------------+
│                               │
│ (Secure Async Rest API)       │ (Buffered Staging Queue)
▼                               ▼
+-----------------------+   +--------------------------------+
|  Private NanoHD ML    |   |  financial-legacy-core-synth   |
| (C++ Vector Engine)   |   | (Simulated Batch Mainframe)    |
+-----------------------+   +--------------------------------+

## Tech Stack
* **Language:** Python 3.10+
* **Framework:** Flask (Lightweight enterprise routing proxy)
* **Integrations:** `requests` for decoupled service orchestration
