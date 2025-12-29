# Engine authoring guide

This guide explains the required files, functions, and common patterns for adding a new
engine to `qti_package_maker`.

## Directory layout
- Create a new package under `qti_package_maker/engines/<engine_name>/`.
- Include at least these files:
  - `engine_class.py`: the engine entry point.
  - `write_item.py`: per-item writers for supported types.
  - `read_package.py`: per-item readers if the engine can read.
- Add an empty `__init__.py` so the folder is importable.

Example layout:
```text
qti_package_maker/engines/<engine_name>/
	__init__.py
	engine_class.py
	write_item.py
	read_package.py
```

## Required functions

### engine_class.py
Implement `EngineClass` that subclasses `BaseEngine`.

Required methods:
- `__init__(self, package_name: str, verbose: bool = False)`
  - set `self.write_item` to your `write_item` module
  - call `self.validate_write_item_module()`
- `save_package(self, item_bank, outfile: str = None)`
  - iterate over `self.process_item_bank(item_bank)`
  - write outputs to a file (or ZIP) using `self.get_outfile_name(...)`
- `read_items_from_file(self, infile: str, allow_mixed: bool = False)`
  - only if the engine supports reading
  - call `read_package.read_items_from_file(...)` and return an `ItemBank`

The registry discovers engines by importing
`qti_package_maker.engines.<engine_name>.engine_class.EngineClass`.

### write_item.py
Write one function per supported item type. Common names:
- `MC`, `MA`, `MATCH`, `NUM`, `FIB`, `MULTI_FIB`, `ORDER`

Each function receives a fully validated item class and returns:
- a string (for text-based outputs), or
- an XML element (for QTI engines), or
- `None` if the type is unsupported for this engine.

Keep output stable and deterministic to avoid flaky tests.

### read_package.py
If your engine reads input, implement:
- `read_items_from_file(input_file: str, allow_mixed: bool = False) -> ItemBank`
- helper readers such as `read_MC`, `read_NUM`, etc.

Return an `ItemBank` and use `add_item_cls` to preserve CRCs and metadata.

## Registration and discovery
Engines are auto-registered by scanning `qti_package_maker/engines/`.
To be discoverable:
- the folder must be a package (`__init__.py`)
- it must contain `engine_class.py` with `EngineClass`
- the folder name is the engine name shown in tables

You do not need to edit `engine_registration.py`.

## Tips and conventions
- Use tabs for indentation in Python files. See [PYTHON_STYLE.md](PYTHON_STYLE.md).
- Keep lines around 100 characters.
- Use `BaseEngine.get_outfile_name(...)` to standardize output naming.
- Call `ItemBank.renumber_items()` before writing to keep item numbers stable.
- Reuse helpers from `qti_package_maker/common/` and existing engines.
- For HTML or XML outputs, keep formatting stable to simplify tests.
- When a format cannot support an item type, return `None` in the writer.

## Testing checklist
- Add or update smoke tests in `tests/` (see `tests/test_all_engines.py`).
- If reading is supported, add roundtrip tests in `tests/integration/`.
- Update capability tables in [README.md](../README.md).
- Document changes in [CHANGELOG.md](CHANGELOG.md).

## References
- [CODE_DESIGN.md](CODE_DESIGN.md)
- [DEVELOPMENT.md](DEVELOPMENT.md)
