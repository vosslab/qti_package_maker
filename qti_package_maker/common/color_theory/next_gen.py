#!/usr/bin/env python3

"""CAM16-based color wheel generator using colour-science."""

# Standard Library
import argparse
import random
import sys
import types
from dataclasses import dataclass
from typing import Optional

# QTI Package Maker
from qti_package_maker.common.color_theory import rgb_color_name_match

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
	max_m_blend: float = 0.0
	brightness_q_cap: Optional[float] = None


DEFAULT_WHEEL_SPECS = {
	"very_dark": WheelSpec(target_j=25.0, m_min=20.0, m_max=90.0, shared_m_quantile=0.45, allow_m_variation=0.18, max_m_blend=0.45),
	"xdark": WheelSpec(target_j=20.0, m_min=22.0, m_max=95.0, shared_m_quantile=0.50, allow_m_variation=0.18, max_m_blend=0.50),
	"dark": WheelSpec(target_j=38.0, m_min=18.0, m_max=85.0, shared_m_quantile=0.40, allow_m_variation=0.15, max_m_blend=0.40),
	"normal": WheelSpec(target_j=62.0, m_min=8.0, m_max=45.0, shared_m_quantile=0.25, allow_m_variation=0.08, max_m_blend=0.25),
	"light": WheelSpec(target_j=82.0, m_min=1.5, m_max=10.0, shared_m_quantile=0.12, allow_m_variation=0.03, max_m_blend=0.15),
	"xlight": WheelSpec(target_j=90.0, m_min=1.0, m_max=8.0, shared_m_quantile=0.08, allow_m_variation=0.02, max_m_blend=0.10),
}

DEFAULT_VIEWING = {
	"surround": "Average",
	"white_point": "D65",
	"adapting_luminance": 64.0,
	"background_luminance": 20.0,
}

_VIEWING_CACHE = None
_MAX_M_CACHE = {}
_BEST_RED_OFFSETS = {
	("xdark", 16, "ff0000"): 27.2,
	("dark", 16, "ff0000"): 25.4,
	("normal", 16, "ff0000"): 19.2,
	("light", 16, "ff0000"): 23.0,
	("xlight", 16, "ff0000"): 17.0,
}

#====================================================================
# Dependency adapter
#====================================================================

def _block_pandas_import():
	try:
		import pandas  # noqa: F401
	except Exception:
		sys.modules["pandas"] = None


_block_pandas_import()
if "colour.plotting" not in sys.modules:
	sys.modules["colour.plotting"] = types.ModuleType("colour.plotting")

# Third Party
import colour


#====================================================================
# Viewing conditions
#====================================================================

def _get_viewing_conditions():
	global _VIEWING_CACHE
	if _VIEWING_CACHE is not None:
		return _VIEWING_CACHE

	xy_w = colour.CCS_ILLUMINANTS["CIE 1931 2 Degree Standard Observer"][DEFAULT_VIEWING["white_point"]]
	XYZ_w = colour.xy_to_XYZ(xy_w) * 100.0
	surround = colour.VIEWING_CONDITIONS_CAM16[DEFAULT_VIEWING["surround"]]
	_VIEWING_CACHE = (XYZ_w, DEFAULT_VIEWING["adapting_luminance"], DEFAULT_VIEWING["background_luminance"], surround, xy_w)
	return _VIEWING_CACHE


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
# CAM16 conversions
#====================================================================

def cam16_jmh_to_xyz(j, m, h, viewing_conditions=None):
	XYZ_w, L_A, Y_b, surround, _xy_w = _get_viewing_conditions()
	if viewing_conditions:
		XYZ_w = viewing_conditions.get("XYZ_w", XYZ_w)
		L_A = viewing_conditions.get("L_A", L_A)
		Y_b = viewing_conditions.get("Y_b", Y_b)
		surround = viewing_conditions.get("surround", surround)

	spec = colour.CAM_Specification_CAM16(J=j, M=m, h=h)
	return colour.CAM16_to_XYZ(spec, XYZ_w, L_A, Y_b, surround)


