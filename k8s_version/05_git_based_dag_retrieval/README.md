# 05_git_based_dag_retrieval — Production-Style DAG Delivery on AKS

This module demonstrates a production-like DAG delivery pattern for Airflow on Kubernetes:

- developers commit DAG code to a Git repository
- a sync mechanism (for example `git-sync`) pulls updates into Airflow pods
- scheduler parses new DAGs automatically

---

## 1) Target workflow

```text
Developer commit -> Git remote -> git-sync poll -> DAG files in pod -> scheduler import -> DAG visible in UI
```

---

## 2) Recommended approach with Helm

Use Airflow Helm chart `dags.gitSync` values so scheduler/webserver use synchronized DAG content.

1. Create secret for repo auth (if private repo).
2. Apply `values-git-sync.yaml` as an overlay with your base values.
3. Upgrade Helm release.
4. Verify `git-sync` container logs and DAG visibility.

---

## 3) Example commands

```bash
# optional: secret for private repo (ssh key)
kubectl -n airflow create secret generic airflow-git-ssh \
  --from-file=ssh=/path/to/id_rsa \
  --from-file=known_hosts=/path/to/known_hosts

# upgrade airflow with git-sync overlay
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f ../01_install/values-airflow.yaml \
  -f values-git-sync.yaml
```

---

## 4) Verification

```bash
kubectl get pods -n airflow
kubectl logs -n airflow deploy/airflow-scheduler -c git-sync --tail=200
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list
```

Expected:
- `git-sync` logs show recent commit sync
- DAGs from Git repo appear in Airflow UI

---

## 5) Failure triage

- **auth/clone errors** -> validate repo URL, SSH key secret, known_hosts
- **DAG missing** -> validate branch/revision/subPath in values file
- **import errors** -> run:

```bash
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list-import-errors
```
