# Inference Protocol

## Required Environment Variables

- `API_BASE_URL`: LLM endpoint.
- `MODEL_NAME`: model to call.
- `HF_TOKEN`: token used by OpenAI client.
- `LOCAL_IMAGE_NAME`: required by checklist (accepted by script environment contract).

Optional:

- `ENV_BASE_URL` (default: `http://127.0.0.1:8000`)
- `MAX_STEPS` (default: 12)

## Output Contract

The script emits only these line types:

- `[START] task=<task_name> env=<benchmark> model=<model_name>`
- `[STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>`
- `[END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>`

Rules satisfied:

- one START line per task episode
- one STEP line per action
- one END line per task episode
- rewards fixed to 2 decimal places
- booleans in lowercase
- score normalized to [0,1]
