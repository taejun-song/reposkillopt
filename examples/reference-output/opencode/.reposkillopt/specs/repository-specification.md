---
spec_id: click-8.1.7
target_repository: pallets/click
target_repository_url: https://github.com/pallets/click
target_repository_commit: 8.1.7
skill_version: 0.1.0
adapter: opencode
created: 2026-05-31
revised: 2026-05-31
revision: 2
status: revised
---

# Repository Specification — pallets/click

## Repository overview

**[fact]** Click is "a simple Python module inspired by the stdlib `optparse` to make writing command line scripts fun" — distributed as the `click` package (`src/click/__init__.py:1-5`).

**[fact]** The repository's metadata describes it as a "Composable command line interface toolkit", licensed BSD-3-Clause, maintained by the Pallets organization (`setup.cfg:5-20`).

**[fact]** The version under analysis is `8.1.7`, declared at `src/click/__init__.py:73` (`__version__ = "8.1.7"`).

**[inference]** The codebase is library-shaped (no application entrypoint of its own; consumers embed it via decorators in their own scripts). Basis: the package exposes a public API only via `__init__.py` re-exports (`src/click/__init__.py:6-72`) and ships no `__main__.py` or `console_scripts` of its own.

## Technology stack

**[fact]** Language: Python; minimum runtime `python_requires = >= 3.7` (`setup.cfg:32`).

**[fact]** Packaging: `setuptools` via `setup.cfg` plus a small `setup.py` that only declares `install_requires` (`setup.py:1-9`). No `pyproject.toml`-only PEP-621 metadata; build remains setuptools-driven.

**[fact]** Runtime dependencies (per `setup.py:3-8`):
- `colorama` on Windows only (`platform_system == 'Windows'`)
- `importlib-metadata` only on Python `< 3.8`

Otherwise the library has **no required third-party runtime dependencies**.

**[fact]** Static analysis tooling configured in-repo: `mypy` (strict mode — `disallow_untyped_defs`, `strict_equality`, `warn_unreachable`, etc., `setup.cfg:73-92`); `flake8` with `bugbear`, `pycodestyle`, `implicit-string-concat` (`setup.cfg:56-72`); `pre-commit` via the `[testenv:style]` tox env (`tox.ini:15-18`).

**[fact]** Test runner: `pytest`, configured under `[tool:pytest]` (`setup.cfg:39-42`) with `testpaths = tests` and `filterwarnings = error`.

## Build and runtime commands

**[fact]** Develop install: standard setuptools editable install (`pip install -e .`) — derived from `setup.cfg [options]` plus `setup.py` (`setup.py:1-9`).

**[fact]** Run the test suite locally: `pytest -v --tb=short` — derived from the tox commands at `tox.ini:13`.

**[fact]** Multi-environment matrix testing: `tox` against `py3{12,11,10,9,8,7}` plus `pypy310`, with `style`, `typing`, and `docs` environments (`tox.ini:1-11`).

**[fact]** Build documentation: `sphinx-build -W -b html -d {envtmpdir}/doctrees docs {envtmpdir}/html` (`tox.ini:32`).

**[fact]** Typing checks: `mypy` plus `pyright` (`tox.ini:24-28`); `mypy` configured to lint `src/click` and `tests/typing` (`setup.cfg:74`).

## Major entrypoints

Click has no application entrypoint of its own; the "entrypoints" are the public-API symbols that user code imports.

Two distinctions matter (per `FB-2026-05-31-001`): the **decorator factory** (a function the user calls to *create* a Command) and the **invocable Command instance** (what the user actually invokes after decoration). Both are entrypoints in different senses.

