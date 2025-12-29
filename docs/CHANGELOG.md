# Changelog

## 2025-12-29

### Added
- Add [docs/TEST_PLAN.md](TEST_PLAN.md) with pytest suite ideas before implementation.
- Add pytest unit and integration coverage for item types, validators, engines, and CLI.
- Add pytest fixtures in `tests/conftest.py` for shared sample items and temp cwd.
- Add integration output checks for QTI ZIPs, human readable, BBQ, and HTML outputs.
- Add pytest unit coverage for text2qti and okla_chrst_bqgen reader parsing.
- Add reader/writer roundtrip smoke tests for BBQ, text2qti, and okla_chrst_bqgen engines.
- Add edge-case tests for text2qti and BBQ reader error paths plus okla unknown-block handling.
- Add unit coverage for missing NUM tolerances in BBQ/text2qti readers.
- Add unit coverage for NUM writers with zero tolerance.
- Add unit coverage for engine registry, manifest generation, YAML helpers, and anti-cheat.
- Add [docs/ENGINE_AUTHORING.md](ENGINE_AUTHORING.md) with engine authoring guidance.
- Add docs consistency check to keep engine names in sync with the registry.
- Add unit coverage for BaseEngine filename helpers and histogram output.
- Add CLI error-path coverage for invalid BBQ filenames.
- Add manifest schema metadata checks for QTI v1.2 and v2.1 outputs.
- Add engine class contract smoke tests (imports and write_item wiring).
- Add ZIP safety checks to prevent absolute or parent directory paths.
- Add BBQ parsing error-path coverage for missing correct flags.
- Add BaseItem repr smoke test.

### Changed
- Convert script-based tests into pytest functions using fixtures and tmp paths.
- Register pytest `smoke` marker and fix item type test inputs.
- Add format_html_lxml and anti-cheat edge case tests.
- Adjust BaseEngine test harness and anti-cheat expectations for current behavior.
- Use ItemBank.add_item_cls for okla_chrst_bqgen reader to preserve question text.
- Default BBQ NUM tolerance to 0.0 with a warning when the field is missing.
- Fix text2qti MA detection for `[ ]` choices and raise clearer errors for missing NUM/FIB answers.
- Emit explicit tolerance in text2qti NUM writer output (including 0.0).
- Limit BBQ and text2qti read skipping to parse-time ValueError/IndexError.

## 2025-12-20

### Added
- Add `docs/DEVELOPMENT.md` with setup, testing, and engine guidance.
- Add `docs/FORMATS.md` with input/output format notes and engine list.
- Add `docs/TROUBLESHOOTING.md` with common issues and fixes.
- Add `docs/INSTALL.md`, `docs/USAGE.md`, `docs/QUESTION_TYPES.md`, and
  `docs/ENGINES.md` to split README content into focused guides.
- Add `docs/RELATED_PROJECTS.md` and `docs/COMMUNITY.md` to move link lists and
  support info out of README.
- Add `TODO.md` to track feature ideas and missing item implementations, migrated from
  `TODO.txt`.
- Add `ROADMAP.md` to capture longer-form plans such as hints support.
- Add feedback planning section to `ROADMAP.md`.

### Changed
- Update `README.md` with documentation links and a backlog pointer.
- Update `TODO.md` to point hint planning at `ROADMAP.md`.
- Move documentation files (changelog, roadmap, todo, style guides, and legacy docs)
  into `docs/` to reduce root-level clutter.
- Split `README.md` into shorter sections with links to new docs.
- Rename `docs/INSTALLATION.md` to `docs/INSTALL.md` and
  `docs/DEVELOPER.md` to `docs/DEVELOPMENT.md`.

### Removed
- Remove legacy `docs/TODO.txt` and `docs/old_README.md` in favor of updated docs.

## 2025-12-12

### Added
- Add `qti_package_maker/common/tabulate_compat.py` with a fallback plain-text table renderer.
- Add HTML `<table>` to plain-text conversion in `qti_package_maker/common/string_functions.py`.

### Changed
- Use `tabulate_compat` in `qti_package_maker/assessment_items/item_bank.py` and
  `qti_package_maker/engines/engine_registration.py`.
- Pass `allow_mixed` through `qti_package_maker/package_interface.py` when supported, and
  forward it in `qti_package_maker/engines/text2qti/engine_class.py` and
  `qti_package_maker/engines/bbq_text_upload/engine_class.py`.
- Allow table markup in `qti_package_maker/engines/human_readable/write_item.py` content checks.

### Removed
- Remove unused variables in `qti_package_maker/engines/text2qti/write_item.py`.
- Remove unnecessary `global` declarations in `qti_package_maker/common/franken_bptools.py`.

### Chore
- Ignore `pyflakes.txt` in `.gitignore`.
- Mark tests executable: `tests/test_bbq_converter_all_types.py` and
  `tests/test_human_readable_tables.py`.
