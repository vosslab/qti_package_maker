#!/usr/bin/env python3

"""CAM16-based color wheel scaffolding (dependency not yet wired)."""

# Standard Library
import math
import random
from dataclasses import dataclass

#====================================================================
# Wheel configuration
#====================================================================

@dataclass(frozen=True)
class WheelSpec:
	"""Policy settings for a specific wheel mode."""
	target_j: float
	m_min: float
	m_max: float
	shared_m_quantile: float
	allow_m_variation: float
	brightness_q_cap: float | None = None


DEFAULT_WHEEL_SPECS = {
	"very_dark": WheelSpec(target_j=25.0, m_min=10.0, m_max=60.0, shared_m_quantile=0.30, allow_m_variation=0.10),
	"dark": WheelSpec(target_j=40.0, m_min=8.0, m_max=50.0, shared_m_quantile=0.25, allow_m_variation=0.10),
	"light": WheelSpec(target_j=80.0, m_min=4.0, m_max=20.0, shared_m_quantile=0.20, allow_m_variation=0.05),
	"xlight": WheelSpec(target_j=88.0, m_min=3.0, m_max=16.0, shared_m_quantile=0.15, allow_m_variation=0.04),
}

DEFAULT_VIEWING = {
	"surround": "average",
	"white_point": "D65",
	"adapting_luminance": 64.0,
}

#====================================================================
# Hue layout helpers
#====================================================================

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


#====================================================================
# CAM16 conversion placeholders
#====================================================================

def cam16_jmh_to_xyz(j, m, h, viewing_conditions):
	raise NotImplementedError("CAM16 conversion requires colour-science wiring.")


def xyz_to_linear_srgb(xyz):
	raise NotImplementedError("CAM16 conversion requires colour-science wiring.")


#====================================================================
# Gamut helpers and max-M search
#====================================================================

def _linear_rgb_in_gamut(rgb, epsilon=1e-7):
	return all(-epsilon <= channel <= 1.0 + epsilon for channel in rgb)


def _quantile(values, q):
	if not values:
		return 0.0
	sorted_vals = sorted(values)
	idx = max(0, min(len(sorted_vals) - 1, int(round(q * (len(sorted_vals) - 1)))) )
	return sorted_vals[idx]


_MAX_M_CACHE = {}


def _max_m_for_hue(j, h, viewing_conditions, cache_key=None, steps=12, m_hi=100.0):
	if cache_key in _MAX_M_CACHE:
		return _MAX_M_CACHE[cache_key]

	lo = 0.0
	hi = m_hi
	for _ in range(steps):
		mid = (lo + hi) / 2.0
		xyz = cam16_jmh_to_xyz(j, mid, h, viewing_conditions)
		rgb = xyz_to_linear_srgb(xyz)
		if _linear_rgb_in_gamut(rgb):
			lo = mid
		else:
			hi = mid

	result = lo
	if cache_key is not None:
		_MAX_M_CACHE[cache_key] = result
	return result


#====================================================================
# Wheel generation (CAM16 stub)
#====================================================================

def generate_color_wheel(num_colors, mode="dark", backend="cam16"):
	if backend != "cam16":
		raise ValueError("Only cam16 backend is supported in next_gen scaffold.")

	spec = DEFAULT_WHEEL_SPECS.get(mode)
	if spec is None:
		raise ValueError(f"Unknown mode: {mode}")

	# Placeholder implementation until CAM16 wiring is added.
	raise NotImplementedError("CAM16 wheel generation is not wired yet.")


#====================================================================

def write_html_color_table(filename, num_colors=16):
	raise NotImplementedError("CAM16 wheel generation is not wired yet.")