**[fact]** Public-API surface is re-exported by `src/click/__init__.py:6-72` and includes:
- **Decorator factories** (the symbols user code imports and calls to *build* invocables): `click.command` (`src/click/__init__.py:13`, defined at `src/click/decorators.py:171`), `click.group` (`__init__.py:15`, defined at `decorators.py:292`), `click.option` (`__init__.py:18`, defined at `decorators.py:351`), `click.argument` (`__init__.py:12`, defined at `decorators.py:323`), `click.pass_context` (`__init__.py:19`), `click.pass_obj` (`__init__.py:20`).
- **Resulting invocable `Command` instance** — what the user actually calls; the `command` decorator returns one (`src/click/decorators.py:241-249`).
- Canonical smallest-working-example: `tests/test_basic.py:8-23` (`test_basic_functionality`) — a `@click.command def cli(): …` followed by `runner.invoke(cli, ["--help"])`.
- Core classes: `Command` (`core.py:1160`), `Group` (`core.py:1781`), `MultiCommand` (`core.py:1472`), `Context` (`core.py:160`), `Parameter` / `Option` / `Argument` (`core.py:2012` / `2449` / `2969`).
- Output / TUI helpers: `echo` (`utils.py`), `prompt`, `confirm`, `progressbar`, `style`, `secho`, `edit`, `launch`, `pause`, `getchar`, `clear`, `echo_via_pager` (re-exported at `__init__.py:40-51`; defined under `termui.py`).
- Parameter types: `BOOL`, `INT`, `FLOAT`, `STRING`, `UUID`, `Choice`, `DateTime`, `File`, `Path`, `IntRange`, `FloatRange`, `Tuple`, `UNPROCESSED`, `ParamType` (re-exported at `__init__.py:52-65`; defined under `types.py`).
- Exceptions: `ClickException`, `UsageError`, `BadParameter`, `BadArgumentUsage`, `BadOptionUsage`, `FileError`, `MissingParameter`, `NoSuchOption`, `Abort` (`__init__.py:30-39`, defined in `exceptions.py`).
- Testing helper: `click.testing.CliRunner` (`src/click/testing.py:1-479`) — used by `tests/conftest.py:1-9` to provide the `runner` fixture.

**[fact]** Invocation entrypoint inside the library: `BaseCommand.main` at `src/click/core.py:1010-1100` (with two type-only overloads at `core.py:989` and `core.py:1000`). User scripts indirectly trigger `main` by calling the command instance: `BaseCommand.__call__` at `core.py:1147-1149` is an alias for `main`.

## Architectural layers

**[fact]** The codebase has six identifiable layers (file-and-symbol attribution below):
1. **Public API surface** — `src/click/__init__.py:1-73` (re-exports only).
2. **User-facing decorators** — `src/click/decorators.py` (561 lines): `command`, `group`, `option`, `argument`, `pass_context`, `pass_obj`, `make_pass_decorator`, `confirmation_option`, `password_option`, `version_option`, `help_option`.
3. **Core execution model** — `src/click/core.py` (3042 lines): `Context`, `BaseCommand`, `Command`, `MultiCommand`, `Group`, `CommandCollection`, `Parameter`, `Option`, `Argument`.
4. **Parsing** — `src/click/parser.py` (529 lines): `OptionParser`, `ParsingState`, `split_arg_string`.
5. **Terminal UI & I/O** — `src/click/termui.py` (784 lines, public) + `src/click/_termui_impl.py` (739 lines, internal) + `src/click/formatting.py` (301 lines, help text rendering).
6. **Platform compatibility shims** — `src/click/_compat.py` (623 lines), `src/click/_winconsole.py` (279 lines), `src/click/_textwrap.py` (49 lines).

**[fact]** Cross-cutting modules: `src/click/types.py` (1089 lines, parameter-type system); `src/click/exceptions.py` (288 lines); `src/click/utils.py` (624 lines, `echo`/`get_app_dir`/`open_file`/etc.); `src/click/globals.py` (68 lines, thread-local context stack); `src/click/shell_completion.py` (596 lines).

**[inference]** Dependency direction within the library: `__init__.py` depends on everything; `decorators.py` depends on `core.py` and `types.py`; `core.py` depends on `parser.py`, `types.py`, `exceptions.py`, `formatting.py`, `globals.py`, `utils.py`; `parser.py` depends on `exceptions.py`. Basis: `from .core import …` / `from .parser import …` import patterns observed at the top of each module (e.g., `src/click/shell_completion.py:6-13`).

## Core modules