def _xyz_to_srgb(XYZ, apply_encoding=True):
	_xyz = [value / 100.0 for value in XYZ]
	_xyz_w, _L_A, _Y_b, _surround, xy_w = _get_viewing_conditions()
	try:
		return colour.XYZ_to_sRGB(
			_xyz,
			illuminant=xy_w,
			chromatic_adaptation_transform=None,
			apply_cctf_encoding=apply_encoding,
		)
	except TypeError:
		return colour.XYZ_to_sRGB(
			_xyz,
			illuminant=xy_w,
			chromatic_adaptation_transform=None,
			apply_encoding_cctf=apply_encoding,
		)


def _linear_rgb_in_gamut(rgb, epsilon=1e-7):
	return all(-epsilon <= channel <= 1.0 + epsilon for channel in rgb)


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


def _resolve_anchor_hex(anchor_hex):
	if anchor_hex:
		if anchor_hex == "legacy":
			try:
				from qti_package_maker.common.color_theory import legacy_color_wheel
			except Exception:
				return "ff0000"
			return legacy_color_wheel.dark_color_wheel["red"]
		return anchor_hex.lower()
	return "ff0000"


def _anchor_cam16_hue(anchor_hex):
	anchor_rgb = _hex_to_rgb(_resolve_anchor_hex(anchor_hex))
	rgb = [value / 255.0 for value in anchor_rgb]
	rgb_colourspace = colour.RGB_COLOURSPACES["sRGB"]
	XYZ = colour.RGB_to_XYZ(rgb, rgb_colourspace, apply_cctf_decoding=True) * 100.0
	XYZ_w, L_A, Y_b, surround, _xy_w = _get_viewing_conditions()
	spec = colour.XYZ_to_CAM16(XYZ, XYZ_w, L_A, Y_b, surround)
	return float(spec.h)


def _redness_score(hex_value):
	r, g, b = _hex_to_rgb(hex_value)
	gb = g + b
	gb_balance = abs(g - b) / (gb + 1e-6)
	gb_over_2r = gb / (2.0 * r + 1e-6)
	return (gb_balance + gb_over_2r, gb_balance, gb_over_2r, -r)


def _rotate_colors_to_target(colors, target_hex):
	if not colors:
		return colors
	target_hex = _resolve_anchor_hex(target_hex)
	if target_hex == "ff0000":
		red_index = min(range(len(colors)), key=lambda idx: _redness_score(colors[idx]))
	else:
		red_index = min(range(len(colors)), key=lambda idx: _rgb_distance(colors[idx], target_hex))
	if red_index == 0:
		return colors
	return colors[red_index:] + colors[:red_index]


def _print_legacy_red_comparison(dark_hex, light_hex, extra_light_hex):
	try:
		from qti_package_maker.common.color_theory import legacy_color_wheel
	except Exception:
		print("Legacy red RGB distance: unavailable (package import failed)")
		return

	legacy_dark = legacy_color_wheel.dark_color_wheel["red"]
	legacy_light = legacy_color_wheel.light_color_wheel["red"]
	legacy_extra_light = legacy_color_wheel.extra_light_color_wheel["red"]

	print("Legacy red RGB distance:")
	print(f"- dark: {legacy_dark} -> {dark_hex} (diff {_rgb_distance(legacy_dark, dark_hex):.1f})")
	print(f"- light: {legacy_light} -> {light_hex} (diff {_rgb_distance(legacy_light, light_hex):.1f})")
	print(f"- extra light: {legacy_extra_light} -> {extra_light_hex} (diff {_rgb_distance(legacy_extra_light, extra_light_hex):.1f})")


