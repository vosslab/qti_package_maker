#!/usr/bin/env python3

# Standard Library
import re

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import color_wheel_next_gen


HEX_RE = re.compile(r"^[0-9a-f]{6}$")


def _hex_list_is_valid(hex_list):
	return all(HEX_RE.match(value) for value in hex_list)


def test_oklch_color_wheel_returns_hex():
	colors = color_wheel_next_gen.oklch_color_wheel(8, category="dark")
	assert len(colors) == 8
	assert _hex_list_is_valid(colors)


def test_oklch_color_wheel_supports_very_dark():
	colors = color_wheel_next_gen.oklch_color_wheel(5, category="very_dark")
	assert len(colors) == 5
	assert _hex_list_is_valid(colors)


def test_oklch_all_color_wheels_lengths_and_hex():
	extra_light, light, dark = color_wheel_next_gen.oklch_all_color_wheels(10)
	assert len(extra_light) == 10
	assert len(light) == 10
	assert len(dark) == 10
	assert _hex_list_is_valid(extra_light)
	assert _hex_list_is_valid(light)
	assert _hex_list_is_valid(dark)


def test_generate_hues_even_spacing():
	hues = color_wheel_next_gen._generate_hues(6, anchor_hue=0.0)
	step = 360.0 / 6.0
	hues_sorted = sorted(hues)
	diffs = [
		hues_sorted[i + 1] - hues_sorted[i]
		for i in range(len(hues_sorted) - 1)
	]
	diffs.append((hues_sorted[0] + 360.0) - hues_sorted[-1])
	assert all(abs(diff - step) < 1e-6 for diff in diffs)


def test_generate_hues_anchor_sets_first_hue():
	anchor = color_wheel_next_gen.TRUE_RED_HUE
	hues = color_wheel_next_gen._generate_hues(8, anchor_hue=anchor)
	assert abs(hues[0] - anchor) < 1e-9


def test_max_chroma_is_in_gamut():
	l = color_wheel_next_gen.DEFAULT_LIGHTNESS["light"]
	h = 42.0
	c = color_wheel_next_gen._max_chroma_for_hue_lightness(l, h)
	assert c >= 0.0
	assert color_wheel_next_gen._oklch_in_gamut(l, c, h)


def test_uniform_chroma_is_in_gamut_for_all_hues():
	hues = color_wheel_next_gen._generate_hues(12)
	l = color_wheel_next_gen.DEFAULT_LIGHTNESS["light"]
	uniform_c = color_wheel_next_gen._uniform_chroma_for_hues(hues, l)
	assert uniform_c >= 0.0
	assert all(color_wheel_next_gen._oklch_in_gamut(l, uniform_c, h) for h in hues)


def test_uniform_chroma_not_exceed_max_for_any_hue():
	hues = color_wheel_next_gen._generate_hues(10)
	l = color_wheel_next_gen.DEFAULT_LIGHTNESS["dark"]
	uniform_c = color_wheel_next_gen._uniform_chroma_for_hues(hues, l)
	max_chromas = color_wheel_next_gen._max_chroma_for_hues(hues, l)
	assert all(uniform_c <= max_c + 1e-9 for max_c in max_chromas)


def test_blend_chroma_between_uniform_and_max():
	hues = color_wheel_next_gen._generate_hues(8, anchor_hue=0.0)
	l = color_wheel_next_gen.DEFAULT_LIGHTNESS["dark"]
	uniform_c = color_wheel_next_gen._uniform_chroma_for_hues(hues, l)
	max_chromas = color_wheel_next_gen._max_chroma_for_hues(hues, l)
	blend = 0.55
	blend_gamma = 1.6
	colors = color_wheel_next_gen._oklch_wheel_for_hues(
		hues,
		l,
		chroma_mode="blend",
		blend=blend,
		blend_gamma=blend_gamma,
	)
	assert len(colors) == len(hues)
	max_global = max(max_chromas)
	for max_c in max_chromas:
		if max_global <= uniform_c:
			c = uniform_c
		else:
			ratio = (max_c - uniform_c) / (max_global - uniform_c)
			ratio = max(0.0, ratio) ** blend_gamma
			c = uniform_c + blend * ratio * (max_global - uniform_c)
		assert uniform_c - 1e-9 <= c <= max_c + 1e-9


def test_hue_balance_caps_to_max_chroma():
	hue = color_wheel_next_gen.TRUE_YELLOW_HUE
	light = color_wheel_next_gen.DEFAULT_LIGHTNESS["light"]
	dark = color_wheel_next_gen.DEFAULT_LIGHTNESS["dark"]
	max_c = 0.2
	c_light = color_wheel_next_gen._apply_hue_balance(0.15, hue, light, max_c)
	c_dark = color_wheel_next_gen._apply_hue_balance(0.15, hue, dark, max_c)
	assert c_light <= max_c + 1e-9
	assert c_dark <= max_c + 1e-9


def test_write_html_color_table(tmp_path):
	filename = tmp_path / "color_table_next_gen.html"
	color_wheel_next_gen.write_html_color_table(str(filename), num_colors=6)
	assert filename.exists()
	assert "<table>" in filename.read_text()
