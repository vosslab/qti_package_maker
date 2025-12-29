# Engine authoring guide

This guide explains the required files, functions, and common patterns for adding a new
engine to `qti_package_maker`.

## What you are building

An engine is a format adapter that converts external files into internal assessment
items stored in an `ItemBank`, or exports those items back out to a format.

## Directory layout
- Create a new package under `qti_package_maker/engines/<engine_name>/`.
- Include at least `engine_class.py` and a writer module (usually `write_item.py`).
- Add `read_package.py` only if the engine can read.
- Add an empty `__init__.py` so the folder is importable.

| File | Required | When you need it | Typical contents |
| --- | --- | --- | --- |
| `engine_class.py` | Yes | Always | `EngineClass`, wiring, registration hooks |
| `write_item.py` | Usually | Any writer | per-item-type renderers |
| `read_package.py` | Only for readers | Any read and write engine | unpack, parse, build items |
| `__init__.py` | Yes | Always | package import, discovery |

Example layout:
```text
qti_package_maker/engines/<engine_name>/
	__init__.py
	engine_class.py
	write_item.py
	read_package.py
```

## Minimal working engine
Use this as a starting point for a write-only engine that supports `MC` and returns
`None` for other types.

Example `engine_class.py`:
```python
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.<engine_name> import write_item


class EngineClass(base_engine.BaseEngine):
	def __init__(self, package_name: str, verbose: bool = False):
		super().__init__(package_name, verbose)
		self.write_item = write_item
		self.validate_write_item_module()

	def save_package(self, item_bank, outfile: str = None):
		item_bank.renumber_items()
		outfile = self.get_outfile_name("<engine_name>", "txt", outfile)
		assessment_items_tree = self.process_item_bank(item_bank)
		# write_item.MC must return a string for this example
		with open(outfile, "w") as f:
			for item_text in assessment_items_tree:
				f.write(item_text)
		return outfile
```

Example `write_item.py`:
```python
def MC(item_cls):
	return f"{item_cls.item_number}. {item_cls.question_text}\n"

def MA(item_cls):
	return None

def MATCH(item_cls):
	return None

def NUM(item_cls):
	return None

def FIB(item_cls):
	return None

def MULTI_FIB(item_cls):
	return None

def ORDER(item_cls):
	return None
```

Example input and output:
- Input: one `MC` item in the `ItemBank`
- Output: `get_outfile_name("<engine_name>", "txt")` creates `<engine_name>-<name>.txt`

## Read and write engine example
If the format supports reading, add `read_package.py` and implement a reader there.
Then call it from `EngineClass.read_items_from_file(...)`.
```python
from qti_package_maker.assessment_items import item_bank
from qti_package_maker.assessment_items import item_types

def read_items_from_file(input_file: str, allow_mixed: bool = False):
	new_bank = item_bank.ItemBank(allow_mixed)
	with open(input_file, "r") as f:
		for line in f:
			item_cls = read_MC(line)
			if item_cls:
				new_bank.add_item_cls(item_cls)
	return new_bank

def read_MC(line: str):
	question_text = line.strip()
	choices_list = ["A", "B"]
	answer_text = "A"
	return item_types.MC(question_text, choices_list, answer_text)
```

Example `engine_class.py` wrapper:
```python
def read_items_from_file(self, infile: str, allow_mixed: bool = False):
	return read_package.read_items_from_file(infile, allow_mixed=allow_mixed)
```

## Required functions

| Function | Required | Purpose | Inputs | Output | Common errors |
| --- | --- | --- | --- | --- | --- |
| `__init__` | Yes | load writer module, validate wiring | `package_name`, `verbose` | instance | wrong module path |
| `save_package` | Yes | write bundle or single file | `item_bank`, `outfile` | output path | wrong outfile name, non-determinism |
| `read_items_from_file` | No | read input and build ItemBank | `infile`, `allow_mixed` | `ItemBank` | mixed types rejected |

### engine_class.py
Implement `EngineClass` that subclasses `BaseEngine`. In this codebase, engines write
via `save_package()` and optionally read via `read_items_from_file()`.

Required methods:
- `__init__(self, package_name: str, verbose: bool = False)`
  - set `self.write_item` to your `write_item` module
  - call `self.validate_write_item_module()`