def _render_red_scan_tables(num_colors=16, mode="dark"):
	spec = DEFAULT_WHEEL_SPECS.get(mode)
	if spec is None:
		raise ValueError(f"Unknown mode: {mode}")

	def rows_for_offsets(offsets):
		rows = []
		for offset in offsets:
			hues = _generate_hues_equal(num_colors, offset=offset)
			color_hex = _color_for_hue(hues[0], spec, mode, m_override=spec.m_max)
			rows.append((offset, color_hex, _redness_score(color_hex)))
		return rows

	coarse_step = 5.0
	fine_step = 1.0
	micro_step = 0.2

	coarse_offsets = [i for i in range(0, 360, int(coarse_step))]
	coarse_rows = rows_for_offsets(coarse_offsets)
	coarse_ranked = sorted(coarse_rows, key=lambda x: x[2])
	best_coarse = coarse_ranked[0][0]

	fine_offsets = [best_coarse + d for d in range(-int(coarse_step), int(coarse_step) + 1, int(fine_step))]
	fine_offsets = [o % 360 for o in fine_offsets]
	fine_rows = rows_for_offsets(fine_offsets)
	fine_ranked = sorted(fine_rows, key=lambda x: x[2])
	fine_top = [row[0] for row in fine_ranked[:3]]

	micro_offsets = []
	step_count = int(round(1.0 / micro_step))
	for base in fine_top:
		for i in range(-step_count, step_count + 1):
			micro_offsets.append((base + i * micro_step) % 360.0)
	micro_offsets = sorted(set(micro_offsets))
	micro_rows = rows_for_offsets(micro_offsets)
	micro_ranked = sorted(micro_rows, key=lambda x: x[2])

	parts = []
	parts.append("<h2>Step 5 (coarse)</h2><table><tr><th>Offset</th><th>Color</th><th>Hex</th><th>Sum</th><th>|G-B|/(G+B)</th><th>(G+B)/(2R)</th></tr>\n")
	for offset, color_hex, score in coarse_ranked:
		total = score[0]
		gb_balance = score[1]
		gb_over_2r = score[2]
		parts.append("<tr>")
		parts.append(f"<td>{offset:.1f}</td>")
		parts.append(_generate_table_td(color_hex, "000000", ""))
		parts.append(f"<td>{color_hex}</td>")
		parts.append(f"<td>{total:.3f}</td>")
		parts.append(f"<td>{gb_balance:.3f}</td>")
		parts.append(f"<td>{gb_over_2r:.3f}</td>")
		parts.append("</tr>\n")
	parts.append("</table>")

	parts.append("<h2>Step 1 (refine)</h2><table><tr><th>Offset</th><th>Color</th><th>Hex</th><th>Sum</th><th>|G-B|/(G+B)</th><th>(G+B)/(2R)</th></tr>\n")
	for offset, color_hex, score in fine_ranked:
		total = score[0]
		gb_balance = score[1]
		gb_over_2r = score[2]
		parts.append("<tr>")
		parts.append(f"<td>{offset:.1f}</td>")
		parts.append(_generate_table_td(color_hex, "000000", ""))
		parts.append(f"<td>{color_hex}</td>")
		parts.append(f"<td>{total:.3f}</td>")
		parts.append(f"<td>{gb_balance:.3f}</td>")
		parts.append(f"<td>{gb_over_2r:.3f}</td>")
		parts.append("</tr>\n")
	parts.append("</table>")

	parts.append("<h2>Step 0.2 (micro)</h2><table><tr><th>Offset</th><th>Color</th><th>Hex</th><th>Sum</th><th>|G-B|/(G+B)</th><th>(G+B)/(2R)</th></tr>\n")
	for offset, color_hex, score in micro_ranked:
		total = score[0]
		gb_balance = score[1]
		gb_over_2r = score[2]
		parts.append("<tr>")
		parts.append(f"<td>{offset:.1f}</td>")
		parts.append(_generate_table_td(color_hex, "000000", ""))
		parts.append(f"<td>{color_hex}</td>")
		parts.append(f"<td>{total:.3f}</td>")
		parts.append(f"<td>{gb_balance:.3f}</td>")
		parts.append(f"<td>{gb_over_2r:.3f}</td>")
		parts.append("</tr>\n")
	parts.append("</table>")

	return "".join(parts)


def _write_red_scan_html(filename, num_colors=16, mode="dark"):
	with open(filename, "w") as f:
		f.write("<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>Red Scan</title>"
				"<style>table {width: 100%; border-collapse: collapse; text-align: center;} "
				"th, td {padding: 8px; border: 1px solid black;} "
				"th {background-color: #333; color: white;} "
				"</style></head><body>")
		f.write(_render_red_scan_tables(num_colors=num_colors, mode=mode))
		f.write("</body></html>")

	print(f"Red scan table saved as {filename}")


