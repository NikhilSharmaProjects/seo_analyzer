"""OpenEnv-compatible SEO optimization environment."""

from __future__ import annotations

from uuid import uuid4

from bs4 import BeautifulSoup
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import SeoAction, SeoObservation, SeoReward, SeoStateModel, TaskLevel, TaskSpec
    from ..seo_engine import evaluate_seo_html
except ImportError:  # pragma: no cover
    from models import SeoAction, SeoObservation, SeoReward, SeoStateModel, TaskLevel, TaskSpec
    from seo_engine import evaluate_seo_html


class SeoOptimizationEnvironment(Environment):
    """RL environment where each action incrementally improves HTML SEO quality."""

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self.tasks = self._build_tasks()
        self.current_task = self.tasks["easy"]
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._done = False
        self._current_html = self.current_task.initial_html
        self._previous_actions: list[str] = []
        self._last_score = 0.0

    @staticmethod
    def _build_tasks() -> dict[str, TaskSpec]:
        easy_html = """
        <html><body>
        <div>Buy our lightweight running shoes now.</div>
        <img src='shoe.jpg'>
        </body></html>
        """
        medium_html = """
        <html><body>
        <h3>Running Store</h3>
        <p>We sell shoes and shoes and shoes.</p>
        <img src='shoe1.jpg'>
        <img src='shoe2.jpg' alt=''>
        </body></html>
        """
        hard_html = """
        <html><body>
        <div><b>Best Running Shoes</b></div>
        <h1>Shoes</h1><h1>More Shoes</h1>
        <p>shoes shoes shoes shoes shoes shoes shoes shoes</p>
        <img src='hero.jpg'>
        </body></html>
        """

        return {
            "easy": TaskSpec(
                id="easy",
                level=TaskLevel.EASY,
                objective="Fix basic SEO issues (title and meta description) to reach at least 70.",
                target_score=70.0,
                keyword="running shoes",
                max_steps=8,
                initial_html=easy_html,
            ),
            "medium": TaskSpec(
                id="medium",
                level=TaskLevel.MEDIUM,
                objective="Improve headings, alt text, and keyword usage to reach at least 85.",
                target_score=85.0,
                keyword="running shoes",
                max_steps=10,
                initial_html=medium_html,
            ),
            "hard": TaskSpec(
                id="hard",
                level=TaskLevel.HARD,
                objective="Fully optimize semantic structure and advanced SEO signals to reach at least 95.",
                target_score=95.0,
                keyword="running shoes",
                max_steps=12,
                initial_html=hard_html,
            ),
        }

    def set_task(self, task_id: str) -> None:
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task_id '{task_id}'. Expected one of: {list(self.tasks.keys())}")
        self.current_task = self.tasks[task_id]

    def reset(self) -> SeoObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._done = False
        self._current_html = self.current_task.initial_html
        self._previous_actions = []
        scoring = evaluate_seo_html(self._current_html, self.current_task.keyword)
        self._last_score = scoring.total_score

        return SeoObservation(
            current_html=self._current_html,
            seo_score=scoring.total_score,
            detected_issues=scoring.issues,
            previous_actions=[],
            task_id=self.current_task.id,
            task_level=self.current_task.level,
            target_score=self.current_task.target_score,
            reward=0.0,
            done=False,
            reward_details=SeoReward(total=0.0, delta_score=0.0),
        )

    def _apply_action(self, action: SeoAction) -> tuple[str, bool]:
        soup = BeautifulSoup(self._current_html, "html.parser")
        keyword = action.keyword or self.current_task.keyword
        changed = False

        if action.action_type == "add_meta_tag":
            head = soup.find("head")
            if head is None:
                html_tag = soup.find("html")
                if html_tag is None:
                    html_tag = soup.new_tag("html")
                    body = soup.find("body")
                    if body:
                        body.extract()
                    html_tag.append(body or soup.new_tag("body"))
                    soup.append(html_tag)
                head = soup.new_tag("head")
                html_tag.insert(0, head)
                changed = True

            meta = soup.find("meta", attrs={"name": "description"})
            if meta is None:
                meta = soup.new_tag("meta")
                meta["name"] = "description"
                meta["content"] = f"Learn about {keyword} and choose the best product for your goals."
                head.append(meta)
                changed = True
            elif not (meta.get("content") or "").strip():
                meta["content"] = f"Learn about {keyword} and choose the best product for your goals."
                changed = True

        elif action.action_type == "fix_title":
            head = soup.find("head")
            if head is None:
                html_tag = soup.find("html")
                if html_tag is None:
                    html_tag = soup.new_tag("html")
                    body = soup.find("body")
                    if body:
                        body.extract()
                    html_tag.append(body or soup.new_tag("body"))
                    soup.append(html_tag)
                head = soup.new_tag("head")
                html_tag.insert(0, head)
                changed = True

            title = soup.find("title")
            value = f"Best {keyword.title()} Guide"
            if title is None:
                title = soup.new_tag("title")
                title.string = value
                head.append(title)
                changed = True
            elif title.get_text(strip=True) != value:
                title.string = value
                changed = True

        elif action.action_type == "optimize_headings":
            body = soup.find("body")
            if body is None:
                body = soup.new_tag("body")
                soup.append(body)
                changed = True

            h1s = soup.find_all("h1")
            if not h1s:
                new_h1 = soup.new_tag("h1")
                new_h1.string = f"{keyword.title()} for Everyday Athletes"
                body.insert(0, new_h1)
                changed = True
            elif len(h1s) > 1:
                for extra in h1s[1:]:
                    extra.name = "h2"
                    changed = True

            if not soup.find("h2"):
                new_h2 = soup.new_tag("h2")
                new_h2.string = "How to choose the right fit"
                h1 = soup.find("h1")
                if h1:
                    h1.insert_after(new_h2)
                else:
                    body.insert(1, new_h2)
                changed = True

        elif action.action_type == "add_alt_text":
            images = soup.find_all("img")
            for i, img in enumerate(images, start=1):
                alt = (img.get("alt") or "").strip()
                if not alt:
                    img["alt"] = f"{keyword} image {i}"
                    changed = True

        elif action.action_type == "improve_keywords":
            body = soup.find("body")
            if body is None:
                body = soup.new_tag("body")
                soup.append(body)
                changed = True

            text_blob = " ".join(soup.stripped_strings).lower()
            if keyword.lower() not in text_blob:
                p = soup.new_tag("p")
                p.string = f"This article explains how {keyword} improve performance and comfort."
                body.append(p)
                changed = True

            title = soup.find("title")
            if title and keyword.lower() not in title.get_text(strip=True).lower():
                title.string = f"{title.get_text(strip=True)} | {keyword.title()}"
                changed = True

        elif action.action_type == "remove_bad_structure":
            for tag_name in ["b", "i"]:
                for tag in soup.find_all(tag_name):
                    tag.name = "strong" if tag_name == "b" else "em"
                    changed = True

            scripts = soup.find_all("script")
            for script in scripts:
                script.decompose()
                changed = True

            empty_divs = [d for d in soup.find_all("div") if not d.get_text(strip=True)]
            for div in empty_divs:
                div.decompose()
                changed = True

            # Keep only one h1 when duplicates exist.
            h1s = soup.find_all("h1")
            for duplicate in h1s[1:]:
                duplicate.name = "h2"
                changed = True

        return str(soup), changed

    def _compute_reward(
        self,
        old_score: float,
        new_score: float,
        action_changed_html: bool,
        is_valid_html: bool,
        repeated: bool,
        reached_goal: bool,
    ) -> SeoReward:
        delta_norm = round((new_score - old_score) / 100.0, 4)
        # Core dense reward is directly tied to SEO score improvement.
        improvement_bonus = delta_norm

        invalid_html_penalty = -0.25 if not is_valid_html else 0.0
        useless_action_penalty = -0.15 if not action_changed_html else 0.0
        repeated_action_penalty = -0.05 if repeated else 0.0

        remaining_steps = self.current_task.max_steps - self._state.step_count
        efficiency_bonus = 0.0
        if reached_goal:
            efficiency_bonus = round(max(0.0, remaining_steps / self.current_task.max_steps) * 0.2, 4)

        total = round(
            improvement_bonus
            + efficiency_bonus
            + invalid_html_penalty
            + useless_action_penalty
            + repeated_action_penalty,
            4,
        )

        return SeoReward(
            total=total,
            delta_score=delta_norm,
            improvement_bonus=improvement_bonus,
            efficiency_bonus=efficiency_bonus,
            invalid_html_penalty=invalid_html_penalty,
            useless_action_penalty=useless_action_penalty,
            repeated_action_penalty=repeated_action_penalty,
        )

    def step(self, action: SeoAction) -> SeoObservation:  # type: ignore[override]
        if self._done:
            return self._build_observation(reward_details=SeoReward(total=0.0, delta_score=0.0), reward=0.0)

        self._state.step_count += 1
        repeated = action.action_type in self._previous_actions

        new_html, changed = self._apply_action(action)
        old_score = self._last_score

        self._current_html = new_html
        scoring = evaluate_seo_html(self._current_html, action.keyword or self.current_task.keyword)
        self._last_score = scoring.total_score

        reached_target = scoring.total_score >= self.current_task.target_score
        exhausted_steps = self._state.step_count >= self.current_task.max_steps
        self._done = reached_target or exhausted_steps

        reward_details = self._compute_reward(
            old_score=old_score,
            new_score=scoring.total_score,
            action_changed_html=changed,
            is_valid_html=scoring.is_valid_html,
            repeated=repeated,
            reached_goal=reached_target,
        )

        self._previous_actions.append(action.action_type)

        print(
            "[DEBUG step] "
            f"task={self.current_task.id} "
            f"step={self._state.step_count} "
            f"action={action.action_type} "
            f"old_score={old_score:.2f} "
            f"new_score={scoring.total_score:.2f} "
            f"reward={reward_details.total:.4f}"
        )

        return self._build_observation(
            scoring_total=scoring.total_score,
            issues=scoring.issues,
            done=self._done,
            reward=reward_details.total,
            reward_details=reward_details,
        )

    def _build_observation(
        self,
        scoring_total: float | None = None,
        issues: list[str] | None = None,
        done: bool | None = None,
        reward: float = 0.0,
        reward_details: SeoReward | None = None,
    ) -> SeoObservation:
        current_score = self._last_score if scoring_total is None else scoring_total
        current_issues = [] if issues is None else issues

        return SeoObservation(
            current_html=self._current_html,
            seo_score=current_score,
            detected_issues=current_issues,
            previous_actions=list(self._previous_actions),
            task_id=self.current_task.id,
            task_level=self.current_task.level,
            target_score=self.current_task.target_score,
            done=self._done if done is None else done,
            reward=reward,
            reward_details=reward_details,
            metadata={
                "step_count": self._state.step_count,
                "max_steps": self.current_task.max_steps,
                "objective": self.current_task.objective,
            },
        )

    def get_state_model(self) -> SeoStateModel:
        scoring = evaluate_seo_html(self._current_html, self.current_task.keyword)
        return SeoStateModel(
            episode_id=self._state.episode_id,
            step_count=self._state.step_count,
            max_steps=self.current_task.max_steps,
            done=self._done,
            task_id=self.current_task.id,
            task_level=self.current_task.level,
            objective=self.current_task.objective,
            keyword=self.current_task.keyword,
            target_score=self.current_task.target_score,
            current_html=self._current_html,
            seo_score=scoring.total_score,
            detected_issues=scoring.issues,
            previous_actions=list(self._previous_actions),
        )

    @property
    def state(self) -> State:
        return self._state
