"""
Public facade for the legacy color wheel API.

Implementation lives in qti_package_maker.common.color_theory.legacy_color_wheel.
"""
from qti_package_maker.common.color_theory.legacy_color_wheel import *  # noqa: F401,F403


def generate_color_wheel(num_colors, backend="legacy", **kwargs):
	"""
	Generate a color wheel using the selected backend.

	Currently supported backends:
	- legacy (default)
	"""
	if backend == "legacy":
		return default_color_wheel(num_colors, **kwargs)
	if backend == "cam16":
		from qti_package_maker.common.color_theory import next_gen
		return next_gen.generate_color_wheel(num_colors, **kwargs)
	raise ValueError(f"Unknown backend: {backend}")
