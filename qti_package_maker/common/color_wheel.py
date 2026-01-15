"""
Public API for color wheel generation.

Provides perceptually-distinct colors for multiple-choice answer highlighting.
"""

# Standard Library
import sys

# QTI Package Maker
from qti_package_maker.common.color_theory.legacy_color_wheel import (
	default_color_wheel as _legacy_color_wheel,
	write_html_color_table as _write_html_color_table,
)

__all__ = ["generate_color_wheel"]


def generate_color_wheel(num_colors: int, backend: str = "cam16", **kwargs) -> list:
	"""
	Generate a list of perceptually-distinct hex color codes.

	Args:
		num_colors: Number of colors to generate.
		backend: Color generation algorithm ("cam16" or "legacy").
		**kwargs: Backend-specific options (e.g., mode="dark" for cam16).

	Returns:
		List of hex color strings (e.g., ["a83232", "32a848", ...]).
	"""
	if backend == "legacy":
		return _legacy_color_wheel(num_colors, **kwargs)
	if backend == "cam16":
		from qti_package_maker.common.color_theory import next_gen
		return next_gen.generate_color_wheel(num_colors, **kwargs)
	raise ValueError(f"Unknown backend: {backend}")


def main():
	filename = "color_table.html"
	num_colors = None

	if len(sys.argv) > 1:
		filename = sys.argv[1]
	if len(sys.argv) > 2:
		num_colors = int(sys.argv[2])

	_write_html_color_table(filename, num_colors=num_colors)


if __name__ == "__main__":
	main()
