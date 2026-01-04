#!/usr/bin/env python3

"""Small RGB/hex helpers for color wheel tooling."""


def _srgb_to_hex(rgb):
	clamped = [min(max(channel, 0.0), 1.0) for channel in rgb]
	values = [int(round(channel * 255)) for channel in clamped]
	return "{:02x}{:02x}{:02x}".format(values[0], values[1], values[2])


def _hex_to_rgb(hex_value):
	return (int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16))


def _rgb_distance(hex_a, hex_b):
	r1, g1, b1 = _hex_to_rgb(hex_a)
	r2, g2, b2 = _hex_to_rgb(hex_b)
	return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