def _write_red_scan_bundle_html(filename, num_colors=16, modes=None):
	if modes is None:
		modes = ["xdark", "dark", "normal", "light", "xlight"]

	with open(filename, "w") as f:
		f.write("<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>Red Scan</title>"
				"<style>table {width: 100%; border-collapse: collapse; text-align: center;} "
				"th, td {padding: 8px; border: 1px solid black;} "
				"th {background-color: #333; color: white;} "
				"</style></head><body>")
		for mode in modes:
			f.write(f"<h1>{mode}</h1>")
			f.write(_render_red_scan_tables(num_colors=num_colors, mode=mode))
		f.write("</body></html>")

	print(f"Red scan bundle saved as {filename}")


#====================================================================
# Hue selection helpers
#====================================================================

def _best_red_offset(
	num_colors,
	mode,
	anchor_hex,
	wheel_specs=None,
	coarse_step=5.0,
	fine_step=1.0,
	micro_step=0.2,
	top_k=3,
):
	specs = wheel_specs or DEFAULT_WHEEL_SPECS
	spec = specs.get(mode)
	if spec is None:
		raise ValueError(f"Unknown mode: {mode}")

	def score_offset(offset):
		hues = _generate_hues_equal(num_colors, offset=offset)
		color_hex = _color_for_hue(hues[0], spec, mode, m_override=spec.m_max)
		return _redness_score(color_hex)

	coarse_offsets = [i for i in range(0, 360, int(coarse_step))]
	coarse_ranked = sorted(((score_offset(o), o) for o in coarse_offsets), key=lambda x: x[0])
	best_coarse = coarse_ranked[0][1]

	fine_offsets = [best_coarse + d for d in range(-int(coarse_step), int(coarse_step) + 1, int(fine_step))]
	fine_ranked = sorted(((score_offset(o % 360), o % 360) for o in fine_offsets), key=lambda x: x[0])
	fine_top = [o for _s, o in fine_ranked[:top_k]]

	micro_offsets = []
	for base in fine_top:
		step_count = int(round(1.0 / micro_step))
		for i in range(-step_count, step_count + 1):
			micro_offsets.append((base + i * micro_step) % 360.0)

	micro_ranked = sorted(((score_offset(o), o) for o in micro_offsets), key=lambda x: x[0])
	return micro_ranked[0][1]


def _select_hues_for_anchor(num_colors, mode, anchor_hex, samples=48, wheel_specs=None):
	specs = wheel_specs or DEFAULT_WHEEL_SPECS
	spec = specs.get(mode)
	if spec is None:
		raise ValueError(f"Unknown mode: {mode}")

	cache_key = (mode, num_colors, _resolve_anchor_hex(anchor_hex))
	if cache_key not in _BEST_RED_OFFSETS:
		_BEST_RED_OFFSETS[cache_key] = _best_red_offset(num_colors, mode, anchor_hex, wheel_specs=specs)

	best_offset = _BEST_RED_OFFSETS[cache_key]
	return _generate_hues_equal(num_colors, offset=best_offset)


#====================================================================
# Max-M search and quantile
#====================================================================

def _quantile(values, q):
	if not values:
		return 0.0
	sorted_vals = sorted(values)
	index = max(0, min(len(sorted_vals) - 1, int(round(q * (len(sorted_vals) - 1)))))
	return sorted_vals[index]


def _max_m_for_hue(j, h, steps=12, m_hi=100.0, cache_key=None):
	if cache_key in _MAX_M_CACHE:
		return _MAX_M_CACHE[cache_key]

	lo = 0.0
	hi = m_hi
	for _ in range(steps):
		mid = (lo + hi) / 2.0
		XYZ = cam16_jmh_to_xyz(j, mid, h)
		rgb = _xyz_to_srgb(XYZ, apply_encoding=False)
		if _linear_rgb_in_gamut(rgb):
			lo = mid
		else:
			hi = mid

	result = lo
	if cache_key is not None:
		_MAX_M_CACHE[cache_key] = result
	return result


