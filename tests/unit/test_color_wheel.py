#!/usr/bin/env python3

# Standard Library
import random
import re

# Pip3 Library
import pytest

# QTI Package Maker
from qti_package_maker.common import color_wheel


def test_min_difference_cases():
	assert color_wheel.min_difference([40, 41]) == 1
	assert color_wheel.min_difference([30, 15, 36]) == 6
	assert color_wheel.min_difference([84, 25, 24, 37]) == 1
	assert color_wheel.min_difference([84, 30, 30, 42, 56, 72]) == 0


def test_facade_legacy_backend_matches_legacy():
	random.seed(0)
	legacy_colors = color_wheel.default_color_wheel(5)
	random.seed(0)
	facade_colors = color_wheel.generate_color_wheel(5, backend="legacy")
	assert facade_colors == legacy_colors


def test_cam16_backend_returns_hex():
	random.seed(0)
	colors = color_wheel.generate_color_wheel(3, backend="cam16", mode="dark")
	assert len(colors) == 3
	assert all(re.match(r"^[0-9a-f]{6}$", value) for value in colors)

	def red_score(hex_value):
		r = int(hex_value[0:2], 16)
		g = int(hex_value[2:4], 16)
		b = int(hex_value[4:6], 16)
		gb = g + b
		gb_balance = abs(g - b) / (gb + 1e-6)
		gb_over_2r = gb / (2.0 * r + 1e-6)
		return (gb_balance + gb_over_2r, gb_balance, gb_over_2r, -r)

	scores = [red_score(value) for value in colors]
	assert scores[0] == min(scores)