**[fact]** Module-by-module (file size in lines):
- `src/click/__init__.py` (73) — public-API re-exports and `__version__`.
- `src/click/core.py` (3042) — `Context`, `BaseCommand` and concrete subclasses (`Command`, `MultiCommand`, `Group`, `CommandCollection`), parameter model (`Parameter`, `Option`, `Argument`), `ParameterSource` enum.
- `src/click/decorators.py` (561) — user-facing decorator factories (`command`, `group`, `option`, `argument`, plus four convenience decorators: `confirmation_option`, `password_option`, `version_option`, `help_option`).
- `src/click/parser.py` (529) — Click's internal option parser (`OptionParser` at L253, `ParsingState` at L245, helpers `split_opt`/`normalize_opt`/`split_arg_string`).
- `src/click/types.py` (1089) — `ParamType` and all built-in types.
- `src/click/exceptions.py` (288) — exception hierarchy rooted at `ClickException`.
- `src/click/formatting.py` (301) — `HelpFormatter` and `wrap_text`.
- `src/click/globals.py` (68) — thread-local context stack: `_local`, `push_context`, `pop_context`, `get_current_context`, `resolve_color_default`.
- `src/click/termui.py` (784) — public terminal-UI functions: `echo_via_pager`, `prompt`, `confirm`, `progressbar`, `clear`, `style`, `secho`, `edit`, `launch`, `pause`, `getchar`, `unstyle`.
- `src/click/_termui_impl.py` (739) — internal implementations called by `termui.py`.
- `src/click/utils.py` (624) — `echo`, `get_app_dir`, `open_file`, `format_filename`, `get_binary_stream`, `get_text_stream`.
- `src/click/testing.py` (479) — `CliRunner` and `Result` test helpers.
- `src/click/shell_completion.py` (596) — `shell_complete` + per-shell completion classes; entered via `BaseCommand._main_shell_completion` at `core.py:1123-1152`.
- `src/click/_compat.py` (623) — Python-version and platform-compat helpers (e.g., `_NonClosingTextIOWrapper` referenced by `_winconsole.py:28`).
- `src/click/_winconsole.py` (279) — Windows console I/O. Header notes "based on the excellent work by Adam Bartoš … issue1602 in the Python bug tracker" (`_winconsole.py:1-7`) and asserts `sys.platform == "win32"` (`_winconsole.py:30`).
- `src/click/_textwrap.py` (49) — small text-wrapping helper used by `formatting.py`.
- `src/click/py.typed` — PEP-561 marker so consumers see Click's type annotations.

## Domain model

**[fact]** The user-facing domain model is built from these classes (all in `src/click/core.py`):
- **Command** (`core.py:1160`, base `BaseCommand` at `core.py:834`) — a leaf invocable. Carries its name, callback, list of `Parameter`s, help text.
- **MultiCommand** (`core.py:1472`) — an invocable that dispatches to subcommands.
- **Group** (`core.py:1781`) — concrete `MultiCommand` that manages a dict of named subcommands.
- **CommandCollection** (`core.py:1957`) — a `MultiCommand` that aggregates several `MultiCommand` sources into one namespace.
- **Context** (`core.py:160`) — per-invocation state: parent context, info_name, parameters, obj/payload, environment-variable prefix, parsing flags, color settings, formatter class.
- **Parameter** (`core.py:2012`) — base class for command-line parameters; concrete subclasses **Option** (`core.py:2449`) and **Argument** (`core.py:2969`).
- **ParameterSource** (`core.py:134`) — enum recording how a parameter received its value (command line / env var / default / etc.).
- **ParamType** (defined in `src/click/types.py`) — the conversion contract; every parameter has a `ParamType`.

**[fact]** Group/Command composition: groups carry subcommands; user code attaches subcommands either by `@group.command()` (the `MultiCommand` decorator path) or by calling `group.add_command(cmd)`. Definitions at `core.py:1472-1957`.

**[human]** Click's documentation uses "**multi command**" as the umbrella term for any `BaseCommand` subclass that dispatches to subcommands. Concretely, `MultiCommand` (`core.py:1472`) is the parent of both `Group` (`core.py:1781`) and `CommandCollection` (`core.py:1957`). This term is **repository-specific Click vocabulary**: it should not be applied to other CLI codebases, where similar concepts go by different names (e.g., "subcommand router", "command tree"). (Source: `FB-2026-05-31-003`.)

## Data model

**Not applicable.** Click is a runtime library with no persistent data store. The only "state" is per-process: the thread-local context stack maintained at `src/click/globals.py:7-46` (`_local`, `push_context`, `pop_context`, `get_current_context`) and the `Context` objects themselves (`core.py:160`).

## External integrations

**[fact]** Required external integrations are limited to two conditional dependencies (`setup.py:3-8`):
- **`colorama`** — only when `platform_system == 'Windows'`. Used by the terminal-color path; `mypy` config explicitly silences `colorama.*` missing-import warnings at `setup.cfg:99-100`.
- **`importlib-metadata`** — only when `python_version < '3.8'` (because `importlib.metadata` was only added in stdlib 3.8). `mypy` silences its missing-import warning at `setup.cfg:102-103`.

