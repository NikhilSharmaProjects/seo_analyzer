"""Deterministic baseline runner for all SEO tasks."""

from __future__ import annotations

import json
import os
from typing import List

try:
    from openai import OpenAI  # Optional, only used when explicitly enabled.
except Exception:  # pragma: no cover
    OpenAI = None

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

try:
    from .models import BaselineResult, BaselineTaskResult, SeoAction
except ImportError:  # pragma: no cover
    from models import BaselineResult, BaselineTaskResult, SeoAction


ALLOWED_ACTIONS = {
    "add_meta_tag",
    "fix_title",
    "optimize_headings",
    "add_alt_text",
    "improve_keywords",
    "remove_bad_structure",
}


def _pick_action_from_issues(issues: List[str]) -> str:
    """Deterministic issue-to-action policy based on real SEO issues."""
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


def _maybe_nvidia_action(issues: List[str]) -> str | None:
    """Optional NVIDIA Nemotron action selection via OpenAI-compatible client."""
    if load_dotenv is not None:
        load_dotenv()

    use_llm = os.getenv("USE_LLM_BASELINE", "0") == "1"
    api_key = os.getenv("OPENAI_API_KEY")
    if not use_llm or OpenAI is None or not api_key:
        return None

    base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    model = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b")

    client = OpenAI(base_url=base_url, api_key=api_key)
    prompt = (
        "Pick one action from this list only: "
        "add_meta_tag, fix_title, optimize_headings, add_alt_text, improve_keywords, remove_bad_structure. "
        f"Issues: {issues}. Return only action name."
    )
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        top_p=0.95,
        messages=[
            {"role": "system", "content": "You are a strict action selector."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=128,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": True},
            "reasoning_budget": 1024,
        },
    )
    action = response.choices[0].message.content.strip()
    return action if action in ALLOWED_ACTIONS else None


def run_baseline(environment, seed: int = 42) -> BaselineResult:
    """Run baseline policy on easy/medium/hard tasks and return reproducible scores."""
    task_ids = ["easy", "medium", "hard"]
    task_results: List[BaselineTaskResult] = []

    for task_id in task_ids:
        environment.set_task(task_id)
        obs = environment.reset()
        history: List[str] = []

        for _ in range(environment.current_task.max_steps):
            action_name = _maybe_nvidia_action(obs.detected_issues) or _pick_action_from_issues(
                obs.detected_issues
            )
            history.append(action_name)
            obs = environment.step(SeoAction(action_type=action_name))
            if obs.done:
                break

        task_results.append(
            BaselineTaskResult(
                task_id=task_id,
                final_score=round(obs.seo_score / 100.0, 4),
                steps_used=len(history),
                passed=obs.seo_score >= environment.current_task.target_score,
                action_history=history,
            )
        )

    use_nvidia = bool(os.getenv("NVIDIA_API_KEY")) and os.getenv("USE_LLM_BASELINE", "0") == "1"
    policy_name = "nvidia-nemotron" if use_nvidia else "deterministic-heuristic"
    return BaselineResult(seed=seed, policy=policy_name, tasks=task_results)


def main() -> None:
    """Run baseline locally and print reproducible JSON output."""
    try:
        from .server.environment import SeoOptimizationEnvironment
    except ImportError:  # pragma: no cover
        from server.environment import SeoOptimizationEnvironment

    env = SeoOptimizationEnvironment()
    result = run_baseline(env)
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