- `save_package(self, item_bank, outfile: str = None)`
  - iterate over `self.process_item_bank(item_bank)`
  - write outputs to a file (or ZIP) using `self.get_outfile_name(...)`
  - for bundle formats, write to a temp folder, zip the folder, then return the zip path
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
Use `None` for unsupported types, and raise only when the type is supported but invalid.

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

To verify discovery, run:
```sh
python3 -m qti_package_maker.engines.engine_registration
```

## Tips and conventions
- Use tabs for indentation in Python files. See [PYTHON_STYLE.md](PYTHON_STYLE.md).
- Keep lines around 100 characters.
- Use `BaseEngine.get_outfile_name(...)` to standardize output naming.
- Call `ItemBank.renumber_items()` before writing to keep item numbers stable.
- Reuse helpers from `qti_package_maker/common/` and existing engines.
- For HTML or XML outputs, keep formatting stable to simplify tests.
- When a format cannot support an item type, return `None` in the writer.
- Rule of thumb: keep format-specific parsing and rendering in the engine, and put
  shared helpers in `qti_package_maker/common/`.

## Item type mapping
Use these item fields when parsing or writing. Attribute names are illustrative; confirm
exact names in the item type classes.

| Item type | write_item.py function | Minimum required fields | Sample attributes |
| --- | --- | --- | --- |
| `MC` | `MC(item_cls)` | prompt, choices, correct | `item_cls.question_text`, `item_cls.choices_list`, `item_cls.answer_text` |
| `MA` | `MA(item_cls)` | prompt, choices, correct set | `item_cls.question_text`, `item_cls.choices_list`, `item_cls.answers_list` |
| `NUM` | `NUM(item_cls)` | prompt, answer, tolerance | `item_cls.question_text`, `item_cls.answer_float`, `item_cls.tolerance_float` |
| `FIB` | `FIB(item_cls)` | prompt, answers | `item_cls.question_text`, `item_cls.answers_list` |
| `MATCH` | `MATCH(item_cls)` | prompt, pairs | `item_cls.question_text`, `item_cls.prompts_list`, `item_cls.choices_list` |
| `MULTI_FIB` | `MULTI_FIB(item_cls)` | prompt, answer map | `item_cls.question_text`, `item_cls.answer_map` |
| `ORDER` | `ORDER(item_cls)` | prompt, sequence | `item_cls.question_text`, `item_cls.ordered_answers_list` |

## Output artifacts

| Output style | What `save_package()` writes | Typical formats | Gotcha |
| --- | --- | --- | --- |
| Single file | one file at outfile | text, HTML, XML | encoding and newline stability |
| Bundle | folder then zip | QTI packages | temp paths leaking into content |
| Multi-file, no zip | folder tree | dev or debug engines | test harness expecting zip |

## Testing checklist
- Add or update smoke tests in `tests/` (see `tests/test_all_engines.py`).
- For writer-only engines, add output checks in `tests/integration/test_engine_outputs.py`.
- If reading is supported, add roundtrip tests in `tests/integration/test_reader_roundtrip.py`.
- Update capability tables in [README.md](../README.md).
- Document changes in [CHANGELOG.md](CHANGELOG.md).

Target notes:
- `tests/test_all_engines.py` is the fast smoke test across all engines.
- `tests/integration/test_engine_outputs.py` checks structural validity of outputs.
- `tests/integration/test_reader_roundtrip.py` checks read then write roundtrips.

| Goal | Command | Notes |
| --- | --- | --- |
| Run all engine tests | `pytest -q tests/test_all_engines.py` | baseline smoke |
| Run only this engine | `pytest -q -k <engine_name>` | fastest loop |
| Debug a single case | `pytest -q -k <test_name> -vv` | show captured logs |
| Run roundtrip tests | `pytest -q -k roundtrip` | matches `tests/integration/test_reader_roundtrip.py` |

## Common failure modes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Engine not discovered | missing `__init__.py` or wrong import path | add `__init__.py`, verify discovery command |
| Crash on write | forgot `validate_write_item_module()` | call validator early in `__init__` |
| Flaky tests | non-deterministic ordering or whitespace | sort items and stabilize output |
| Reader rejects file | mixed types but `allow_mixed` ignored | plumb `allow_mixed` through read path |
| CRC or metadata lost | not using `add_item_cls` | rebuild `ItemBank` with `add_item_cls` |

## References
- [CODE_DESIGN.md](CODE_DESIGN.md)
- [DEVELOPMENT.md](DEVELOPMENT.md)
- `qti_package_maker/engines/template_class/`
