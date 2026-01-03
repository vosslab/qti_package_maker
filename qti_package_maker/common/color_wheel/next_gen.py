#!/usr/bin/env python3

# Standard Library
import math
import random

#====================================================================
DEFAULT_LIGHTNESS = {
	"very_dark": 0.40,
	"dark": 0.52,
	"light": 0.90,
	"extra_light": 0.94,
}

#====================================================================
# OKLCH / OKLab conversion helpers
# References: https://bottosson.github.io/posts/oklab/
#====================================================================

def _oklch_to_oklab(l, c, h_degrees):
	h_rad = math.radians(h_degrees)
	a = c * math.cos(h_rad)
	b = c * math.sin(h_rad)
	return l, a, b

#====================================================================

def _oklab_to_linear_srgb(l, a, b):
	l_ = l + 0.3963377774 * a + 0.2158037573 * b
	m_ = l - 0.1055613458 * a - 0.0638541728 * b
	s_ = l - 0.0894841775 * a - 1.2914855480 * b

	l = l_ ** 3
	m = m_ ** 3
	s = s_ ** 3

	r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
	g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
	b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
	return r, g, b

#====================================================================

def _linear_to_srgb_channel(value):
	if value <= 0.0031308:
		return 12.92 * value
	return 1.055 * (value ** (1.0 / 2.4)) - 0.055

#====================================================================

def _srgb_channel_to_linear(value):
	if value <= 0.04045:
		return value / 12.92
	return ((value + 0.055) / 1.055) ** 2.4

#====================================================================

def _linear_srgb_to_oklab(r, g, b):
	l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
	m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
	s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

	l_ = l ** (1.0 / 3.0)
	m_ = m ** (1.0 / 3.0)
	s_ = s ** (1.0 / 3.0)

	l_ok = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
	a_ok = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
	b_ok = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
	return l_ok, a_ok, b_ok

#====================================================================

def _oklab_to_oklch(l, a, b):
	c = math.sqrt(a * a + b * b)
	h = math.degrees(math.atan2(b, a)) % 360.0
	return l, c, h

#====================================================================

def _srgb_to_oklch(r, g, b):
	r_lin = _srgb_channel_to_linear(r)
	g_lin = _srgb_channel_to_linear(g)
	b_lin = _srgb_channel_to_linear(b)
	return _oklab_to_oklch(*_linear_srgb_to_oklab(r_lin, g_lin, b_lin))

# OKLCH hue for sRGB red (#ff0000)
TRUE_RED_HUE = _srgb_to_oklch(1.0, 0.0, 0.0)[2]
TRUE_YELLOW_HUE = _srgb_to_oklch(1.0, 1.0, 0.0)[2]

#====================================================================

def _oklch_to_linear_srgb(l, c, h_degrees):
	l_ok, a_ok, b_ok = _oklch_to_oklab(l, c, h_degrees)
	return _oklab_to_linear_srgb(l_ok, a_ok, b_ok)

#====================================================================

def _oklch_in_gamut(l, c, h_degrees, epsilon=1e-7):
	r, g, b = _oklch_to_linear_srgb(l, c, h_degrees)
	return (
		-epsilon <= r <= 1.0 + epsilon and
		-epsilon <= g <= 1.0 + epsilon and
		-epsilon <= b <= 1.0 + epsilon
	)

#====================================================================

def _max_chroma_for_hue_lightness(l, h_degrees, max_limit=1.5, steps=24):
	if not _oklch_in_gamut(l, 0.0, h_degrees):
		return 0.0

	lo = 0.0
	hi = 0.1
	while hi < max_limit and _oklch_in_gamut(l, hi, h_degrees):
		lo = hi
		hi *= 1.5

	if hi >= max_limit and _oklch_in_gamut(l, max_limit, h_degrees):
		return max_limit

	if hi > max_limit:
		hi = max_limit

	for _ in range(steps):
		mid = (lo + hi) / 2.0
		if _oklch_in_gamut(l, mid, h_degrees):
			lo = mid
		else:
			hi = mid

	return lo

#====================================================================
def _max_chroma_for_hues(hues, lightness):
	return [_max_chroma_for_hue_lightness(lightness, h) for h in hues]

#====================================================================
def _uniform_chroma_for_hues(hues, lightness):
	max_chromas = _max_chroma_for_hues(hues, lightness)
	if not max_chromas:
		return 0.0
	return min(max_chromas)

#====================================================================

def _oklch_to_srgb_hex(l, c, h_degrees):
	r_lin, g_lin, b_lin = _oklch_to_linear_srgb(l, c, h_degrees)
	r = _linear_to_srgb_channel(r_lin)
	g = _linear_to_srgb_channel(g_lin)
	b = _linear_to_srgb_channel(b_lin)

	r = min(max(r, 0.0), 1.0)
	g = min(max(g, 0.0), 1.0)
	b = min(max(b, 0.0), 1.0)

	ri = int(round(r * 255))
	gi = int(round(g * 255))
	bi = int(round(b * 255))
	return f"{ri:02x}{gi:02x}{bi:02x}"

