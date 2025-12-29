#!/usr/bin/env python3

# Standard Library
import pytest

# QTI Package Maker
from qti_package_maker.assessment_items import item_types
from qti_package_maker.engines.html_selftest import write_item as html_write_item
from qti_package_maker.engines.html_selftest import html_functions


def _build_item(item_type: str, item_tuple):
	if item_type == "MC":
		return item_types.MC(*item_tuple)
	if item_type == "MA":
		return item_types.MA(*item_tuple)
	if item_type == "MATCH":
		return item_types.MATCH(*item_tuple)
	if item_type == "NUM":
		return item_types.NUM(*item_tuple)
	if item_type == "FIB":
		return item_types.FIB(*item_tuple)
	if item_type == "MULTI_FIB":
		return item_types.MULTI_FIB(*item_tuple)
	if item_type == "ORDER":
		return item_types.ORDER(*item_tuple)
	raise ValueError(f"Unsupported item type: {item_type}")


@pytest.mark.parametrize("item_type", ["MC", "MA", "MATCH", "NUM", "FIB", "MULTI_FIB", "ORDER"])
def test_html_selftest_outputs_are_valid_html(sample_items, item_type):
	item_cls = _build_item(item_type, sample_items[item_type])
	html_text = getattr(html_write_item, item_type)(item_cls)
	assert html_text
	assert "qti-selftest" in html_text
	html_functions.validate_selftest_html(html_text)


def test_html_selftest_theme_css_contains_palette_selectors(sample_items):
	item_cls = _build_item("MC", sample_items["MC"])
	html_text = html_write_item.MC(item_cls)
	assert "qti-selftest-theme" in html_text
	assert "prefers-color-scheme: dark" in html_text
	assert "data-md-color-scheme" in html_text
	assert "slate" in html_text
	assert "default" in html_text
	assert "--qti-choice-1-bg" in html_text


@pytest.mark.parametrize("item_type", ["MATCH", "ORDER"])
def test_html_selftest_choice_palette_classes(sample_items, item_type):
	item_cls = _build_item(item_type, sample_items[item_type])
	html_text = getattr(html_write_item, item_type)(item_cls)
	assert "qti-choice-" in html_text
	assert "var(--qti-choice-" in html_text
	assert "qti-dropzone" in html_text


def test_html_selftest_num_input_uses_theme_class(sample_items):
	item_cls = _build_item("NUM", sample_items["NUM"])
	html_text = html_write_item.NUM(item_cls)
	assert "qti-input" in html_text
