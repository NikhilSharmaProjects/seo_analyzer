# Reward Design

This environment uses a dense reward to stabilize learning and reduce sparse-feedback problems.

## Formula

Total reward is the sum of:

- Improvement bonus: 2.0 \* (new_score - old_score) / 100
- Efficiency bonus: up to +0.2 when target is reached early
- Invalid HTML penalty: -0.25
- Useless action penalty (no HTML change): -0.15
- Repeated action penalty: -0.05

## Why This Works

- Incremental reward gives immediate learning signal.
- Penalties discourage degenerate behavior.
- Efficiency bonus encourages shorter optimization trajectories.

## Expected Agent Behavior

A good policy should:

1. Prioritize highest-impact issues first.
2. Avoid repeating low-impact actions.
3. Finish in fewer steps to maximize cumulative reward.
