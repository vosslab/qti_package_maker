#!/usr/bin/env python3

# Standard Library
import re

# QTI Package Maker
from qti_package_maker.common.color_theory import next_gen


def test_generate_color_wheel_returns_hex():
	colors = next_gen.generate_color_wheel(4, mode="dark")
	assert len(colors) == 4
	assert all(re.match(r"^[0-9a-f]{6}$", value) for value in colors)


def test_redness_score_prefers_red():
	assert next_gen._redness_score("ff0000") < next_gen._redness_score("0000ff")


def test_write_html_color_table(tmp_path):
	output = tmp_path / "next_gen_table.html"
	next_gen.write_html_color_table(str(output), num_colors=4, modes=["dark", "light", "xlight"])
	content = output.read_text()
	assert "Color Name" in content
	assert "White / Dark" in content


def test_write_red_scan_bundle_html(tmp_path):
	output = tmp_path / "red_scan.html"
	next_gen._write_red_scan_bundle_html(str(output), num_colors=4, modes=["dark", "light"])
	content = output.read_text()
	assert "<h1>dark</h1>" in content
	assert "Step 0.2 (micro)" in content
