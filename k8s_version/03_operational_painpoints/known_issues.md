# Known Issues Backlog (AKS Edition)

Imported and normalized from an external workshop known-issues source file.

This companion document extends the AKS troubleshooting module with high-scale failure patterns.

---

## 1) Kernel-Level Memory Limits & Zombie Tasks

**Description**  
Worker pods exceed memory limits and are terminated with `SIGKILL` (`OOMKilled`), leaving Airflow state transitions incomplete and tasks stuck in `RUNNING`.

**How to identify**  
`kubectl describe pod` -> `Last State: Terminated`, `Reason: OOMKilled`.

**Mitigations**
- Increase memory limits/requests for workers and scheduler.
- Add memory telemetry and alerting before hard OOM.
- Use pre-oom handling for graceful `SIGTERM` where applicable.
- Evaluate Kubelet `singleProcessOOMKill` behavior for your node pool profile.

---

## 2) Database Connection Exhaustion & PgBouncer Bottlenecks

**Description**  
High DAG/task concurrency creates connection storms that saturate PostgreSQL.

**How to identify**
- Random 30–40 second startup delays
- Logs with:
  - `Unable to retrieve connection from secrets backend`
  - `FATAL: sorry, too many clients already`

**Mitigations**
- Run PgBouncer in **transaction** mode.
- Disable internal SQLAlchemy pooling where appropriate:
  - `AIRFLOW__CORE__SQL_ALCHEMY_POOL_SIZE=0`
  - `MAX_OVERFLOW=-1`
- Set `CONNECTION_CHECK_MAX_COUNT=0` to reduce startup connection checks.

---

## 3) API Server Overload & Uvicorn Memory Leaks

**Description**  
Heavy heartbeat/XCom volume can cause FastAPI/Uvicorn process memory growth and OOM restarts.

**How to identify**
- API pods crash with `OOMKilled`
- UI intermittently returns `503`
- API pod startup latency rises significantly

**Mitigations**
- Run one Uvicorn worker process per container.
- Prefer horizontal pod scaling.
- Add rate limiting (NGINX/Envoy) or tune Kubernetes APF objects.

---

## 4) Scheduler Race Conditions & Orphaned Processes

**Description**  
In HA scheduler setups, transaction races can misclassify active KubernetesExecutor pods as dead/orphaned.

**How to identify**
- `try_number` increments unexpectedly
- Task marked `FAILED` in UI while pod remains healthy

**Mitigations**
- Temporarily reduce scheduler replicas under extreme load.
- Increase `scheduler_health_check_threshold` to reduce false restart behavior.

---

## 5) Triggerer Loop Starvation & Thread-Safety Crashes

**Description**  
Blocking synchronous I/O in Triggerer async loops and unsafe locking patterns can crash message handling.

**How to identify**
- `Async thread blocked` warnings
- `RuntimeError: Response read out of order!`
- Tasks stuck in `DEFERRED`

**Mitigations**
- Remove synchronous SDK calls from async Triggerer loops.
- Lower `AIRFLOW__TRIGGERER__DEFAULT_CAPACITY`.
- Scale Triggerer replicas horizontally.

---

## 6) Storage Anomalies: Multi-Attach PVC Errors

**Description**  
Concurrent pod scheduling can trigger PVC multi-attach conflicts depending on storage class access semantics.

**How to identify**
- Pod startup stalls
- Events include `Multi-Attach error for volume ... already exclusively attached`

**Mitigations**
- Prefer image-baked DAG delivery for high-scale workloads.
- Avoid shared-volume DAG patterns that conflict with storage access mode constraints.

---

## 7) KEDA Dynamic Scaling & Graceful Termination Failures

**Description**  
During scale-down, workers may receive `SIGTERM` then `SIGKILL` before long-running tasks drain.

**How to identify**
- Task failures correlate with HPA/KEDA downscale events
- Worker logs show `SIGTERM`/`SIGKILL` near replica reduction

**Mitigations**
- Set `terminationGracePeriodSeconds` above max task duration.
- Set `worker_prefetch_multiplier=1`.
- Add `preStop` hook to wait for active tasks to drain.
- Prefer Deployments over StatefulSets when appropriate for worker lifecycle.