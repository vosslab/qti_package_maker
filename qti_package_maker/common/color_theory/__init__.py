#!/usr/bin/env python3

"""Color wheel package with legacy implementation and backend hook."""

# QTI Package Maker
from . import legacy_color_wheel as _legacy

__all__ = [name for name in _legacy.__dict__ if not name.startswith("__")]
globals().update({name: _legacy.__dict__[name] for name in __all__})


def generate_color_wheel(num_colors, backend="legacy", **kwargs):
	"""
	Generate a color wheel using the selected backend.

	Currently supported backends:
	- legacy (default)
	"""
	if backend != "legacy":
		raise NotImplementedError("CAM16 backend not yet implemented.")
	return _legacy.default_color_wheel(num_colors, **kwargs)
