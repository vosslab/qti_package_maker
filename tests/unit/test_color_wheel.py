#!/usr/bin/env python3

# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import color_wheel


def test_min_difference_cases():
	assert color_wheel.min_difference([40, 41]) == 1
	assert color_wheel.min_difference([30, 15, 36]) == 6
	assert color_wheel.min_difference([84, 25, 24, 37]) == 1
	assert color_wheel.min_difference([84, 30, 30, 42, 56, 72]) == 0
