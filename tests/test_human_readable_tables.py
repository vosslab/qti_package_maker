#!/usr/bin/env python3

import os
import sys
import tempfile

# Allow running tests without installing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qti_package_maker import package_interface


def main():
	qti_packer = package_interface.QTIPackageInterface("human-table", verbose=False, allow_mixed=True)
	question_text = (
		"<p>Use the table below.</p>"
		"<table>"
		"<tr><th>Col A</th><th>Col B</th></tr>"
		"<tr><td>1</td><td>2</td></tr>"
		"</table>"
		"<p>Done.</p>"
	)
	choices_list = ["Option 1", "Option 2"]
	qti_packer.add_item("MC", (question_text, choices_list, "Option 1"))

	tests_dir = os.path.abspath(os.path.dirname(__file__))
	with tempfile.TemporaryDirectory(prefix=".tmp-human-table-", dir=tests_dir) as tmpdir:
		outfile = os.path.join(tmpdir, "human-table.html")
		qti_packer.save_package("human", outfile)

		with open(outfile, "r", encoding="utf-8") as f:
			contents = f.read()

		if "[TABLE]" in contents:
			raise ValueError("Human-readable output still contains [TABLE] placeholder")
		for required in ("Col A", "Col B", "1", "2"):
			if required not in contents:
				raise ValueError(f"Missing expected table content: {required}")


if __name__ == "__main__":
	main()