**[fact]** Click has no required network or filesystem-side-effect integrations of its own.

**[inference]** The package may be paged through the user's pager (`echo_via_pager` at `termui.py`, re-exported `__init__.py:42`) and may launch external editors (`edit` at `termui.py`, re-exported `__init__.py:43`). Basis: presence of these symbols in the public API. These are user-controlled and not "integrations" in the third-party-service sense.

## Control-flow traces

**[fact]** Trace — invoking a decorated Click CLI (`@click.command def foo(): …; foo()`):

1. `@click.command` evaluated → `click.command` factory at `src/click/decorators.py:171` constructs a `Command` instance (`decorators.py:241-249`) and returns it; the user's `foo` symbol now refers to a `Command` object, not the original function.
2. User code calls `foo(["--help"])` (or just `foo()`, picking up `sys.argv[1:]`).
3. `Command.__call__` (inherited from `BaseCommand.__call__` at `core.py:1147-1149`) aliases to `BaseCommand.main`.
4. `BaseCommand.main` (real impl at `core.py:1010-1100`) executes:
   - Defaults `args` to `sys.argv[1:]` (`core.py:1083-1085`); on Windows, additionally calls `_expand_args` (`core.py:1085-1086`).
   - Calls `_main_shell_completion` (`core.py:1123-1152`) to short-circuit into the completion path if the appropriate `_<PROG>_COMPLETE` env var is set.
   - Otherwise constructs a `Context` via `self.make_context(prog_name, args, …)` (referenced from `BaseCommand.make_context` at `core.py:907`).
   - Calls `self.invoke(ctx)` (one of the `invoke` overloads at `core.py:715-732`; concrete impls at `Command.invoke` `core.py:1423`, `MultiCommand.invoke` `core.py:1654`).
   - Wraps the call in exception handling for `ClickException`, `Exit`, and `Abort` (`core.py:1103-1124`).
5. `Command.invoke` calls the user's original callback with the parsed parameters from `Context.params`.

**[fact]** Trace — `Group` dispatch:
1. As above, but the top-level object is a `Group` (`core.py:1781`), which is a `MultiCommand` (`core.py:1472`), which is a `Command` (`core.py:1160`).
2. `MultiCommand.invoke` at `core.py:1654` parses the remaining arguments to extract the subcommand name, looks it up via `MultiCommand.get_command`, makes a new `Context` for the subcommand, and recursively invokes it.

## Data-flow traces

**[fact]** Trace — argv to callback kwargs:

1. **Ingress**: a list of strings (`sys.argv[1:]` by default) enters `BaseCommand.main` (`core.py:1083-1086`).
2. **Tokenization & parsing**: in `make_context`, an `OptionParser` (`src/click/parser.py:253`) processes the arg list against the `Parameter` set declared on the `Command`. The parser produces values keyed by parameter name.
3. **Type conversion**: each parameter's `ParamType.convert` (in `src/click/types.py`) converts the raw string value to the target Python type (`int`, `float`, `bool`, `Path`, custom `ParamType`, etc.).
4. **Defaults & env-var fallback**: parameters whose value is missing get their default; if `auto_envvar_prefix` is set on the `Context` (or `envvar=` is set on the parameter), the env var is consulted. `ParameterSource` (`core.py:134`) records the origin.
5. **Storage in `Context.params`**: the converted values are stored as a `dict[str, Any]` on the `Context`.
6. **Callback invocation**: `Command.invoke` (`core.py:1423`) calls the user's callback with `**ctx.params`. The callback's return value is propagated.
7. **Egress**: in standalone mode (`standalone_mode=True`, the default per `core.py:1010-1015`), `main` calls `sys.exit` with the appropriate exit code; otherwise the return value flows back to the caller.

## Dependency map

**[fact]** **Internal dependency graph** (file → modules it imports from sibling files; based on top-of-file `from .X import …` statements; spot-checked at `src/click/shell_completion.py:6-13` and `src/click/_winconsole.py:28`):
- `__init__.py` → `core`, `decorators`, `exceptions`, `formatting`, `globals`, `parser`, `termui`, `types`, `utils`.
- `decorators.py` → `core`, `types`.
- `core.py` → `parser`, `types`, `exceptions`, `formatting`, `globals`, `utils`, `_compat`, `termui` (lazy, in some methods).
- `parser.py` → `exceptions`.
- `shell_completion.py` → `core`, `parser`, `utils`.
- `termui.py` → `_compat`, `_termui_impl`, `globals`, `utils`, `exceptions`, `types`.
- `_winconsole.py` → `_compat`.
- `_termui_impl.py` → `_compat`, `globals`, `utils`.
- `testing.py` → `_compat`, `core`, `formatting`, `termui`, `utils`.

