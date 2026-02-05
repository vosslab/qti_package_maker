import subprocess


#============================================
def get_repo_root() -> str:
	"""
	Get the repository root using git rev-parse --show-toplevel.

	Returns:
		str: Absolute path to the repository root.
	"""
	return subprocess.check_output(
		["git", "rev-parse", "--show-toplevel"],
		text=True,
	).strip()
