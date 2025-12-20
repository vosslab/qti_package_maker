# Troubleshooting

## Install or import errors
- Ensure dependencies are installed: `pip install -r requirements.txt`.
- If running scripts directly, use `source source_me_for_testing.sh` to set
  `PYTHONPATH`.
- If engine discovery fails, verify the package is importable:
  `python3 -m qti_package_maker.engines.engine_registration`.

## BBQ parse issues
- BBQ files must be tab-delimited, have no header row, and contain one question per
  line.
- Blank lines or embedded newlines in questions will cause parsing errors.
- Use `--allow-mixed` (CLI) or `allow_mixed=True` (API) for mixed question types.

## Empty output or missing items
- If an output is empty, confirm the input file was read and yielded items.
- Try a small sample file and increase `--limit` to isolate a bad row.

## HTML tables in question text
- Tables are converted to plain text when possible.
- If you see `[TABLE]`, the HTML may be malformed; verify `<table>` tags are
  well-formed.

## HTML self-test styling
- The HTML self-test output uses inline styles and helper functions in
  `qti_package_maker/engines/html_selftest/html_functions.py`.
- For styling changes (including dark mode), update those helpers and regenerate output.
