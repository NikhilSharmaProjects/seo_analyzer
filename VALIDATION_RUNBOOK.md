# Validation Runbook

## Local Runtime

1. Install dependencies:
    - `pip install -e .`
2. Start server:
    - `python -m uvicorn server.app:app --host 127.0.0.1 --port 8000`
3. Check API:
    - `curl http://127.0.0.1:8000/tasks`
    - `curl -X POST "http://127.0.0.1:8000/task/reset?task_id=easy"`

## Functional Verification

1. Baseline:
    - `python baseline.py`
2. Test case:
    - `python test_case.py`
3. Inference format:
    - `python inference.py`

## Container Verification

1. Build:
    - `docker build -t seo-analyzer-env -f server/Dockerfile .`
2. Run:
    - `docker run --rm -p 8000:8000 seo-analyzer-env`
3. Probe:
    - `curl -X POST http://127.0.0.1:8000/reset -H "Content-Type: application/json" -d '{}'`

## Official Validator

Use the provided script:

- `bash prevalidationScript.sh <your_hf_space_url> .`

### Windows PowerShell (recommended)

- `./prevalidationScript.ps1 -PingUrl "https://your-space.hf.space" -RepoDir "."`

### Windows + Git Bash (alternative)

- `bash ./prevalidationScript.sh https://your-space.hf.space .`

### Common Windows Errors

- `/usr/bin/env not recognized`
    - Cause: command is Unix-style and not valid in PowerShell.
    - Fix: use `bash ./prevalidationScript.sh ...` in Git Bash, or use `prevalidationScript.ps1`.

- `failed to connect to the docker API ... dockerDesktopLinuxEngine`
    - Cause: Docker Desktop daemon is not running.
    - Fix: start Docker Desktop and wait until it says Engine running, then rerun build/validation.
