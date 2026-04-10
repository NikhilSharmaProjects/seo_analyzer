"""Hackathon submission inference script for the SEO OpenEnv environment.

LLM env vars (optional; script falls back to deterministic heuristic policy if missing):
- API_BASE_URL: LLM API endpoint
- MODEL_NAME: LLM model identifier
- HF_TOKEN: API token for LLM endpoint
- LOCAL_IMAGE_NAME: optional, expected by checklist (not used directly here)

Optional env vars:
- ENV_BASE_URL: environment server URL (default: http://127.0.0.1:8000)
- MAX_STEPS: max episode steps (default: 12)
"""

from __future__ import annotations

import os
from typing import Optional

import requests
from openai import OpenAI

TASKS = ["easy", "medium", "hard"]
BENCHMARK = "seo_analyzer"
ALLOWED_ACTIONS = {
    "add_meta_tag",
    "fix_title",
    "optimize_headings",
    "add_alt_text",
    "improve_keywords",
    "remove_bad_structure",
}


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={str(done).lower()} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def _heuristic_action(issues: list[str]) -> str:
    issue_text = " ".join(issues).lower()
    if "meta description" in issue_text:
        return "add_meta_tag"
    if "title" in issue_text:
        return "fix_title"
    if "h1" in issue_text or "h2" in issue_text or "heading" in issue_text:
        return "optimize_headings"
    if "alt text" in issue_text or "images" in issue_text:
        return "add_alt_text"
    if "keyword" in issue_text:
        return "improve_keywords"
    if "invalid" in issue_text or "structure" in issue_text:
        return "remove_bad_structure"
    return "improve_keywords"


def _llm_action(
    client: Optional[OpenAI], model_name: str, task: str, issues: list[str], score: float
) -> tuple[str, Optional[str]]:
    if client is None:
        return _heuristic_action(issues), None

    prompt = (
        "You are controlling an SEO optimization environment. "
        "Return exactly one action from this list and nothing else: "
        "add_meta_tag, fix_title, optimize_headings, add_alt_text, improve_keywords, remove_bad_structure. "
        f"Task={task}, current_score={score:.2f}, issues={issues}."
    )

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Return only one allowed action token."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=16,
            stream=False,
        )
        action = (completion.choices[0].message.content or "").strip()
        if action in ALLOWED_ACTIONS:
            return action, None
        return _heuristic_action(issues), "invalid_model_action"
    except Exception as exc:  # pragma: no cover
        return _heuristic_action(issues), str(exc)


def _post_json(base_url: str, path: str, payload: dict) -> dict:
    response = requests.post(f"{base_url}{path}", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def _score_from_observation(obs: dict) -> float:
    return round(float(obs.get("seo_score", 0.0)) / 100.0, 4)


def run_task(
    client: Optional[OpenAI], model_name: str, base_url: str, task: str, max_steps: int
) -> None:
    log_start(task=task, env=BENCHMARK, model=model_name)

    rewards: list[float] = []
    steps = 0
    success = False
    score_01 = 0.0
    done = False
    issues: list[str] = []

    try:
        reset_obs = _post_json(base_url, f"/task/reset?task_id={task}", {})
        issues = reset_obs.get("detected_issues", [])
        done = bool(reset_obs.get("done", False))
        score_01 = _score_from_observation(reset_obs)

        while (not done) and steps < max_steps:
            action, action_error = _llm_action(client, model_name, task, issues, score_01 * 100.0)
            try:
                step_obs = _post_json(base_url, "/task/step", {"action_type": action})
            except Exception as exc:
                steps += 1
                rewards.append(0.0)
                log_step(step=steps, action=action, reward=0.0, done=True, error=str(exc))
                done = True
                break

            reward = float(step_obs.get("reward") or 0.0)
            done = bool(step_obs.get("done", False))
            issues = step_obs.get("detected_issues", [])
            score_01 = _score_from_observation(step_obs)

            steps += 1
            rewards.append(reward)
            log_step(step=steps, action=action, reward=reward, done=done, error=action_error)

        success = (
            score_01 >= 0.70 if task == "easy" else score_01 >= 0.85 if task == "medium" else score_01 >= 0.95
        )
    except Exception:
        # Fail closed for this task without crashing the entire script.
        pass
    finally:
        log_end(success=success, steps=steps, score=score_01, rewards=rewards)


def main() -> None:
    api_base_url = os.getenv("API_BASE_URL")
    # Primary validator path: API_KEY + API_BASE_URL (LiteLLM proxy).
    # Backward compatibility: fall back to HF_TOKEN if API_KEY is absent.
    api_key = os.getenv("API_KEY") or os.getenv("HF_TOKEN")
    model_name = os.getenv("MODEL_NAME") or os.getenv("OPENAI_MODEL")
    _ = os.getenv("LOCAL_IMAGE_NAME")  # present for checklist compatibility

    env_base_url = os.getenv("ENV_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        max_steps = int(os.getenv("MAX_STEPS", "12"))
    except ValueError:
        max_steps = 12

    use_llm = bool(api_base_url and api_key)
    model_label = model_name if use_llm and model_name else "deterministic-heuristic"

    client: Optional[OpenAI] = None
    if use_llm:
        try:
            client = OpenAI(base_url=api_base_url, api_key=api_key)
        except Exception:
            client = None
            model_label = "deterministic-heuristic"

    for task in TASKS:
        run_task(client=client, model_name=model_label, base_url=env_base_url, task=task, max_steps=max_steps)


if __name__ == "__main__":
    main()
