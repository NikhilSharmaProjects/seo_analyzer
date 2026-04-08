---
title: SEO Analyzer
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
tags:
    - openenv
    - reinforcement-learning
    - seo
---

# AI SEO Optimization Environment (OpenEnv)

This project is a reinforcement learning environment where an agent improves low-quality HTML into SEO-optimized HTML through iterative actions.

It is built for the Meta PyTorch OpenEnv Hackathon and focuses on practical, real-world SEO optimization rather than static analysis only.

## Why This Matters

Most SEO tools stop at reporting issues. This environment turns SEO into a sequential decision-making problem:

1. Observe current HTML quality.
2. Choose one SEO action.
3. Measure improvement and assign reward.
4. Repeat until target quality is reached.

This setup is ideal for RL training, policy benchmarking, and autonomous optimization research.

## Key Features

- OpenEnv-compatible environment with reset, step, and state support.
- Pydantic models for Action, Observation, State, Reward, Grader, and Baseline outputs.
- Deterministic SEO scoring using BeautifulSoup.
- Three tasks with increasing difficulty:
    - easy: target >= 70
    - medium: target >= 85
    - hard: target >= 95
- Dense reward function with improvement rewards and penalties for poor behavior.
- Required API endpoints:
    - /reset
    - /step
    - /state
    - /tasks
    - /grader
    - /baseline
- Docker-ready deployment for local runs and Hugging Face Spaces.
- NVIDIA Nemotron support via OpenAI-compatible client for baseline action selection.

## Project Structure

- models.py: All core Pydantic contracts.
- seo_engine.py: Deterministic SEO scoring logic (0-100).
- environment.py: Public export of the OpenEnv environment class.
- grader.py: Deterministic final grading (0.0-1.0).
- baseline.py: Reproducible baseline policy runner.
- app.py: Root FastAPI app re-export.
- server/environment.py: OpenEnv environment implementation.
- server/app.py: FastAPI app + custom task/grader/baseline endpoints.
- server/Dockerfile: Container runtime.
- openenv.yaml: OpenEnv environment manifest.
- docs:
    - SETUP.md
    - ARCHITECTURE.md
    - RL_BASICS.md
    - OPENENV_GUIDE.md
    - TASKS.md
    - REWARD_DESIGN.md
    - SUBMISSION_READINESS.md
    - JUDGING_CRITERIA_MAPPING.md
    - VALIDATION_RUNBOOK.md
    - INFERENCE_PROTOCOL.md
    - RISK_AND_LIMITATIONS.md

## Beginner-Friendly File Walkthrough

- models.py
    - Contains all data contracts used across API, environment, grader, and baseline.
    - Why: Pydantic models make interfaces explicit and easy to validate.
- seo_engine.py
    - Scores HTML by SEO signals (title, meta, headings, alt text, keyword usage, semantic tags).
    - Why: deterministic scoring is critical for reproducible RL training.
- server/environment.py
    - Core RL loop: reset, step, state tracking, task difficulty handling, reward calculation.
    - Why: this is where agent learning signal is generated.
- grader.py
    - Converts raw SEO score into final normalized score (0.0-1.0).
    - Why: hackathon judges need a deterministic, standard output.
- server/app.py
    - Exposes OpenEnv endpoints and custom utility endpoints.
    - Why: allows both agent training and practical evaluation workflows.
- baseline.py
    - Runs a reproducible baseline policy for all tasks.
    - Why: establishes a benchmark and shows your environment is learnable.

## How It Works

1. Start with poor HTML for a chosen task.
2. Evaluate SEO score with BeautifulSoup checks.
3. Agent selects one action from a constrained action space.
4. Environment applies deterministic HTML transformation.
5. Environment computes dense reward from score delta and penalties.
6. Episode ends when target score is met or max steps reached.

## API Endpoints

- POST /reset: OpenEnv reset endpoint.
- POST /step: OpenEnv step endpoint.
- GET /state: OpenEnv state endpoint.
- GET /tasks: Returns easy/medium/hard task specs.
- POST /grader: Deterministic final score in 0.0-1.0.
- GET /baseline: Runs deterministic baseline across all tasks.
- POST /task/reset: Convenience endpoint to reset singleton by task id.
- GET /task/state: Full singleton state snapshot.

## NVIDIA Model Configuration

This project uses `nvidia/nemotron-3-super-120b-a12b` for LLM-based baseline actions when credentials are present.

1. Copy `.env.example` to `.env`.
2. Set `NVIDIA_API_KEY`.
3. Optionally set `NVIDIA_BASE_URL`, `NVIDIA_MODEL`, and `USE_LLM_BASELINE`.

If `NVIDIA_API_KEY` is missing (or `USE_LLM_BASELINE=0`), baseline runs the deterministic heuristic policy.

## Judge Preparation: Possible Questions + Strong Answers

Q: Why use RL here instead of rule-based scripts?
A: SEO optimization is sequential and stateful. One action can change future opportunities, so RL is a natural fit for learning action ordering and strategy under step budgets.

Q: How does the reward function help learning?
A: It is dense. The agent receives immediate feedback from score deltas, plus penalties for invalid or useless actions, and an efficiency bonus for early completion. This reduces sparse-reward training failure.

Q: Why is this better than static SEO tools?
A: Static tools diagnose. This environment supports closed-loop optimization, where an agent can act, evaluate impact, and improve iteratively.

Q: How can this scale to real-world usage?
A: The same interface can run against larger HTML corpora, CMS page templates, and organization-specific SEO policies. New actions and scoring components can be added without breaking API contracts.

## Troubleshooting (Windows)

- If `/usr/bin/env` fails in PowerShell, run `prevalidationScript.ps1` instead of the bash script.
- If Docker API connection fails, start Docker Desktop first, then rerun `docker build`.