#====================================================================

def _score_offset_for_lightnesses(offset, step, lightnesses, num_colors):
	hues = [(offset + step * i) % 360.0 for i in range(num_colors)]
	min_chromas = [
		_uniform_chroma_for_hues(hues, lightness)
		for lightness in lightnesses
	]
	return min(min_chromas)

#====================================================================

def _choose_hue_offset(num_colors, lightnesses=None, samples=24):
	step = 360.0 / float(num_colors)
	if not lightnesses:
		return random.random() * 360.0

	best_offset = None
	best_score = None
	for _ in range(samples):
		offset = random.random() * 360.0
		score = _score_offset_for_lightnesses(offset, step, lightnesses, num_colors)
		if best_score is None or score > best_score:
			best_score = score
			best_offset = offset

	return best_offset

#====================================================================

def _generate_hues(
	num_colors,
	lightnesses=None,
	offset_strategy="random",
	samples=24,
	anchor_hue=None,
):
	step = 360.0 / float(num_colors)
	if anchor_hue is not None:
		offset = float(anchor_hue) % 360.0
	elif offset_strategy == "optimize_min_chroma":
		offset = _choose_hue_offset(num_colors, lightnesses=lightnesses, samples=samples)
	else:
		offset = random.random() * 360.0
	return [(offset + step * i) % 360.0 for i in range(num_colors)]

#====================================================================

def _circular_distance_degrees(a, b):
	diff = abs(a - b) % 360.0
	return min(diff, 360.0 - diff)

#====================================================================

def _hue_gaussian_weight(hue, center, width_degrees):
	if width_degrees <= 0:
		return 0.0
	distance = _circular_distance_degrees(hue, center)
	return math.exp(-(distance ** 2) / (2.0 * (width_degrees ** 2)))

#====================================================================

def _apply_hue_balance(c, hue, lightness, max_c, width_degrees=28.0):
	weight = _hue_gaussian_weight(hue, TRUE_YELLOW_HUE, width_degrees)
	if weight <= 0.0:
		return c

	if lightness <= DEFAULT_LIGHTNESS["dark"] + 0.02:
		c = c * (1.0 + 0.30 * weight)
	elif abs(lightness - DEFAULT_LIGHTNESS["light"]) <= 0.02:
		c = c * (1.0 - 0.35 * weight)

	if max_c is not None:
		c = min(c, max_c)
	return max(c, 0.0)

#====================================================================

def _oklch_wheel_for_hues(
	hues,
	lightness,
	chroma_mode="blend",
	blend=0.55,
	blend_gamma=1.6,
	hue_balance=True,
):
	colors = []
	# chroma_mode: "uniform" for even hues, "max" for per-hue max, "blend" for mixed
	uniform_c = None
	max_chromas = None
	if chroma_mode in ("uniform", "blend"):
		uniform_c = _uniform_chroma_for_hues(hues, lightness)
	if chroma_mode in ("max", "blend") or hue_balance:
		max_chromas = _max_chroma_for_hues(hues, lightness)
		max_chroma_global = max(max_chromas) if max_chromas else uniform_c
	for idx, h in enumerate(hues):
		if chroma_mode == "uniform":
			c = uniform_c
		elif chroma_mode == "max":
			c = _max_chroma_for_hue_lightness(lightness, h)
		else:
			if max_chroma_global is None or max_chroma_global <= uniform_c:
				c = uniform_c
			else:
				ratio = (max_chromas[idx] - uniform_c) / (max_chroma_global - uniform_c)
				ratio = max(0.0, ratio) ** blend_gamma
				c = uniform_c + blend * ratio * (max_chroma_global - uniform_c)

		if hue_balance:
			max_c = max_chromas[idx] if max_chromas else None
			c = _apply_hue_balance(c, h, lightness, max_c)
		colors.append(_oklch_to_srgb_hex(lightness, c, h))
	return colors

#====================================================================

def oklch_color_wheel(
	num_colors,
	category="dark",
	chroma_mode="blend",
	offset_strategy="optimize_min_chroma",
	samples=24,
	anchor_hue=TRUE_RED_HUE,
	blend=0.55,
	blend_gamma=1.6,
	hue_balance=True,
):
	if num_colors <= 0:
		raise ValueError("num_colors must be positive")

	if category not in DEFAULT_LIGHTNESS:
		raise ValueError(f"Unknown category: {category}")

	hues = _generate_hues(
		num_colors,
		lightnesses=[DEFAULT_LIGHTNESS[category]],
		offset_strategy=offset_strategy,
		samples=samples,
		anchor_hue=anchor_hue,
	)
	return _oklch_wheel_for_hues(
		hues,
		DEFAULT_LIGHTNESS[category],
		chroma_mode=chroma_mode,
		blend=blend,
		blend_gamma=blend_gamma,
		hue_balance=hue_balance,
	)

