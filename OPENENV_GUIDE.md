# OpenEnv Guide

OpenEnv standardizes environment APIs so training/evaluation agents can interact with environments consistently.

## Required Methods

- reset(): Start a new episode and return initial observation.
- step(action): Apply one action and return next observation with reward.
- state: Return low-level OpenEnv state (episode_id, step_count).

## Pydantic Contracts Used

- Action: SeoAction
- Observation: SeoObservation
- State model: SeoStateModel (for rich custom endpoint)
- Reward model: SeoReward

## Manifest

openenv.yaml defines environment metadata and app entrypoint.

## Endpoints

OpenEnv app provides reset/step/state and schema/websocket support. This project also adds tasks/grader/baseline endpoints for hackathon evaluation workflows.
