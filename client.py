# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""SEO Analyzer OpenEnv client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import SeoAction, SeoObservation, SeoReward, SeoStateModel, TaskLevel


class SeoAnalyzerEnv(EnvClient[SeoAction, SeoObservation, State]):
    """
    Client for the Seo Analyzer Environment.

    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions with lower latency.
    Each client instance has its own dedicated environment session on the server.

    Example:
        >>> with SeoAnalyzerEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset()
        ...     result = client.step(SeoAction(action_type="fix_title"))
        ...     print(result.observation.seo_score)
    """

    def _step_payload(self, action: SeoAction) -> Dict:
        """
        Convert SeoAction to JSON payload for step message.

        Args:
            action: SeoAction instance

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "action_type": action.action_type,
            "keyword": action.keyword,
        }

    def _parse_result(self, payload: Dict) -> StepResult[SeoObservation]:
        """
        Parse server response into StepResult[SeoObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with SeoObservation
        """
        obs_data = payload.get("observation", {})
        reward_data = obs_data.get("reward_details")
        reward_details = SeoReward(**reward_data) if reward_data else None

        observation = SeoObservation(
            current_html=obs_data.get("current_html", ""),
            seo_score=obs_data.get("seo_score", 0.0),
            detected_issues=obs_data.get("detected_issues", []),
            previous_actions=obs_data.get("previous_actions", []),
            task_id=obs_data.get("task_id", "easy"),
            task_level=TaskLevel(obs_data.get("task_level", "easy")),
            target_score=obs_data.get("target_score", 70.0),
            reward_details=reward_details,
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """
        Parse server response into State object.

        Args:
            payload: JSON response from state request

        Returns:
            State object with episode_id and step_count
        """
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )

    @staticmethod
    def parse_full_state(payload: Dict) -> SeoStateModel:
        """Parse custom /state response into rich state model."""
        return SeoStateModel(**payload)
