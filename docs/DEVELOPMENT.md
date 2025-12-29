# Developer guide

## Quick setup
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

If you want to run scripts without installing, load the local environment:
```sh
source source_me_for_testing.sh
```

## Running smoke tests
```sh
python3 tests/test_all_engines.py
```

Other helpful checks:
```sh
python3 tests/test_bbq_converter_all_types.py
python3 tests/test_human_readable_tables.py
```

## Style notes
- Use tabs for indentation (see [PYTHON_STYLE.md](PYTHON_STYLE.md)).
- Keep lines around 100 characters.
- Use `#!/usr/bin/env python3` for executable scripts in `tools/` and `tests/`.
- Target Python 3.9+ compatibility.

## Adding an engine
1. Create `qti_package_maker/engines/<engine_name>/` with an `engine_class.py` and
   format-specific helpers (for example `write_item.py`, `add_item.py`, `read_package.py`).
2. Follow the existing engine patterns so the registry can discover it.
3. Update the capability tables in [README.md](../README.md).
4. Add or update smoke tests in `tests/` and document changes in
   [CHANGELOG.md](CHANGELOG.md).

For a full checklist, see [ENGINE_AUTHORING.md](ENGINE_AUTHORING.md).

## References
- [CODE_DESIGN.md](CODE_DESIGN.md)
- [PYTHON_STYLE.md](PYTHON_STYLE.md)
- [CHANGELOG.md](CHANGELOG.md)
