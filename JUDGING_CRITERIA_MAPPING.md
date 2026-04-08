# Judging Criteria Mapping

## Real-World Utility (30%)

- Domain: SEO optimization for HTML pages (real production task).
- Why useful: converts static SEO analysis into sequential optimization suitable for agent learning.
- Evidence: server/environment.py, seo_engine.py.

## Task & Grader Quality (25%)

- Three tasks: easy, medium, hard.
- Deterministic grader in range [0.0, 1.0].
- Progressive difficulty and target thresholds (70/85/95).
- Evidence: server/environment.py, grader.py, TASKS.md.

## Environment Design (20%)

- Clean `reset()`, `step()`, `state` implementation.
- Meaningful action space and observation space.
- Dense rewards from score delta + penalties.
- Evidence: models.py, server/environment.py, REWARD_DESIGN.md.

## Code Quality & Spec Compliance (15%)

- Typed Pydantic contracts for action/observation/reward/state.
- OpenEnv manifest and FastAPI app wiring.
- Dockerfile included.
- Evidence: models.py, openenv.yaml, server/app.py, server/Dockerfile.

## Creativity & Novelty (10%)

- RL framing for SEO optimization instead of static linting.
- Deterministic graders with practical transformations.
- Evidence: README.md, ARCHITECTURE.md.
