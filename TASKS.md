# Task Definitions

## Easy (task_id: easy)

- Goal: Fix basic SEO issues.
- Typical missing items: title, meta description.
- Target: score >= 70.
- Max steps: 8.

## Medium (task_id: medium)

- Goal: Improve structure quality.
- Focus: heading hierarchy, alt text, keyword usage.
- Target: score >= 85.
- Max steps: 10.

## Hard (task_id: hard)

- Goal: Full optimization.
- Focus: semantic HTML + advanced structure cleanup.
- Target: score >= 95.
- Max steps: 12.

## Deterministic Grading

The grader always returns the same score for the same HTML and task.

- Output range: 0.0 to 1.0
- Conversion: score_100 / 100
