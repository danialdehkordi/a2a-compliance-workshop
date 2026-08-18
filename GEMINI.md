# Project Rules & Workflow Guidelines

## Deployment & CI/CD Tracking
- **No polling loops on `gh run list`**: When monitoring GitHub Actions workflows or deployments, DO NOT run repetitive polling loops (`gh run list` / `sleep`).
- **Use single-shot blocking commands or reactive waits**: Use `gh run watch <run-id>` or background execution tasks that notify only upon completion.
- **Always deploy GCP resources to `europe-west3`** unless explicitly specified otherwise.
