#!/usr/bin/env python3

"""Hue layout helpers."""

# Standard Library
import random


def _generate_hues_equal(num_colors, offset=0.0):
	step = 360.0 / float(num_colors)
	return [(offset + step * i) % 360.0 for i in range(num_colors)]


def _generate_hues_anchor(num_colors, anchor_hue):
	return _generate_hues_equal(num_colors, offset=anchor_hue)


def _generate_hues_offset(num_colors):
	offset = random.random() * 360.0
	return _generate_hues_equal(num_colors, offset=offset)


def _generate_hues_optimized(num_colors, score_fn, samples=24):
	best_offset = None
	best_score = None
	for _ in range(samples):
		offset = random.random() * 360.0
		hues = _generate_hues_equal(num_colors, offset=offset)
		score = score_fn(hues)
		if best_score is None or score > best_score:
			best_score = score
			best_offset = offset
	return _generate_hues_equal(num_colors, offset=best_offset or 0.0)