def _colors_for_hues(hues, spec, mode, apply_variation=True):
	max_ms = []
	for hue in hues:
		cache_key = (mode, round(spec.target_j, 2), round(hue, 1))
		max_ms.append(_max_m_for_hue(spec.target_j, hue, cache_key=cache_key))

	shared_m = _quantile(max_ms, spec.shared_m_quantile)
	shared_m = max(spec.m_min, min(spec.m_max, shared_m))

	colors = []
	for hue, max_m in zip(hues, max_ms):
		m = shared_m
		if spec.max_m_blend > 0:
			m = shared_m + (max_m - shared_m) * spec.max_m_blend
		if apply_variation and spec.allow_m_variation > 0:
			variation = (random.random() * 2.0 - 1.0) * spec.allow_m_variation * shared_m
			m = m + variation

		m = max(spec.m_min, min(spec.m_max, m))
		m = min(m, max_m)

		XYZ = cam16_jmh_to_xyz(spec.target_j, m, hue)
		rgb = _xyz_to_srgb(XYZ, apply_encoding=True)
		colors.append(_srgb_to_hex(rgb))

	return colors


def _color_for_hue(hue, spec, mode, m_override=None):
	cache_key = (mode, round(spec.target_j, 2), round(hue, 1))
	max_m = _max_m_for_hue(spec.target_j, hue, cache_key=cache_key)
	if m_override is None:
		m = min(spec.m_max, max_m)
	else:
		m = min(m_override, max_m)

	m = max(spec.m_min, min(spec.m_max, m))
	XYZ = cam16_jmh_to_xyz(spec.target_j, m, hue)
	rgb = _xyz_to_srgb(XYZ, apply_encoding=True)
	return _srgb_to_hex(rgb)


#====================================================================
# Wheel generation (CAM16)
#====================================================================

def generate_color_wheel(
	num_colors,
	mode="dark",
	hue_layout="offset",
	anchor_hue=0.0,
	samples=24,
	wheel_specs=None,
	anchor_hex=None,
	hues=None,
	apply_variation=True,
	rotate_to_anchor=True,
):
	if num_colors <= 0:
		raise ValueError("num_colors must be positive")

	specs = wheel_specs or DEFAULT_WHEEL_SPECS
	spec = specs.get(mode)
	if spec is None:
		raise ValueError(f"Unknown mode: {mode}")

	if hues is None:
		if hue_layout == "anchor":
			hues = _generate_hues_anchor(num_colors, anchor_hue)
		elif hue_layout == "optimize":
			def _score(hues_list):
				values = [
					_max_m_for_hue(spec.target_j, hue, cache_key=(mode, round(spec.target_j, 2), round(hue, 1)))
					for hue in hues_list
				]
				return _quantile(values, spec.shared_m_quantile)
			hues = _generate_hues_optimized(num_colors, _score, samples=samples)
		else:
			hues = _generate_hues_offset(num_colors)

	colors = _colors_for_hues(hues, spec, mode, apply_variation=apply_variation)

	if rotate_to_anchor:
		return _rotate_colors_to_target(colors, anchor_hex)
	return colors


#====================================================================
# HTML output for manual evaluation
#====================================================================

def _generate_table_td(bg_hex_color, text_hex_color, text="this is a test"):
	td_cell = ''
	td_cell += f"<td style='background-color:#{bg_hex_color};'>"
	td_cell += f"<span style='color:#{text_hex_color};'>{text}</span></td>\n"
	return td_cell