**[fact]** **External dependencies** (`setup.py:3-8`):
- `colorama` (Windows only).
- `importlib-metadata` (Python < 3.8 only).
No other runtime external dependencies.

**[inference]** Development/test/typing/docs dependencies are managed in `requirements/*.txt` (autogenerated by `pip-compile-multi`, header at e.g. `requirements/tests.txt:1-5`). Specific dev-time packages are not enumerated here as they do not affect runtime behavior.

## Configuration map

**[fact]** Click reads configuration primarily from per-`Context` constructor arguments (see the `Context` docstring at `src/click/core.py:161-258`):
- `auto_envvar_prefix` — when set, individual `Option`s consult `{PREFIX}_{NAME}` environment variables. Default: `None` (disabled).
- `default_map` — dict-like with per-parameter defaults.
- `terminal_width`, `max_content_width` — help-rendering widths.
- `resilient_parsing`, `allow_extra_args`, `allow_interspersed_args`, `ignore_unknown_options` — parsing flexibility flags.
- `help_option_names` — names of the help option(s); default `['--help']`.
- `token_normalize_func` — optional callable for case-insensitive matching etc.
- `color`, `show_default` — display behavior.

**[fact]** Shell-completion env var: `_{PROG_NAME}_COMPLETE` (uppercased, `-` and `.` → `_`) — read in `BaseCommand._main_shell_completion` at `src/click/core.py:1140-1146` to short-circuit into the completion path when set.

**[fact]** `mypy` and `flake8` settings live in `setup.cfg` (`setup.cfg:56-103`). `pytest` settings live in `setup.cfg:39-42`. `tox` envs are defined in `tox.ini`.

## Testing strategy

**[fact]** Test framework: `pytest`, configured at `setup.cfg:39-42` with `testpaths = tests` and `filterwarnings = error` (any warning becomes a test failure).

**[fact]** Test layout: `tests/` directory with one `test_*.py` file per concern. Twenty files at the inspected commit:
`test_arguments.py`, `test_basic.py`, `test_chain.py`, `test_command_decorators.py`, `test_commands.py`, `test_compat.py`, `test_context.py`, `test_custom_classes.py`, `test_defaults.py`, `test_formatting.py`, `test_imports.py`, `test_info_dict.py`, `test_normalization.py`, `test_options.py`, `test_parser.py`, `test_shell_completion.py`, `test_termui.py`, `test_testing.py`, `test_types.py`, plus `conftest.py`.

**[human]** A second test tree, `tests/typing/`, is exercised by `pyright tests/typing` (`tox.ini:24-28`); the `mypy` configuration also covers it (`setup.cfg:74`). It is not run by the default `pytest` invocation, so it is easy to miss on a casual inspection. (Source: `FB-2026-05-31-002`.)

**[fact]** Shared fixture: `runner` (a `CliRunner` instance) provided by `tests/conftest.py:1-9`. Example consumer at `tests/test_basic.py:8-23` (the `runner.invoke(cli, ["--help"])` pattern).

**[fact]** Matrix coverage via `tox.ini:1-11`: CPython 3.7–3.12 plus PyPy 3.10; plus dedicated `style`, `typing`, and `docs` envs.

**[fact]** Typing tests: `mypy` covers `src/click` and `tests/typing` (`setup.cfg:74`); `pyright` runs both `--verifytypes click` and against `tests/typing` (`tox.ini:25-28`).

## Deployment assumptions

**[fact]** Click is distributed via PyPI as a library. It is **not** itself an executable application — there is no `__main__.py`, no `console_scripts` entry in `setup.cfg`, no Dockerfile.

**[fact]** End consumers embed Click by importing it from their own Python scripts (or wheels), typically wiring a `@click.command()`-decorated function into a `console_scripts` entry of their own package.

**[fact]** Build artifacts: source distribution + universal Python wheel built by setuptools (`setup.cfg [options]`, `tox.ini` uses `package = wheel` at `tox.ini:7`).

