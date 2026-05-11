# Stretch — Module 25 (Structured Output)

Optional extensions for students who finish early. Not graded.

- **Pydantic models, not JSON Schema files**: accept `--output-model app.models:CodeReview` and use `model_json_schema()` to derive the schema. Closer to how pydantic-deepagents does it (`output_type=PydanticModel`).
- **Streaming structured output**: render partial JSON as the model emits it (OpenAI supports this with `response_format.json_schema`). Useful for long outputs.
- **Two-pass repair**: instead of re-prompting, run a small "fix this JSON to match this schema" call with a cheaper model.
- **Schema discovery**: scan `./schemas/` and pick automatically when the user's prompt names a schema (`"do a code review"` → `code-review.json`).

Pick one or two; don't try to do all of them.
