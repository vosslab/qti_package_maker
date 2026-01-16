import os
import subprocess


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


#============================================
def list_tracked_python_files() -> list[str]:
	"""
	List tracked Python files in the repo.

	Returns:
		list[str]: Absolute paths to tracked .py files.
	"""
	result = subprocess.run(
		["git", "-C", REPO_ROOT, "ls-files", "--", "*.py"],
		capture_output=True,
		text=True,
	)
	if result.returncode != 0:
		message = result.stderr.strip() or "Failed to list tracked Python files."
		raise RuntimeError(message)
	paths = []
	for line in result.stdout.splitlines():
		if not line:
			continue
		if line.startswith("old_shell_folder/"):
			continue
		paths.append(os.path.join(REPO_ROOT, line))
	return paths


#============================================
def inspect_file(path: str) -> tuple[int | None, int | None, list[int]]:
	"""
	Check a file for tab/space indentation usage.

	Args:
		path: File path.

	Returns:
		tuple[int | None, int | None, list[int]]: First tab line, first space line,
			and line numbers with mixed indentation.
	"""
	first_tab_line = None
	first_space_line = None
	mixed_lines = []
	with open(path, "r", encoding="utf-8", errors="replace") as handle:
		for line_number, line in enumerate(handle, 1):
			stripped = line.lstrip(" \t")
			if stripped.strip() == "":
				continue
			indent = line[:len(line) - len(stripped)]
			if not indent:
				continue
			if "\t" in indent and " " in indent:
				mixed_lines.append(line_number)
				continue
			if indent.startswith("\t"):
				if first_tab_line is None:
					first_tab_line = line_number
			elif indent.startswith(" "):
				if first_space_line is None:
					first_space_line = line_number
	return first_tab_line, first_space_line, mixed_lines


#============================================
def test_indentation_style() -> None:
	"""
	Fail on mixed indentation across or within a file.
	"""
	errors = []
	for path in sorted(list_tracked_python_files()):
		first_tab_line, first_space_line, mixed_lines = inspect_file(path)
		if mixed_lines:
			display_path = os.path.relpath(path, REPO_ROOT)
			for line_number in mixed_lines[:3]:
				errors.append(f"{display_path}:{line_number}: mixed indent within line")
			continue
		if first_tab_line and first_space_line:
			display_path = os.path.relpath(path, REPO_ROOT)
			errors.append(
				f"{display_path}: tabs and spaces in file "
				f"(tab line {first_tab_line}, space line {first_space_line})"
			)
	if errors:
		message = "\n".join(errors)
		raise AssertionError(f"Indentation issues found:\n{message}")