**[unknown]** The exact PyPI publishing workflow (which CI job, which credentials, which signing/attestation) is not visible from inspection alone; CI configuration (`.github/workflows/`) was not enumerated in this rollout. See *Unknowns*.

## Change-impact map

**[fact]** Change-impact relationships derived from the dependency map above:
- Changes to `src/click/parser.py` affect **every** `Command` because all parsing flows through `OptionParser` (`parser.py:253`) via `Command.make_context` (`core.py:907`).
- Changes to `Context` (`core.py:160`) affect every invocation since every command runs inside a Context.
- Changes to `BaseCommand.main` (`core.py:1010-1100`) affect every standalone invocation.
- Changes to `src/click/types.py` `ParamType` subclasses affect any user-declared `Option`/`Argument` using that type.
- Changes to `src/click/shell_completion.py` affect **only** the shell-completion code path (entered via `BaseCommand._main_shell_completion`, `core.py:1123-1152`); they do not affect ordinary CLI execution.
- Changes to `src/click/_winconsole.py` or the Windows branches of `src/click/_compat.py` affect Windows users only; the Linux/macOS code paths are unaffected.

**[inference]** Adding a new parameter type (a new `ParamType` subclass in `types.py`) is low-risk because the type-conversion contract is open-ended; existing types are not affected. Basis: each type implements `ParamType.convert` independently (visible in `types.py` structure).

## Known risks

- **[fact]** **Strict typing settings can break CI on innocuous-looking edits.** `mypy` is configured with `disallow_untyped_defs`, `disallow_incomplete_defs`, `strict_equality`, `warn_unreachable`, `warn_unused_ignores`, `no_implicit_reexport`, etc. (`setup.cfg:74-92`). Adding an unannotated helper or a now-unnecessary `# type: ignore` will fail CI.

- **[fact]** **`filterwarnings = error` makes any new warning a test failure** (`setup.cfg:41-42`). Upstream deprecation warnings in `colorama`, `importlib-metadata`, or any test-time dependency can break the suite even if Click itself is unchanged.

- **[fact]** **Windows-only code paths are platform-sensitive.** `src/click/_winconsole.py:30` asserts `sys.platform == "win32"` and uses raw `ctypes` against the Win32 console API (`_winconsole.py:8-27`). Changes here are validated only on Windows runners; Linux CI gives no signal.

