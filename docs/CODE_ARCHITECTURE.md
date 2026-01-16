# Code architecture

## Overview
qti_package_maker is a Python package and CLI that converts Blackboard Question Upload
(BBQ) text files into QTI packages and other export formats by routing items through
a shared item bank and format-specific engines.

## Major components
- [qti_package_maker/package_interface.py](../qti_package_maker/package_interface.py): Public
  orchestration API that loads engines, manages the item bank, and saves outputs.
- [qti_package_maker/assessment_items](../qti_package_maker/assessment_items): Item classes,
  validation, and the ItemBank container.
- [qti_package_maker/engines](../qti_package_maker/engines): Engine registry, base engine,
  and per-format readers and writers.
- [qti_package_maker/common](../qti_package_maker/common): Shared helpers such as strings,
  manifests, and color utilities.
- [tools/bbq_converter.py](../tools/bbq_converter.py): Primary CLI for reading BBQ input and
  writing output formats.
- [tests](../tests): Unit and integration coverage for engines, item types, and tools.

## Data flow
- Input BBQ file is passed to [tools/bbq_converter.py](../tools/bbq_converter.py).
- [qti_package_maker/package_interface.py](../qti_package_maker/package_interface.py)
  loads the BBQ reader engine and parses items into an ItemBank.
- The ItemBank is passed to one or more engines for format-specific export.
- Engines write output artifacts (ZIP, HTML, or text) based on the selected format.

## Testing and verification
- Smoke test all engines: `python3 tests/test_all_engines.py`.
- Pytest suite: `python3 -m pytest`.
- Pyflakes scan: `bash tests/run_pyflakes.sh`.
- ASCII compliance scan: `python3 tests/run_ascii_compliance.py`.

## Extension points
- Add a new engine under [qti_package_maker/engines](../qti_package_maker/engines) with an
  `engine_class.py`; it is discovered by
  [qti_package_maker/engines/engine_registration.py](../qti_package_maker/engines/engine_registration.py).
- Add or adjust item types in
  [qti_package_maker/assessment_items/item_types.py](../qti_package_maker/assessment_items/item_types.py)
  and validation rules in
  [qti_package_maker/assessment_items/validator.py](../qti_package_maker/assessment_items/validator.py).
- Extend shared helpers in
  [qti_package_maker/common](../qti_package_maker/common) when logic is reused across engines.
- Add new CLIs in [tools](../tools) when a script is needed beyond the core package API.

## Known gaps
- Confirm the full list of supported input formats beyond BBQ text.
- Document per-engine output file naming and locations.
