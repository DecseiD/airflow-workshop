# Contributing

Thanks for contributing to this workshop repo.

## Scope
This repository is a **demo/tutorial** project optimized for local lab runs.

## Contribution Guidelines
- Keep changes runnable on local Docker Compose setup.
- Keep docs environment-neutral (use placeholders like `<HOST_IP>`).
- Keep demo credentials/examples aligned with existing workshop flow.
- Prefer small, focused PRs with clear rationale.

## Documentation Rules
- Avoid personal infrastructure details (real hostnames, private paths, private IPs).
- Use relative links in Markdown.

## Code Style
- Python: keep functions readable and avoid unnecessary abstraction.
- DAG changes must keep connection id `iot_db_conn` unless docs are updated.

## Validation
- Verify modified commands are executable as written.
- Verify dashboard/API docs match real endpoint names.
