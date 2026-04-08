# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""FastAPI app for the SEO optimization OpenEnv environment."""

from __future__ import annotations

from fastapi import HTTPException

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e
try:
    from ..baseline import run_baseline
    from ..grader import grade_html_for_task
    from ..models import GraderRequest, SeoAction, SeoObservation
    from .environment import SeoOptimizationEnvironment
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    from baseline import run_baseline
    from grader import grade_html_for_task
    from models import GraderRequest, SeoAction, SeoObservation
    from server.environment import SeoOptimizationEnvironment


# OpenEnv-compatible routes: /reset /step /state /schema /ws
app = create_app(
    SeoOptimizationEnvironment,
    SeoAction,
    SeoObservation,
    env_name="seo_analyzer",
    max_concurrent_envs=2,
)

# Auxiliary singleton for deterministic non-websocket endpoints.
_rest_env = SeoOptimizationEnvironment()


@app.post("/task/reset")
def reset_task(task_id: str = "easy"):
    """Reset a selected task using a deterministic singleton environment."""
    try:
        _rest_env.set_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _rest_env.reset().model_dump()


@app.post("/task/step")
def step_task(action: SeoAction):
    """Execute one step on the deterministic singleton environment."""
    return _rest_env.step(action).model_dump()


@app.get("/task/state")
def get_task_state():
    """Return full task state snapshot for the deterministic singleton environment."""
    return _rest_env.get_state_model().model_dump()


@app.get("/tasks")
def list_tasks():
    """List all task definitions and objectives."""
    return [task.model_dump() for task in _rest_env.tasks.values()]


@app.post("/grader")
def grader(payload: GraderRequest):
    """Deterministic grader endpoint returning score in range 0-1."""
    task = _rest_env.tasks.get(payload.task_id)
    if task is None:
        raise HTTPException(status_code=400, detail="Unknown task_id")
    return grade_html_for_task(task, payload.html).model_dump()


@app.get("/baseline")
def baseline():
    """Run reproducible baseline across easy/medium/hard tasks."""
    baseline_env = SeoOptimizationEnvironment()
    return run_baseline(baseline_env).model_dump()


def main(host: str = "0.0.0.0", port: int = 8000):
    """
    Entry point for direct execution via uv run or python -m.

    This function enables running the server without Docker:
        uv run --project . server
        uv run --project . server --port 8001
        python -m seo_analyzer.server.app

    Args:
        host: Host address to bind to (default: "0.0.0.0")
        port: Port number to listen on (default: 8000)

    For production deployments, consider using uvicorn directly with
    multiple workers:
        uvicorn seo_analyzer.server.app:app --workers 4
    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)
