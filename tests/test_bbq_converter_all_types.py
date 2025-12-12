#!/usr/bin/env python3

import os
import sys
import zipfile
import tempfile
import subprocess


def write_all_types_bbq_file(bbq_file: str) -> None:
	# Supported by `qti_package_maker/engines/bbq_text_upload/read_package.py`:
	# MC, MA, MAT, NUM, FIB, FIB_PLUS, ORD
	lines = [
		"MC\t2+2?\t3\tincorrect\t4\tcorrect",
		"MA\tPrime numbers?\t2\tcorrect\t3\tcorrect\t4\tincorrect\t5\tcorrect",
		"MAT\tMatch capital to country.\tUSA\tWashington\tFrance\tParis",
		"NUM\tApprox pi?\t3.14\t0.01",
		"FIB\tCapital of France?\tParis",
		"FIB_PLUS\tFill in: The [animal] has milk.\tanimal\tcow",
		"ORD\tOrder these.\tOne\tTwo\tThree",
	]
	with open(bbq_file, "w", encoding="utf-8") as f:
		for line in lines:
			f.write(line + "\n")


def assert_exists_and_nonempty(path: str) -> None:
	if not os.path.exists(path):
		raise FileNotFoundError(path)
	if os.path.getsize(path) <= 0:
		raise ValueError(f"Expected non-empty output file: {path}")


def assert_zip_has_manifest(zip_path: str) -> None:
	with zipfile.ZipFile(zip_path, "r") as zf:
		names = zf.namelist()
		if "imsmanifest.xml" not in names:
			raise ValueError(f"Missing imsmanifest.xml in {zip_path}")


def main() -> None:
	tests_dir = os.path.abspath(os.path.dirname(__file__))
	repo_root = os.path.abspath(os.path.join(tests_dir, ".."))
	converter = os.path.join(repo_root, "tools", "bbq_converter.py")

	with tempfile.TemporaryDirectory(prefix=".tmp-bbq-converter-", dir=tests_dir) as tmpdir:
		bbq_file = os.path.join(tmpdir, "bbq-alltypes-questions.txt")
		write_all_types_bbq_file(bbq_file)

		argv = [
			sys.executable,
			converter,
			"-i",
			bbq_file,
			"--all",
			"--allow-mixed",
			"--quiet",
		]
		env = os.environ.copy()
		env["PYTHONPATH"] = repo_root + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
		try:
			result = subprocess.run(
				argv,
				cwd=tmpdir,
				env=env,
				check=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
			)
		except subprocess.CalledProcessError as e:
			print(e.stdout)
			print("Files in tmpdir:")
			for name in sorted(os.listdir(tmpdir)):
				print("-", name)
			raise

		if result.stdout:
			print(result.stdout.strip())

		required_outputs = [
			os.path.join(tmpdir, "qti21-alltypes.zip"),
			os.path.join(tmpdir, "human-alltypes.html"),
			os.path.join(tmpdir, "bbq-alltypes.txt"),
			os.path.join(tmpdir, "selftest-alltypes.html"),
		]

		for outpath in required_outputs:
			assert_exists_and_nonempty(outpath)

		assert_zip_has_manifest(os.path.join(tmpdir, "qti21-alltypes.zip"))

		optional_qti12 = os.path.join(tmpdir, "qti12-alltypes.zip")
		if os.path.exists(optional_qti12):
			assert_exists_and_nonempty(optional_qti12)
			assert_zip_has_manifest(optional_qti12)


if __name__ == "__main__":
	main()
