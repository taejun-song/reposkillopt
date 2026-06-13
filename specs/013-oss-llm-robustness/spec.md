# Feature Specification: Open-Source / Local LLM Robustness

**Feature Branch**: `013-oss-llm-robustness`
**Created**: 2026-06-13
**Status**: Draft
**Input**: Make RepoSkillOpt work reliably with open-source / local LLMs (Qwen, Llama, Mistral, DeepSeek via Ollama / vLLM / llama.cpp / LM Studio). The transport already exists (`openai` provider + `base_url`); harden the **output handling** (chat models wrap the spec in code fences or add preamble/postamble) and **prove the deterministic guarantees hold for weaker models**. Built TDD (tests first).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a spec with a local open-source model (Priority: P1)

An engineer points the engine at a local Ollama/vLLM server running an open-source model and generates a Repository Specification. Even though the model wraps its answer in a ```` ```markdown ```` fence or adds "Here is the specification:", the produced spec is parsed correctly — sections detected, citations grounded, completeness guaranteed.

**Independent Test**: Feed fence-wrapped and preamble-wrapped model output through the generation path; assert the stored spec has its sections detected and grounded identically to clean output.

**Acceptance Scenarios**:
1. **Given** model output wrapped in a single outer ```` ```markdown … ``` ```` (or ``` ~~~ ```) fence, **When** the spec is produced, **Then** the outer fence is stripped and section detection / grounding work (inner ```` ```mermaid ```` diagram fences are preserved).
2. **Given** model output with chat preamble/postamble ("Sure! Here is …" / "Let me know if …"), **When** the spec is produced, **Then** the chatter before the first heading/front-matter and after the last section is trimmed.
3. **Given** a `--rollout-provider ollama:<model>`, **When** a provider is made, **Then** it targets a local OpenAI-compatible endpoint (default `http://localhost:11434/v1`) with a dummy key, no real key required.

### User Story 2 - Guarantees hold for weaker models (Priority: P1)

A smaller open-source model produces a thinner spec (fewer cited claims, some sections sparse). The deterministic guarantees still hold: 100% symbol coverage (completeness step), all sections detectable (tolerant detector), and fabricated citations are caught by grounding.

**Independent Test**: Run a "weak model" fixture spec through completeness + grounding + structure; assert coverage 100%, sections detected, fabricated citation flagged.

**Acceptance Scenarios**:
1. **Given** a weak-model spec missing the *Symbols not yet analyzed* listing, **When** the completeness step runs, **Then** symbol coverage is 100% (model quality cannot break the guarantee).
2. **Given** a weak-model spec with a fabricated `file:line`, **When** grounded, **Then** that citation is reported unresolved (no silent pass).

## Requirements *(mandatory)*

- **FR-001**: Provide `sanitize_model_spec(text) -> str` — deterministic, model-free: strip a single outer code fence (```` ``` ````/`~~~`, optionally tagged `markdown`/`md`) that wraps the *entire* response, and trim chat preamble before the first `#`/`---` and postamble after the last section. MUST preserve inner fenced blocks (e.g. ```` ```mermaid ````).
- **FR-002**: Apply `sanitize_model_spec` to model output in the spec-generation paths (`judge.generate_spec`, `judge.generate_section`) so every provider's spec is normalized before grounding/completeness/scoring.
- **FR-003**: `make_provider("ollama:<model>")` returns an OpenAI-compatible provider defaulting `base_url` to `http://localhost:11434/v1` with a dummy key; existing `openai:<model>` behavior unchanged.
- **FR-004**: The OpenAI-compatible provider MUST fail gracefully on malformed/empty OSS responses (missing `choices`, error body) with a clear `ProviderError`, never a raw `KeyError`.
- **FR-005**: Sanitization MUST be idempotent and MUST NOT alter already-clean specs (no outer fence, no chatter ⇒ byte-identical).
- **FR-006**: No change to grounding, rubric, reward, or metric definitions; the deterministic guarantees (completeness, grounding, tolerant section detection) are the model-robustness layer and are exercised by tests for weak-model output.
- **FR-007**: Built test-first (TDD): the sanitization and ollama-alias tests are written and red before implementation, then green.

### Key Entities

- **sanitize_model_spec**: pure text normalizer for chat-model output quirks.

## Success Criteria *(mandatory)*

- **SC-001**: Fence-wrapped and preamble-wrapped model output yield the same detected-section count and grounding result as the equivalent clean spec.
- **SC-002**: A weak-model spec still reaches 100% symbol coverage after completeness, and a fabricated citation is flagged unresolved.
- **SC-003**: `make_provider("ollama:qwen2.5-coder")` produces a provider pointing at `http://localhost:11434/v1`, no real API key.
- **SC-004**: `sanitize_model_spec` is idempotent and a no-op on clean specs; full engine suite stays green (frozen metrics unchanged).

## Assumptions

- "Open-source models" are served behind an OpenAI-compatible HTTP API (Ollama shim, vLLM, llama.cpp server, LM Studio) — the established air-gap posture. Native non-OpenAI APIs are out of scope (use the shim).
- Model *quality* varies; the deterministic engine guarantees coverage/grounding regardless — this feature hardens parsing + proves the guarantees, it does not fine-tune or grade models.
