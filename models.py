# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Pydantic models used by the SEO optimization environment."""

from enum import Enum
from typing import Dict, List, Literal, Optional

from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field


ActionType = Literal[
    "add_meta_tag",
    "fix_title",
    "optimize_headings",
    "add_alt_text",
    "improve_keywords",
    "remove_bad_structure",
]


class TaskLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SeoAction(Action):
    """Single environment action executed at each RL step."""

    action_type: ActionType = Field(..., description="The SEO operation to apply")
    keyword: Optional[str] = Field(
        default=None,
        description="Optional keyword override. If omitted, task keyword is used.",
    )


class SeoReward(BaseModel):
    """Detailed reward object for dense-reward training and debugging."""

    total: float = Field(..., description="Final scalar reward returned by environment")
    delta_score: float = Field(..., description="Change in normalized SEO score (0-1)")
    improvement_bonus: float = Field(default=0.0)
    efficiency_bonus: float = Field(default=0.0)
    invalid_html_penalty: float = Field(default=0.0)
    useless_action_penalty: float = Field(default=0.0)
    repeated_action_penalty: float = Field(default=0.0)


class SeoObservation(Observation):
    """Observation returned after reset and step calls."""

    current_html: str = Field(..., description="Current HTML after latest action")
    seo_score: float = Field(..., ge=0.0, le=100.0, description="SEO score in range 0-100")
    detected_issues: List[str] = Field(default_factory=list)
    previous_actions: List[str] = Field(default_factory=list)
    task_id: str = Field(...)
    task_level: TaskLevel = Field(...)
    target_score: float = Field(..., ge=0.0, le=100.0)
    reward_details: Optional[SeoReward] = Field(default=None)


class SeoStateModel(BaseModel):
    """Complete state snapshot used by the custom /state endpoint."""

    episode_id: str
    step_count: int
    max_steps: int
    done: bool
    task_id: str
    task_level: TaskLevel
    objective: str
    keyword: str
    target_score: float
    current_html: str
    seo_score: float
    detected_issues: List[str]
    previous_actions: List[str]


class TaskSpec(BaseModel):
    """Task definition for each difficulty level."""

    id: str
    level: TaskLevel
    objective: str
    target_score: float = Field(..., ge=0.0, le=100.0)
    keyword: str
    max_steps: int
    initial_html: str


class SeoScoreBreakdown(BaseModel):
    """Detailed SEO score internals for analysis and grading."""

    total_score: float = Field(..., ge=0.0, le=100.0)
    normalized_score: float = Field(..., ge=0.0, le=1.0)
    component_scores: Dict[str, float] = Field(default_factory=dict)
    issues: List[str] = Field(default_factory=list)
    is_valid_html: bool = Field(default=True)


class GraderRequest(BaseModel):
    task_id: str = Field(..., description="easy, medium, or hard")
    html: str = Field(..., description="Final candidate HTML to grade")


class GraderResult(BaseModel):
    task_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    score_100: float = Field(..., ge=0.0, le=100.0)
    passed: bool
    issues: List[str] = Field(default_factory=list)


class BaselineTaskResult(BaseModel):
    task_id: str
    final_score: float = Field(..., ge=0.0, le=1.0)
    steps_used: int
    passed: bool
    action_history: List[str] = Field(default_factory=list)


class BaselineResult(BaseModel):
    seed: int
    policy: str
    tasks: List[BaselineTaskResult]
