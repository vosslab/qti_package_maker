import os
import shutil
import subprocess


SKIP_ENV = "SKIP_REPO_HYGIENE"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKIP_DIRS = [".git", ".venv", "old_shell_folder"]


#============================================
def bandit_exclude_arg() -> str:
	"""
	Build the bandit exclude argument.
	"""
	value = ",".join(SKIP_DIRS)
	return value


#============================================
def run_bandit(repo_root: str) -> tuple[int, str]:
	"""
	Run bandit recursively and return (exit_code, combined_output).
	"""
	bandit_bin = shutil.which("bandit")
	if not bandit_bin:
		raise AssertionError("bandit not found on PATH.")
	command = [
		bandit_bin,
		"-r",
		repo_root,
		"--severity-level",
		"medium",
		"-x",
		bandit_exclude_arg(),
	]
	result = subprocess.run(
		command,
		capture_output=True,
		text=True,
		cwd=repo_root,
	)
	output = result.stdout + result.stderr
	return (result.returncode, output)


#============================================
def test_bandit_security() -> None:
	"""
	Run bandit at severity medium or higher.
	"""
	if os.environ.get(SKIP_ENV) == "1":
		return

	# Delete old report file before running
	bandit_out = os.path.join(REPO_ROOT, "report_bandit.txt")
	if os.path.exists(bandit_out):
		os.remove(bandit_out)

	exit_code, output = run_bandit(REPO_ROOT)
	if exit_code == 0:
		return

	with open(bandit_out, "w", encoding="utf-8") as handle:
		handle.write(output)

	raise AssertionError("Bandit issues detected. See REPO_ROOT/report_bandit.txt")