def write_html_color_table(filename, num_colors=16, modes=None):
	if modes is None:
		modes = ["dark", "light", "xlight"]

	dark_mode = modes[0] if len(modes) > 0 else "dark"
	light_mode = modes[1] if len(modes) > 1 else "light"
	extra_light_mode = modes[2] if len(modes) > 2 else "xlight"

	anchor_hex = _resolve_anchor_hex(None)
	hues = _select_hues_for_anchor(num_colors, dark_mode, anchor_hex, samples=48)

	dark_wheel = generate_color_wheel(num_colors, mode=dark_mode, hues=hues, rotate_to_anchor=False)
	light_wheel = generate_color_wheel(num_colors, mode=light_mode, hues=hues, rotate_to_anchor=False)
	extra_light_wheel = generate_color_wheel(num_colors, mode=extra_light_mode, hues=hues, rotate_to_anchor=False)
	dark_spec = DEFAULT_WHEEL_SPECS.get(dark_mode)
	light_spec = DEFAULT_WHEEL_SPECS.get(light_mode)
	extra_light_spec = DEFAULT_WHEEL_SPECS.get(extra_light_mode)
	if dark_spec is not None and dark_wheel:
		dark_wheel[0] = _color_for_hue(hues[0], dark_spec, dark_mode, m_override=dark_spec.m_max)
	if light_spec is not None and light_wheel:
		light_wheel[0] = _color_for_hue(hues[0], light_spec, light_mode, m_override=light_spec.m_max)
	if extra_light_spec is not None and extra_light_wheel:
		extra_light_wheel[0] = _color_for_hue(hues[0], extra_light_spec, extra_light_mode, m_override=extra_light_spec.m_max)

	with open(filename, 'w') as f:
		f.write("<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>Color Table</title>"
				"<style>table {width: 100%; border-collapse: collapse; text-align: center;} "
				"th, td {padding: 10px; border: 1px solid black;} "
				"th {background-color: #333; color: white;} "
				"</style></head><body>"
				"<table><tr>"
				"<th>Color Name</th>"
				"<th>White / Dark</th>"
				"<th>Extra Light / Dark</th>"
				"<th>Light / Black</th>"
				"<th>Extra Light / Black</th>"
				"<th>Dark / White</th>"
				"<th>Dark / Light</th>"
				"<th>Dark / Shift Dark</th>"
				"</tr>\n")

		for i in range(num_colors):
			f.write("<tr>\n")
			matched_name = rgb_color_name_match.hex_to_best_xkcd_name(dark_wheel[i])
			color_name = f"hue {i + 1} ({matched_name})"
			dark_hex = dark_wheel[i]
			light_hex = light_wheel[i]
			extra_light_hex = extra_light_wheel[i]
			shifted_dark_hex = dark_wheel[(i + num_colors // 2) % num_colors]

			f.write(_generate_table_td("ffffff", "000000", color_name))
			f.write(_generate_table_td("ffffff", dark_hex, "this is a test"))
			f.write(_generate_table_td(extra_light_hex, dark_hex, "this is a test"))
			f.write(_generate_table_td(light_hex, "000000", "this is a test"))
			f.write(_generate_table_td(extra_light_hex, "000000", "this is a test"))
			f.write(_generate_table_td(dark_hex, "ffffff", "this is a test"))
			f.write(_generate_table_td(dark_hex, light_hex, "this is a test"))
			f.write(_generate_table_td(dark_hex, shifted_dark_hex, "this is a test"))
			f.write("</tr>\n")

		f.write("</table></body></html>")

	print(f"HTML color table saved as {filename}")
	_print_legacy_red_comparison(dark_wheel[0], light_wheel[0], extra_light_wheel[0])


def main():
	if "qti_package_maker" not in sys.modules:
		try:
			import qti_package_maker  # noqa: F401
		except Exception:
			from pathlib import Path
			repo_root = Path(__file__).resolve().parents[3]
			sys.path.insert(0, str(repo_root))

	parser = argparse.ArgumentParser(description="Generate CAM16 color tables and red scans.")
	parser.add_argument("--best-red", action="store_true", help="Report best red offsets and write red scan HTML.")
	parser.add_argument("--scan-output", default="red_scan.html", help="Output file for red scan HTML.")
	parser.add_argument("--output", default="color_table_next_gen.html", help="Output HTML filename.")
	parser.add_argument("--num-colors", type=int, default=16, help="Number of hues to generate.")
	parser.add_argument("--modes", nargs="*", help="Modes to render in the table.")
	args = parser.parse_args()

	if args.best_red:
		target_modes = args.modes
		if not target_modes or "all" in target_modes:
			target_modes = ["xdark", "dark", "normal", "light", "xlight"]
		for mode in target_modes:
			offset = _best_red_offset(args.num_colors, mode, None)
			print(f"best red offset for {mode} ({args.num_colors}): {offset:.1f}")
		_write_red_scan_bundle_html(args.scan_output, num_colors=args.num_colors, modes=target_modes)
		return

	write_html_color_table(args.output, num_colors=args.num_colors, modes=args.modes or None)


if __name__ == "__main__":
	main()
