"""Mandatory proof test: run real actions and show HTML/score improvements."""

from __future__ import annotations

from models import SeoAction
from server.environment import SeoOptimizationEnvironment


def run_test_case() -> None:
    env = SeoOptimizationEnvironment()
    env.set_task("easy")

    obs = env.reset()
    print("=== BEFORE HTML ===")
    print(obs.current_html)
    print(f"Initial score: {obs.seo_score:.2f}")
    print("Initial issues:")
    for issue in obs.detected_issues:
        print(f"- {issue}")

    actions = [
        "fix_title",
        "add_meta_tag",
        "optimize_headings",
        "add_alt_text",
        "improve_keywords",
    ]

    start_score = obs.seo_score
    for action_name in actions:
        obs = env.step(SeoAction(action_type=action_name))

    print("\n=== AFTER HTML ===")
    print(obs.current_html)
    print(f"Final score: {obs.seo_score:.2f}")
    print(f"Score improvement: {obs.seo_score - start_score:.2f}")
    print("Final issues:")
    for issue in obs.detected_issues:
        print(f"- {issue}")


if __name__ == "__main__":
    run_test_case()
