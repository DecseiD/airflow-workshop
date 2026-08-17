# Module 05: Git-Based DAG Retrieval (Production-Like Developer Workflow)

This module demonstrates a **production-style DAG delivery flow** where Airflow reads DAGs from a Git repository instead of manual file copy.

> Goal: model real team workflows (branch -> merge -> sync -> scheduler parse -> DAG appears).

---

## 1) Why this module matters

In small local demos, copying DAG files directly into mounted folders is fast.
In production, teams usually ship DAGs through source control and a sync mechanism.

This module shows:
- how a DAG repo is polled and synced automatically
- how scheduler picks up changes after sync
- how to triage common sync/import issues

---

## 2) Local architecture (module scope)

- Airflow core stack runs from `01_install/docker-compose.yaml`
- A `git-sync` sidecar container clones/pulls a DAG Git repo into `01_install/dags`
- Scheduler/webserver read DAGs from that folder

```text
DAG Repo (Git) -> git-sync container -> ./01_install/dags -> Airflow scheduler/webserver
```

---

## 3) Prerequisites

- Airflow module 01 is running
- Git repository exists with DAG files under a folder like `dags/`
- Local host has outbound access to the Git remote

> For private repos, use SSH deploy keys and known_hosts pinning.

---

## 4) Configure git-sync env file

Create `airflow/05_git_based_dag_retrieval/.env.git-sync` from the example:

```bash
cp .env.git-sync.example .env.git-sync
```

Edit values:
- `GIT_SYNC_REPO`
- `GIT_SYNC_BRANCH`
- `GIT_SYNC_PERIOD`
- `GIT_SYNC_SUBPATH`

---

## 5) Start git-sync overlay

From `airflow/01_install`:

```bash
docker compose \
  -f docker-compose.yaml \
  -f ../05_git_based_dag_retrieval/docker-compose.git-sync.yaml \
  --env-file ../05_git_based_dag_retrieval/.env.git-sync \
  up -d git-sync
```

Check sync logs:

```bash
docker compose -f docker-compose.yaml -f ../05_git_based_dag_retrieval/docker-compose.git-sync.yaml logs -f git-sync
```

---

## 6) Verify DAG retrieval

```bash
# Verify files synced into local DAG mount
ls -la airflow/01_install/dags

# Verify Airflow can see DAGs
docker compose -f airflow/01_install/docker-compose.yaml exec airflow-scheduler airflow dags list
```

Expected result: DAGs from the Git repo become visible in Airflow UI without manual copy.

---

## 7) Developer workflow demo sequence

1. Create/update a DAG in the DAG repo.
2. Push to branch configured in `GIT_SYNC_BRANCH`.
3. Wait one sync interval.
4. Confirm `git-sync` logs show new commit hash.
5. Confirm scheduler imports DAG successfully.
6. Trigger DAG in UI.

---

## 8) Common failure cases

- **Repo auth fails** -> validate SSH key mount / token and known_hosts.
- **DAG not visible** -> verify `GIT_SYNC_SUBPATH` and scheduler import errors:

```bash
docker compose -f airflow/01_install/docker-compose.yaml exec airflow-scheduler airflow dags list-import-errors
```

- **Wrong branch/tag** -> validate `GIT_SYNC_BRANCH` and `GIT_SYNC_REV` settings.
