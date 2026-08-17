# Known Issues Backlog

Use it as an advanced troubleshooting appendix alongside `troubleshooting_guide.md`.

---

## 1) Kernel-Level Memory Limits & Zombie Tasks

**Description**  
Worker pods exceed memory limits and get terminated by `SIGKILL` (`OOMKilled`). Airflow exception handling cannot complete, so tasks can remain stuck in `RUNNING`.

**How to identify**  
Use `kubectl describe pod` and check `Last State: Terminated` with `Reason: OOMKilled`.

**Mitigations**
- Increase memory limits.
- Add active memory monitoring to trigger software exceptions before hard OOM.
- Use pre-oom handling (`preoomkiller`) for graceful `SIGTERM` behavior.
- Evaluate Kubelet `singleProcessOOMKill`.

---

## 2) Database Connection Exhaustion & PgBouncer Bottlenecks

**Description**  
High task concurrency creates a connection storm that overwhelms PostgreSQL's process-per-connection model.

**How to identify**
- Random 30–40 second startup delays.
- Logs like:
  - `Unable to retrieve connection from secrets backend`
  - `FATAL: sorry, too many clients already`

**Mitigations**
- Run PgBouncer in **transaction** mode.
- Disable Airflow internal SQLAlchemy pooling:
  - `AIRFLOW__CORE__SQL_ALCHEMY_POOL_SIZE=0`
  - `MAX_OVERFLOW=-1`
- Set `CONNECTION_CHECK_MAX_COUNT=0` to avoid repeated startup connection checks.

---

## 3) API Server Overload & Uvicorn Memory Leaks

**Description**  
Large heartbeat/XCom volume from worker pods causes FastAPI/Uvicorn workers to bloat memory (up to ~1 GiB each), leading to pod termination.

**How to identify**
- API pods crash with `OOMKilled`.
- UI intermittently returns `503`.
- API pod startup latency grows (up to ~4 minutes).

**Mitigations**
- Run one Uvicorn worker process per container.
- Scale horizontally instead of vertically increasing worker processes.
- Add rate limiting via NGINX/Envoy, or tune Kubernetes API Priority and Fairness (APF).

---

## 4) Scheduler Race Conditions & Orphaned Processes

**Description**  
Under HA scheduling, competing transactions may incorrectly classify active KubernetesExecutor pods as dead/orphaned and terminate them prematurely.

**How to identify**
- `try_number` increases unexpectedly.
- UI marks task `FAILED` while backing pod is still running correctly.

**Mitigations**
- Temporarily reduce active scheduler replicas during extreme load.
- Increase `scheduler_health_check_threshold` to avoid false restart loops.

---

## 5) Triggerer Loop Starvation & Thread-Safety Crashes

**Description**  
Synchronous I/O inside Triggerer async loops blocks progress; non-thread-safe locking in messaging paths can cause decoding crashes.

**How to identify**
- `Async thread blocked` warnings.
- Fatal `RuntimeError: Response read out of order!`
- Tasks stuck in `DEFERRED`.

**Mitigations**
- Remove synchronous SDK calls from async run loops.
- Lower `AIRFLOW__TRIGGERER__DEFAULT_CAPACITY`.
- Scale Triggerer replicas horizontally.

---

## 6) Storage Anomalies: Multi-Attach PVC Errors

**Description**  
Concurrent scheduling can trigger shared PVC multi-attach contention beyond storage protocol capability.

**How to identify**
- Pod startup stalls.
- Event log includes: `Multi-Attach error for volume ... volume is already exclusively attached`.

**Mitigations**
- Prefer image-baked DAG delivery for high-scale workloads.
- Avoid fragile shared-volume DAG delivery where storage class semantics conflict with workload concurrency.

---

## 7) KEDA Dynamic Scaling & Graceful Termination Failures

**Description**  
During downscaling, workers receive `SIGTERM` then `SIGKILL` too quickly; long-running tasks are aborted before warm shutdown completes.

**How to identify**
- Task failures align with HPA/KEDA replica reductions.
- Worker logs show `SIGTERM/SIGKILL` around scale-down windows.

**Mitigations**
- Set `terminationGracePeriodSeconds` above max task runtime.
- Set `worker_prefetch_multiplier=1`.
- Add `preStop` hooks to delay termination until active tasks drain.
- Prefer Deployments over StatefulSets where that model fits worker lifecycle.
