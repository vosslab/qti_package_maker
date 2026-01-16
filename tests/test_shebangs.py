import os
import stat


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKIP_DIRS = {
	".git",
	".venv",
	"__pycache__",
	".pytest_cache",
	".mypy_cache",
	"old_shell_folder",
}
PYTHON_SHEBANG = "#!/usr/bin/env python3"


#============================================
def iter_repo_files() -> list[str]:
	"""
	Collect regular files under the repo root.

	Returns:
		list[str]: Absolute file paths.
	"""
	paths = []
	for root, dirs, files in os.walk(REPO_ROOT):
		dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
		for name in files:
			path = os.path.join(root, name)
			if os.path.islink(path):
				continue
			if not os.path.isfile(path):
				continue
			paths.append(path)
	return paths


#============================================
def read_shebang(path: str) -> str:
	"""
	Read the shebang line if present.

	Args:
		path: File path.

	Returns:
		str: Shebang line without newline, or empty string if none.
	"""
	try:
		with open(path, "rb") as handle:
			line = handle.readline(200)
	except OSError:
		return ""
	if not line.startswith(b"#!"):
		return ""
	try:
		return line.decode("utf-8").rstrip("\n")
	except UnicodeDecodeError:
		return line.decode("utf-8", errors="replace").rstrip("\n")


#============================================
def is_executable(path: str) -> bool:
	"""
	Check whether any executable bit is set on a file.

	Args:
		path: File path.

	Returns:
		bool: True if executable for user/group/other.
	"""
	try:
		mode = os.stat(path).st_mode
	except OSError:
		return False
	return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


#============================================
def categorize_errors() -> dict[str, list[str]]:
	"""
	Scan repo for shebang and executable mismatches.

	Returns:
		dict[str, list[str]]: Error categories to path lists.
	"""
	errors = {
		"shebang_not_executable": [],
		"executable_no_shebang": [],
		"python_shebang_invalid": [],
	}
	for path in iter_repo_files():
		shebang = read_shebang(path)
		exec_flag = is_executable(path)
		if shebang and not exec_flag:
			errors["shebang_not_executable"].append(path)
		if exec_flag and not shebang:
			errors["executable_no_shebang"].append(path)
		if shebang and "python" in shebang:
			if shebang != PYTHON_SHEBANG:
				errors["python_shebang_invalid"].append(path)
	return errors


#============================================
def format_errors(errors: dict[str, list[str]]) -> str:
	"""
	Format error categories for assertion output.

	Args:
		errors: Error categories and paths.

	Returns:
		str: Formatted error summary.
	"""
	lines = []
	for key in sorted(errors.keys()):
		paths = errors[key]
		if not paths:
			continue
		lines.append(f"{key}: {len(paths)}")
		for path in sorted(paths)[:10]:
			display_path = os.path.relpath(path, REPO_ROOT)
			lines.append(f"  {display_path}")
	return "\n".join(lines)


#============================================
def test_shebang_executable_alignment() -> None:
	"""
	Ensure shebangs and executable bits are aligned.
	"""
	errors = categorize_errors()
	if all(not values for values in errors.values()):
		return
	message = format_errors(errors)
	raise AssertionError(f"Shebang issues found:\n{message}")
