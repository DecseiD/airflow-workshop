# Module 03: Operational Pain Points & Production Troubleshooting

> Recommended placement in this workshop: **final capstone module** after monitoring.

Welcome to Module 03 of the Apache Airflow Workshop! Running Apache Airflow in enterprise production environments brings unique challenges around scheduler latency, UI scaling, local vs remote developer feedback loops, and security isolation.

This module provides senior-level operational insights and practical solutions to common production failure modes.

---

## 1. Module Contents

* **[`troubleshooting_guide.md`](./troubleshooting_guide.md)**: Comprehensive, production-tested field guide covering 4 critical operational domains:
  1. **UI & Scheduler Dysfunction** (Missing DAGs, Scheduler heartbeats, DB connection pool exhaustion)
  2. **Developer Experience & "Sync Tax"** (Git-sync delays, remote execution limits, fast feedback loops)
  3. **Webserver Performance & 502/504 Errors** (Gunicorn tuning, webserver healthchecks, UI scaling)
  4. **Security Vulnerabilities & Log Isolation** (CVE-2025-66236 context, read/write path attacks, strict log volume isolation)

* **[`known_issues.md`](./known_issues.md)**: Curated known-issues backlog imported from external workshop notes, normalized into a structured Description / Identification / Mitigation format.

---

## 2. Recommended Reading
- Start with [`troubleshooting_guide.md`](./troubleshooting_guide.md) for root-cause analyses, CLI diagnostic commands, and production mitigation strategies.
- Then review [`known_issues.md`](./known_issues.md) for advanced, high-scale failure patterns and mitigation playbooks.
