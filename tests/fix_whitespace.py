#!/usr/bin/env python3
import argparse
import os
import sys


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		argparse.Namespace: Parsed arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Fix whitespace issues (line endings, trailing whitespace, final newline, BOM).",
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_file",
		required=True,
		help="Input file to fix",
	)
	args = parser.parse_args()
	return args


#============================================
def read_bytes(input_file: str) -> bytes:
	"""Read file bytes.

	Args:
		input_file: Path to the file.

	Returns:
		bytes: File contents.
	"""
	with open(input_file, "rb") as handle:
		data = handle.read()
	return data


#============================================
def normalize_line_endings(data: bytes) -> bytes:
	"""Normalize CRLF and CR line endings to LF.

	Args:
		data: File bytes.

	Returns:
		bytes: Bytes with LF line endings.
	"""
	normalized = data.replace(b"\r\n", b"\n")
	normalized = normalized.replace(b"\r", b"\n")
	return normalized


#============================================
def strip_utf8_bom(data: bytes) -> tuple[bytes, bool]:
	"""Strip a UTF-8 BOM if present.

	Args:
		data: File bytes.

	Returns:
		tuple[bytes, bool]: Updated bytes and a change flag.
	"""
	bom = b"\xef\xbb\xbf"
	if data.startswith(bom):
		return data[len(bom):], True
	return data, False


#============================================
def strip_trailing_whitespace(data: bytes) -> tuple[bytes, bool]:
	"""Strip trailing spaces and tabs from each line.

	Args:
		data: File bytes with LF line endings.

	Returns:
		tuple[bytes, bool]: Updated bytes and a change flag.
	"""
	original = data
	lines = data.split(b"\n")
	fixed_lines = []
	for line in lines:
		fixed_lines.append(line.rstrip(b" \t"))
	fixed = b"\n".join(fixed_lines)
	changed = fixed != original
	return fixed, changed


#============================================
def ensure_final_newline(data: bytes) -> tuple[bytes, bool]:
	"""Ensure the file ends with a single LF if non-empty.

	Args:
		data: File bytes with LF line endings.

	Returns:
		tuple[bytes, bool]: Updated bytes and a change flag.
	"""
	if not data:
		return data, False
	if data.endswith(b"\n"):
		return data, False
	return data + b"\n", True


#============================================
def fix_whitespace_bytes(data: bytes) -> tuple[bytes, bool]:
	"""Apply whitespace fixes.

	Args:
		data: Input bytes.

	Returns:
		tuple[bytes, bool]: Updated bytes and a change flag.
	"""
	original = data

	data, _ = strip_utf8_bom(data)
	data = normalize_line_endings(data)
	data, _ = strip_trailing_whitespace(data)
	data, _ = ensure_final_newline(data)

	changed = data != original
	return data, changed


#============================================
def write_bytes(output_file: str, data: bytes) -> None:
	"""Write bytes back to a file.

	Args:
		output_file: Path to write.
		data: Bytes to write.
	"""
	with open(output_file, "wb") as handle:
		handle.write(data)


#============================================
def main() -> int:
	"""Run the whitespace fixer.

	Returns:
		int: Process exit code.
	"""
	args = parse_args()
	input_file = args.input_file

	if not os.path.isfile(input_file):
		message = f"{input_file}:0:0: file not found"
		print(message, file=sys.stderr)
		return 1

	data = read_bytes(input_file)
	fixed, changed = fix_whitespace_bytes(data)
	if changed:
		write_bytes(input_file, fixed)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
