# Architecture

## Components

- FastAPI layer (server/app.py)
    - Serves OpenEnv-compatible endpoints and extra endpoints for tasks, grader, baseline.
- Environment core (server/environment.py)
    - Holds state, applies actions, computes rewards, ends episodes.
- SEO engine (seo_engine.py)
    - Deterministic score and issue detection using BeautifulSoup.
- Grader (grader.py)
    - Deterministic normalized score (0.0-1.0) for final evaluation.
- Baseline (baseline.py)
    - Reproducible policy to benchmark across easy/medium/hard.

## RL Loop

1. reset() initializes task HTML and score.
2. Agent receives observation:
    - current_html
    - seo_score
    - detected_issues
    - previous_actions
3. Agent picks one valid action.
4. step(action) mutates HTML.
5. Environment re-scores HTML and computes dense reward.
6. Episode terminates on target score or max steps.

## Determinism

- No randomness in task content, scoring, or baseline policy.
- Grader uses same deterministic scoring pipeline.
- Scores are reproducible for identical inputs.
