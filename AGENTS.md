# Repository Guidelines

## Project Structure & Module Organization

- `qti_package_maker/`: main Python package.
  - `assessment_items/`: item type classes + validation.
  - `engines/`: format-specific readers/writers (e.g., `canvas_qti_v1_2/`, `blackboard_qti_v2_1/`, `bbq_text_upload/`, `html_selftest/`).
  - `common/`: shared utilities (text cleanup, YAML tools, manifests, etc.).
  - `data/`: packaged data files used at runtime.
- `tools/`: developer utilities (notably `tools/bbq_converter.py`).
- `tests/`: lightweight smoke tests and engine coverage scripts.
- `examples/`: small sample QTI ZIPs for manual validation.

For architecture context, see `docs/CODE_DESIGN.md`.

## Build, Test, and Development Commands

Common local setup:

- `python3 -m venv .venv && source .venv/bin/activate`: create/activate a venv.
- `pip install -r requirements.txt`: install runtime deps.
- `pip install -e .`: editable install for development.

Useful repo commands:

- `python3 tools/bbq_converter.py -i bbq-<name>-questions.txt -1`: convert BBQ text to Canvas QTI v1.2.
- `python3 tools/bbq_converter.py -i bbq-<name>-questions.txt --all`: generate all supported outputs.
- `python3 tests/test_all_engines.py`: smoke test writing all item types to all engines.
- `source source_me_for_testing.sh`: sets `PYTHONPATH` to repo root for running scripts without install.

## Coding Style & Naming Conventions

- **Indentation:** use **tabs** (see `docs/PYTHON_STYLE.md`); avoid formatters that convert tabs to spaces.
- Prefer Python 3.9+ compatible code (project metadata), keep lines ~100 chars.
- Use `#!/usr/bin/env python3` for executable scripts in `tools/` and `tests/`.
- Keep module/file names lowercase with underscores (e.g., `item_xml_helpers.py`).

## Testing Guidelines

- Tests here are primarily **smoke tests** (generate outputs, verify files exist).
- Add new coverage as a script in `tests/` named `test_<topic>.py`.
- Clean up generated artifacts (ZIP/HTML/TXT) in the test itself.

## Commit & Pull Request Guidelines

- Commit subjects in history are short and action-oriented (e.g., "Fix...", "Add...", "Refactor...").
- Include in PRs:
  - what formats/engines are affected (e.g., `canvas_qti_v1_2`, `bbq_text_upload`);
  - a minimal repro or sample input file name/pattern (`bbq-<name>-questions.txt`);
  - outputs produced (ZIP/HTML/TXT) and how you validated them.

## Agent-Specific Notes

- When adding an engine, follow the existing pattern in `qti_package_maker/engines/<engine_name>/` and register it via the engine registry.
- Keep changes narrowly scoped; update `README.md` capability tables if engine behavior changes.
See Markdown style in `docs/MARKDOWN_STYLE.md`.
When making edits, document them in `docs/CHANGELOG.md`.
See repo style in docs/REPO_STYLE.md.
Agents may run programs in the tests folder, including smoke tests and pyflakes/mypy runner scripts.

## Environment
Codex must run Python using `/opt/homebrew/opt/python@3.12/bin/python3.12` (use Python 3.12 only).
On this user's macOS (Homebrew Python 3.12), Python modules are installed to `/opt/homebrew/lib/python3.12/site-packages/`.
When in doubt, implement the changes the user asked for rather than waiting for a response; the user is not the best reader and will likely miss your request and then be confused why it was not implemented or fixed.
When changing code always run tests, documentation does not require tests.