#====================================================================

def oklch_light_and_dark_color_wheel(
	num_colors,
	chroma_mode="blend",
	offset_strategy="optimize_min_chroma",
	samples=24,
	anchor_hue=TRUE_RED_HUE,
	blend=0.55,
	blend_gamma=1.6,
	hue_balance=True,
):
	lightnesses = [DEFAULT_LIGHTNESS["dark"], DEFAULT_LIGHTNESS["light"]]
	hues = _generate_hues(
		num_colors,
		lightnesses=lightnesses,
		offset_strategy=offset_strategy,
		samples=samples,
		anchor_hue=anchor_hue,
	)
	light_colors = _oklch_wheel_for_hues(
		hues,
		DEFAULT_LIGHTNESS["light"],
		chroma_mode=chroma_mode,
		blend=blend,
		blend_gamma=blend_gamma,
		hue_balance=hue_balance,
	)
	dark_colors = _oklch_wheel_for_hues(
		hues,
		DEFAULT_LIGHTNESS["dark"],
		chroma_mode=chroma_mode,
		blend=blend,
		blend_gamma=blend_gamma,
		hue_balance=hue_balance,
	)
	return light_colors, dark_colors

#====================================================================

def oklch_all_color_wheels(
	num_colors,
	chroma_mode="blend",
	offset_strategy="optimize_min_chroma",
	samples=24,
	anchor_hue=TRUE_RED_HUE,
	blend=0.55,
	blend_gamma=1.6,
	hue_balance=True,
):
	lightnesses = [
		DEFAULT_LIGHTNESS["dark"],
		DEFAULT_LIGHTNESS["light"],
	]
	hues = _generate_hues(
		num_colors,
		lightnesses=lightnesses,
		offset_strategy=offset_strategy,
		samples=samples,
		anchor_hue=anchor_hue,
	)
	extra_light = _oklch_wheel_for_hues(
		hues,
		DEFAULT_LIGHTNESS["extra_light"],
		chroma_mode=chroma_mode,
		blend=blend,
		blend_gamma=blend_gamma,
		hue_balance=hue_balance,
	)
	light = _oklch_wheel_for_hues(
		hues,
		DEFAULT_LIGHTNESS["light"],
		chroma_mode=chroma_mode,
		blend=blend,
		blend_gamma=blend_gamma,
		hue_balance=hue_balance,
	)
	dark = _oklch_wheel_for_hues(
		hues,
		DEFAULT_LIGHTNESS["dark"],
		chroma_mode=chroma_mode,
		blend=blend,
		blend_gamma=blend_gamma,
		hue_balance=hue_balance,
	)
	return extra_light, light, dark

#====================================================================

def _generate_table_td(bg_hex_color, text_hex_color, text="this is a test"):
	"""
	Generates an HTML table cell (<td>) with the specified background and text color.
	"""
	td_cell = ''
	td_cell += f"<td style='background-color:#{bg_hex_color};'>"
	td_cell += f"<span style='color:#{text_hex_color};'>{text}</span></td>\n"
	return td_cell

#====================================================================

def write_html_color_table(
	filename,
	num_colors=16,
	chroma_mode="blend",
	offset_strategy="optimize_min_chroma",
	samples=24,
	anchor_hue=TRUE_RED_HUE,
	blend=0.55,
	blend_gamma=1.6,
	hue_balance=True,
):
	"""
	Generates an HTML table displaying next-gen OKLCH color combinations.
	"""
	extra_light_colors, light_colors, dark_colors = oklch_all_color_wheels(
		num_colors,
		chroma_mode=chroma_mode,
		offset_strategy=offset_strategy,
		samples=samples,
		anchor_hue=anchor_hue,
		blend=blend,
		blend_gamma=blend_gamma,
		hue_balance=hue_balance,
	)
	color_names = [f"hue {i + 1}" for i in range(num_colors)]

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
			color_name = color_names[i]
			dark_hex = dark_colors[i]
			light_hex = light_colors[i]
			extra_light_hex = extra_light_colors[i]
			shifted_dark_hex = dark_colors[(i + num_colors // 2) % num_colors]

			f.write("<tr>\n")
			f.write(_generate_table_td("ffffff", "000000", color_name))
			f.write(_generate_table_td("ffffff", dark_hex))
			f.write(_generate_table_td(extra_light_hex, dark_hex))
			f.write(_generate_table_td(light_hex, "000000"))
			f.write(_generate_table_td(extra_light_hex, "000000"))
			f.write(_generate_table_td(dark_hex, "ffffff"))
			f.write(_generate_table_td(dark_hex, light_hex))
			f.write(_generate_table_td(dark_hex, shifted_dark_hex))
			f.write("</tr>\n")

		f.write("</table></body></html>")

	print(f"HTML color table saved as {filename}")

#====================================================================

def main():
	html_filename = "color_table_next_gen.html"
	write_html_color_table(html_filename)

#====================================================================

if __name__ == "__main__":
	main()
