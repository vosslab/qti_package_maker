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
	assert next_gen._redness_score("ff0000") < next_gen._redness_score("000000")


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


def test_write_html_color_table_cam16_debug(tmp_path):
	output = tmp_path / "cam16_debug.html"
	modes = ["xdark", "dark", "normal", "light", "xlight"]
	next_gen.write_html_color_table_cam16_debug(str(output), num_colors=4, modes=modes)
	content = output.read_text()
	assert "CAM16 Debug" in content
	for mode in modes:
		assert f"<h1>{mode}" in content
	assert "target J" in content
	assert "XKCD Name" in content
	assert "UCS_r" in content
	assert "gamut_margin" in content
	assert "M_max_hue" in content


def test_cam16_j_m_q_ranges():
	num_colors = 8
	for mode, spec in next_gen.DEFAULT_WHEEL_SPECS.items():
		hues = next_gen._generate_hues_equal(num_colors, offset=0.0)
		colors = next_gen.generate_color_wheel(
			num_colors,
			mode=mode,
			hues=hues,
			rotate_to_anchor=False,
			apply_variation=False,
		)

		for hue, hex_value in zip(hues, colors):
			cam = next_gen._srgb_hex_to_cam16_spec(hex_value)
			assert abs(cam.J - spec.target_j) <= 5.0

			max_m = next_gen._max_m_for_hue(
				spec.target_j,
				hue,
				cache_key=(mode, round(spec.target_j, 2), round(hue, 1)),
			)
			min_expected = min(spec.m_min, max_m)
			max_expected = min(spec.m_max, max_m)
			assert cam.M >= (min_expected - 2.0)
			assert cam.M <= (max_expected + 2.0)

			assert cam.Q > 0.0
			assert cam.Q < 260.0