- **[fact]** **Shell completion is per-shell.** `src/click/shell_completion.py:18-78` dispatches by shell name; supporting a new shell version (or a breaking change in an existing shell's completion protocol) requires per-shell handling and is not exercised by typical `pytest tests/`.

- **[inference]** **Public API drift is heavily constrained.** Every public symbol is explicitly re-exported in `src/click/__init__.py:6-72`. Renaming or removing a symbol there is a semver-major breaking change for downstream users. Basis: per-symbol `from … import X as X` pattern signals deliberate public API.

## Unknowns and unresolved questions

- **[unknown]** CI workflow content (`.github/workflows/*.yml`) was not enumerated in this rollout. Concretely: which Python versions actually run in CI vs. the tox `envlist` declaration; how releases are cut and published to PyPI.
- **[unknown]** Whether the contents of `examples/` (aliases, colors, completion, complex, imagepipe, inout, naval, repo, termui, validation) are exercised by automated tests, or are documentation-only.
- **[unknown]** Whether `requirements/*.in` → `requirements/*.txt` regeneration is gated on CI (the file headers note `pip-compile-multi`, but its invocation site was not located in this pass).
- **[unknown]** Exactly which shells `shell_completion.py` supports out-of-the-box and which version thresholds apply (a deeper read of `shell_completion.py` is required).

## Evidence index

- `src/click/__init__.py:1-5` — module docstring identifying Click as inspired by `optparse`.
- `src/click/__init__.py:6-72` — public-API re-exports.
- `src/click/__init__.py:73` — `__version__ = "8.1.7"`.
- `src/click/core.py:134` — `ParameterSource` enum.
- `src/click/core.py:160` — `Context` class.
- `src/click/core.py:161-258` — `Context` constructor docstring (parameter semantics).
- `src/click/core.py:715-732` — `invoke` overloads.
- `src/click/core.py:834` — `BaseCommand` class.
- `src/click/core.py:907` — `BaseCommand.make_context`.
- `src/click/core.py:953` — `BaseCommand.invoke`.
- `src/click/core.py:989` — `BaseCommand.main` overload #1.
- `src/click/core.py:1000` — `BaseCommand.main` overload #2.
- `src/click/core.py:1010-1100` — `BaseCommand.main` real implementation.
- `src/click/core.py:1083-1086` — argv default + Windows expansion.
- `src/click/core.py:1103-1124` — exception handling around `invoke`.
- `src/click/core.py:1123-1152` — `BaseCommand._main_shell_completion`.
- `src/click/core.py:1140-1146` — `_PROG_COMPLETE` env-var resolution.
- `src/click/core.py:1147-1149` — `BaseCommand.__call__` alias to `main`.
- `src/click/core.py:1160` — `Command` class.
- `src/click/core.py:1423` — `Command.invoke`.
- `src/click/core.py:1472` — `MultiCommand` class.
- `src/click/core.py:1654` — `MultiCommand.invoke`.
- `src/click/core.py:1781` — `Group` class.
- `src/click/core.py:1957` — `CommandCollection` class.
- `src/click/core.py:2012` — `Parameter` class.
- `src/click/core.py:2449` — `Option` class.
- `src/click/core.py:2969` — `Argument` class.
- `src/click/decorators.py:171` — `command` decorator (real impl).
- `src/click/decorators.py:241-249` — `Command` instantiation inside `command` decorator.
- `src/click/decorators.py:292` — `group` decorator.
- `src/click/decorators.py:323` — `argument` decorator.
- `src/click/decorators.py:351` — `option` decorator.
- `src/click/exceptions.py` — exception hierarchy file (288 lines).
- `src/click/formatting.py` — `HelpFormatter` file (301 lines).
- `src/click/globals.py:1-46` — thread-local context stack and helpers.
- `src/click/parser.py:245` — `ParsingState`.
- `src/click/parser.py:253` — `OptionParser`.
- `src/click/shell_completion.py:6-13` — imports from `core` and `parser`.
- `src/click/shell_completion.py:18-78` — `shell_complete` entrypoint.
- `src/click/termui.py` — public terminal-UI helpers (784 lines).
- `src/click/testing.py:1-479` — `CliRunner` and `Result`.
- `src/click/types.py` — `ParamType` and built-in types (1089 lines).
- `src/click/_winconsole.py:1-7` — provenance comment.
- `src/click/_winconsole.py:28` — `from ._compat import _NonClosingTextIOWrapper`.
- `src/click/_winconsole.py:30` — `assert sys.platform == "win32"`.
- `setup.cfg:5-20` — package metadata.
- `setup.cfg:32` — `python_requires = >= 3.7`.
- `setup.cfg:39-42` — `[tool:pytest]` config.
- `setup.cfg:56-72` — `[flake8]` config.
- `setup.cfg:73-92` — `[mypy]` config.
- `setup.cfg:74` — `mypy files = src/click, tests/typing`.
- `setup.cfg:99-100` — `mypy-colorama.*` silence.
- `setup.cfg:102-103` — `mypy-importlib_metadata.*` silence.
- `setup.py:1-9` — `install_requires` declaration.
- `tests/conftest.py:1-9` — `runner` fixture (`CliRunner`).
- `tests/test_basic.py:8-23` — example test using the `runner` fixture.
- `tox.ini:1-11` — envlist (CPython 3.7–3.12, PyPy 3.10, style, typing, docs).
- `tox.ini:7` — `package = wheel`.
- `tox.ini:13` — `pytest -v --tb=short`.
- `tox.ini:15-18` — `[testenv:style]` (pre-commit).
- `tox.ini:24-28` — `[testenv:typing]` (mypy + pyright).
- `tox.ini:32` — `[testenv:docs]` (sphinx-build).
- `FB-2026-05-31-001` — entrypoint-correction Feedback Item; reshaped *Major entrypoints*.
- `FB-2026-05-31-002` — missing-context Feedback Item; added `tests/typing/` to *Testing strategy*.
- `FB-2026-05-31-003` — terminology Feedback Item; added "multi command" note as `**[human]**` in *Domain model*.

## Change log

- **revision 1 → 2** (2026-05-31): Applied three Feedback Items — `FB-2026-05-31-001` (clarified decorator-factory vs invocable-Command distinction in *Major entrypoints*, added `tests/test_basic.py:8-23` pointer), `FB-2026-05-31-002` (added `tests/typing/` to *Testing strategy* as a `**[human]**` claim), `FB-2026-05-31-003` (added the "multi command" terminology note to *Domain model* as a `**[human]**` claim with explicit repo-scoped marker).
