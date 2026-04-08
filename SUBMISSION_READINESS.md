# Submission Readiness

This checklist is aligned to the official pre-submission gate.

## Pass/Fail Gate

- HF Space deploys and responds to `/reset`: PENDING (run after deploy)
- OpenEnv spec compliance (`openenv validate`): PENDING
- Dockerfile builds (`docker build`): PENDING
- Baseline inference script runs without error: READY (script exists and is wired)
- 3+ tasks with graders scoring in [0.0, 1.0]: READY

## Evidence Map

- OpenEnv manifest: openenv.yaml
- Environment API: server/environment.py
- Server endpoints: server/app.py
- Grader logic: grader.py
- Scoring engine: seo_engine.py
- Inference script: inference.py
- Local proof script: test_case.py

## Final Pre-Submit Commands

1. `python -m uvicorn server.app:app --host 127.0.0.1 --port 8000`
2. `python baseline.py`
3. `python test_case.py`
4. `docker build -t seo-analyzer-env -f server/Dockerfile .`
5. `openenv validate`
6. `bash prevalidationScript.sh <your_hf_space_url> .`
