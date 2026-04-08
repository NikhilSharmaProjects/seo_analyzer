# Setup Guide

## 1. Prerequisites

- Python 3.10+
- pip or uv
- Docker (optional, for container run)

## 2. Install Locally

```bash
pip install -e .
```

Or with uv:

```bash
uv sync
```

Create your environment file:

```bash
copy .env.example .env
```

Set your NVIDIA key in `.env`:

```env
NVIDIA_API_KEY=your_real_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/nemotron-3-super-120b-a12b
USE_LLM_BASELINE=1
```

Set submission inference variables in `.env` (required by hackathon evaluator):

```env
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=nvidia/Nemotron-3-Super-49B-v1
HF_TOKEN=your_hf_token_here
LOCAL_IMAGE_NAME=seo-analyzer-env
ENV_BASE_URL=http://127.0.0.1:8000
```

## 3. Run Server

```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

Open API docs:

- http://localhost:8000/docs

## 4. Quick API Checks

```bash
# Task catalog
curl http://localhost:8000/tasks

# Reset singleton to medium task
curl -X POST "http://localhost:8000/task/reset?task_id=medium"

# One action step via OpenEnv endpoint
curl -X POST http://localhost:8000/step -H "Content-Type: application/json" -d "{\"action_type\":\"fix_title\"}"

# Deterministic grader
curl -X POST http://localhost:8000/grader -H "Content-Type: application/json" -d "{\"task_id\":\"easy\",\"html\":\"<html><body><h1>Running Shoes</h1></body></html>\"}"

# Baseline run
curl http://localhost:8000/baseline

# Submission inference run (strict [START]/[STEP]/[END] logs)
python inference.py
```

## 5. Docker Build and Run

```bash
docker build -t seo-analyzer-env -f server/Dockerfile .
docker run --rm -p 8000:8000 seo-analyzer-env
```

## 6. Hugging Face Spaces

This project is Docker-compatible and includes openenv.yaml. Push as a Docker Space.
