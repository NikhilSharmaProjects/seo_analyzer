# RL Basics (Simple Explanation)

Reinforcement Learning (RL) is learning by trial and feedback.

## Core Terms

- State/Observation: What the agent sees now.
- Action: What the agent does next.
- Reward: Immediate feedback (good or bad).
- Episode: One full attempt from reset to done.
- Policy: The strategy for choosing actions.

## In This Project

- Observation: Current HTML + SEO score + issue list.
- Action: One SEO operation (fix title, add meta, etc.).
- Reward: Positive if SEO score improves, negative for bad behavior.
- Done: True when target score is reached or steps run out.

## Why RL Fits SEO Optimization

SEO fixing is sequential. The order of operations matters. RL learns not only what to do, but also when to do it.
