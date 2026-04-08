# Risks and Limitations

## Operational Risks

- Port conflicts on 8000 can prevent startup.
    - Mitigation: run one server instance at a time.
- Missing env vars for inference can fail execution.
    - Mitigation: define API_BASE_URL, MODEL_NAME, HF_TOKEN before running inference.

## Model-Selection Risk

- LLM may output an invalid action token.
    - Mitigation: script validates action and falls back to deterministic valid action.

## Resource Limits

- Inference runtime depends on model latency.
    - Mitigation: bounded max steps and short action prompts.

## Determinism Scope

- Environment scoring and grading are deterministic.
- LLM-driven action choice may vary unless model/temperature are fixed.
