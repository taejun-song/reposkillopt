# Feature Specification: Keyless `opencode-cli` Provider

**Feature Branch**: `017-opencode-cli-provider`
**Created**: 2026-06-13
**Status**: Draft
**Input**: RepoSkillOpt's engine has a `claude-cli` provider that shells out to `claude -p` so it makes real LLM calls with no API key (borrowing Claude Code's auth/model). Add the OpenCode equivalent: an `opencode-cli` provider that shells out to `opencode run`, so the engine uses OpenCode's configured model — including local/open-source models — with no API key of its own. Built TDD.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the engine keylessly via OpenCode (Priority: P1)

An engineer with OpenCode installed and authenticated (`opencode auth login`) runs `optimize-repo`/`benchmark` with `--rollout-provider opencode-cli` and the engine makes real model calls through OpenCode's configured model — no `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` needed.

**Acceptance Scenarios**:
1. **Given** `--rollout-provider opencode-cli`, **When** a spec is generated, **Then** the engine invokes `opencode run` (non-interactive) and uses the returned text — no API key read.
2. **Given** `opencode-cli:<provider/model>`, **When** built, **Then** that model is passed via `--model`; absent a model, OpenCode's configured default is used.
3. **Given** `opencode` is not installed / the call fails / times out, **When** invoked, **Then** a clear `ProviderError` is raised (never a raw traceback).

## Requirements *(mandatory)*

- **FR-001**: `make_provider("opencode-cli")` / `make_provider("opencode-cli:<provider/model>")` returns an `OpenCodeCLIProvider`; `complete()` runs `opencode run [--model <m>] <prompt>` and returns the assistant text (ANSI-stripped, trimmed). No API key required.
- **FR-002**: System prompt is prepended to the user prompt (parity with `claude_cli`). Output is sanitized downstream by `sanitize_model_spec` in the generation path.
- **FR-003**: Missing binary, non-zero exit, and timeout all raise `ProviderError` with a clear message.
- **FR-004**: Existing providers (`claude-cli`, `anthropic`, `openai`, `ollama`, `fake`) are unchanged. No grounding/rubric/reward/metric-definition change.
- **FR-005**: Built TDD — tests red before implementation.

### Key Entities
- **OpenCodeCLIProvider**: `LLMProvider` shelling out to `opencode run`.

## Success Criteria *(mandatory)*

- **SC-001**: With `--rollout-provider opencode-cli` the engine generates a spec via `opencode run` with **no API key** set (mirrors the `claude-cli` keyless path).
- **SC-002**: Bad/missing binary, non-zero exit, and timeout each surface a `ProviderError`. Full engine suite green.

## Assumptions
- `opencode run` is OpenCode's non-interactive mode and prints the assistant response to stdout. The live OpenCode call is not exercised in CI here (no `opencode` binary), mirroring the opt-in nature of the `claude_cli` live test; command construction + error paths are unit-tested with a mock.
