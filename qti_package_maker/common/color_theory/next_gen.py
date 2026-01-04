#!/usr/bin/env python3

"""CAM16-based color wheel generator using colour-science."""

# Standard Library
import argparse

# QTI Package Maker
from qti_package_maker.common.color_theory.cam16_utils import (
	_cam16_ucs_radius,
	_gamut_margin,
	_linear_rgb_in_gamut,
	_srgb_hex_to_cam16_spec,
	_xyz_to_srgb,
	cam16_jmh_to_xyz,
)
from qti_package_maker.common.color_theory.color_utils import _hex_to_rgb, _rgb_distance, _srgb_to_hex
from qti_package_maker.common.color_theory.generator import (
	_color_for_hue,
	_colors_for_hues,
	_max_m_for_hue,
	_m_for_target_ucs_r,
	_print_legacy_red_comparison,
	_quantile,
	_redness_score,
	_resolve_anchor_hex,
	_rotate_colors_to_target,
	_shared_m_and_max_ms,
	generate_color_wheel,
)
from qti_package_maker.common.color_theory.hue_layout import (
	_generate_hues_anchor,
	_generate_hues_equal,
	_generate_hues_offset,
	_generate_hues_optimized,
)
from qti_package_maker.common.color_theory.html_tables import (
	_generate_table_td,
	write_html_color_table,
	write_html_color_table_cam16_debug,
)
from qti_package_maker.common.color_theory.red_scan import (
	_BEST_RED_OFFSETS,
	_best_red_offset,
	_render_red_scan_tables,
	_select_hues_for_anchor,
	_write_red_scan_bundle_html,
	_write_red_scan_html,
)
from qti_package_maker.common.color_theory.wheel_specs import DEFAULT_VIEWING, DEFAULT_WHEEL_MODE_ORDER, DEFAULT_WHEEL_SPECS, WheelSpec, _build_wheel_spec, _validate_colorfulness_control


def main():
	parser = argparse.ArgumentParser(description="Generate CAM16 color tables and red scans.")
	parser.add_argument("--best-red", action="store_true", help="Report best red offsets and write red scan HTML.")
	parser.add_argument("--scan-output", default="red_scan.html", help="Output file for red scan HTML.")
	parser.add_argument("--output", default="color_table_next_gen.html", help="Output HTML filename.")
	parser.add_argument("--cam16-debug", action="store_true", help="Write CAM16 debug HTML output.")
	parser.add_argument("--cam16-debug-output", default="color_table_cam16_debug.html", help="Output CAM16 debug HTML filename.")
	parser.add_argument("--num-colors", type=int, default=16, help="Number of hues to generate.")
	parser.add_argument("--modes", nargs="*", help="Modes to render in the table.")
	args = parser.parse_args()

	if args.best_red:
		target_modes = args.modes
		if not target_modes or "all" in target_modes:
			target_modes = list(DEFAULT_WHEEL_MODE_ORDER)
		for mode in target_modes:
			offset = _best_red_offset(args.num_colors, mode, None)
			print(f"best red offset for {mode} ({args.num_colors}): {offset:.1f}")
		_write_red_scan_bundle_html(args.scan_output, num_colors=args.num_colors, modes=target_modes)
		return

	write_html_color_table(args.output, num_colors=args.num_colors, modes=args.modes or None)
	if args.cam16_debug:
		write_html_color_table_cam16_debug(
			args.cam16_debug_output,
			num_colors=args.num_colors,
			modes=args.modes or None,
		)


if __name__ == "__main__":
	main()
