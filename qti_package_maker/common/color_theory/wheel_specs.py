#!/usr/bin/env python3

"""Wheel mode specifications and viewing defaults."""

# Standard Library
from dataclasses import MISSING, dataclass, fields
from pathlib import Path
from typing import Optional

import yaml


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
	target_ucs_r: Optional[float] = None


_DEFAULT_WHEEL_SPECS = {
	"very_dark": WheelSpec(target_j=25.0, m_min=20.0, m_max=90.0, shared_m_quantile=0.45, allow_m_variation=0.18, max_m_blend=0.45),
	"xdark": WheelSpec(target_j=25.0, m_min=22.0, m_max=95.0, shared_m_quantile=0.50, allow_m_variation=0.18, max_m_blend=0.50),
	"dark": WheelSpec(target_j=40.0, m_min=18.0, m_max=85.0, shared_m_quantile=0.40, allow_m_variation=0.15, max_m_blend=0.40),
	"normal": WheelSpec(target_j=55.0, m_min=8.0, m_max=45.0, shared_m_quantile=0.25, allow_m_variation=0.08, max_m_blend=0.25),
	"light": WheelSpec(target_j=75.0, m_min=1.5, m_max=10.0, shared_m_quantile=0.12, allow_m_variation=0.03, max_m_blend=0.15, target_ucs_r=14.0),
	"xlight": WheelSpec(target_j=90.0, m_min=1.0, m_max=8.0, shared_m_quantile=0.08, allow_m_variation=0.02, max_m_blend=0.10, target_ucs_r=12.0),
}

_DEFAULT_VIEWING = {
	"surround": "Average",
	"white_point": "D65",
	"adapting_luminance": 64.0,
	"background_luminance": 20.0,
}

_DEFAULT_BEST_RED_OFFSETS = {
	16: {
		"xdark": 27.2,
		"dark": 25.0,
		"normal": 19.2,
		"light": 20.6,
		"xlight": 17.0,
	},
}


def _build_wheel_spec(values, defaults=None):
	base = defaults.__dict__ if defaults is not None else {}
	merged = {**base, **(values or {})}
	kwargs = {}
	for field in fields(WheelSpec):
		if field.name in merged:
			kwargs[field.name] = merged[field.name]
		elif field.default is not MISSING:
			kwargs[field.name] = field.default
		elif field.default_factory is not MISSING:  # type: ignore[comparison-overlap]
			kwargs[field.name] = field.default_factory()  # type: ignore[misc]
		else:
			raise ValueError(f"Missing required wheel spec field: {field.name}")
	return WheelSpec(**kwargs)


def _load_wheel_specs_from_yaml():
	yaml_path = Path(__file__).with_name("wheel_specs.yaml")
	if not yaml_path.exists():
		return _DEFAULT_WHEEL_SPECS, _DEFAULT_VIEWING, _DEFAULT_BEST_RED_OFFSETS

	with yaml_path.open("r") as handle:
		data = yaml.safe_load(handle) or {}

	viewing = dict(_DEFAULT_VIEWING)
	viewing.update(data.get("viewing", {}) or {})

	specs = {}
	raw_specs = data.get("wheel_specs", {}) or {}
	if not raw_specs:
		specs = dict(_DEFAULT_WHEEL_SPECS)
	else:
		for mode, see in raw_specs.items():
			defaults = _DEFAULT_WHEEL_SPECS.get(mode)
			specs[mode] = _build_wheel_spec(see, defaults=defaults)

	red_offsets = dict(_DEFAULT_BEST_RED_OFFSETS)
	raw_offsets = data.get("best_red_offsets", {}) or {}
	if raw_offsets:
		red_offsets = raw_offsets

	return specs, viewing, red_offsets


DEFAULT_WHEEL_SPECS, DEFAULT_VIEWING, DEFAULT_BEST_RED_OFFSETS = _load_wheel_specs_from_yaml()
DEFAULT_WHEEL_MODE_ORDER = list(DEFAULT_WHEEL_SPECS.keys())
