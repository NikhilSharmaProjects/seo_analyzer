"""Deterministic grading utilities for the SEO optimization tasks."""

from __future__ import annotations

try:
    from .models import GraderResult, TaskSpec
    from .seo_engine import evaluate_seo_html
except ImportError:  # pragma: no cover
    from models import GraderResult, TaskSpec
    from seo_engine import evaluate_seo_html


def grade_html_for_task(task: TaskSpec, html: str) -> GraderResult:
    """Grade HTML for a specific task and return a deterministic 0-1 score."""
    breakdown = evaluate_seo_html(html, task.keyword)
    score_01 = round(breakdown.total_score / 100.0, 4)
    return GraderResult(
        task_id=task.id,
        score=score_01,
        score_100=breakdown.total_score,
        passed=breakdown.total_score >= task.target_score,
        issues=breakdown.issues,
    )
