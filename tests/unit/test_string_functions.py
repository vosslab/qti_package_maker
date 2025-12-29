#!/usr/bin/env python3

# Standard Library

# Pip3 Library
import pytest

# QTI Package Maker
from qti_package_maker.common import string_functions


def test_strip_crc_prefix():
	assert string_functions.strip_crc_prefix("34. b5b6 banana") == "banana"
	assert string_functions.strip_crc_prefix("<p>b5b6</p> banana") == "banana"


def test_strip_prefix_from_string():
	assert string_functions.strip_prefix_from_string("A. Glucose") == "Glucose"
	assert string_functions.strip_prefix_from_string("<p>A. Glucose</p>") == "<p>Glucose</p>"


def test_remove_prefix_from_list():
	choices = ["A. One", "B. Two", "C. Three"]
	assert string_functions.remove_prefix_from_list(choices) == ["One", "Two", "Three"]


def test_number_helpers_bounds():
	with pytest.raises(ValueError):
		string_functions.number_to_letter(0)
	with pytest.raises(ValueError):
		string_functions.number_to_lowercase(0)


def test_html_table_to_text():
	html = "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>"
	table_text = string_functions._html_table_to_text(html)
	assert "[TABLE]" not in table_text
	assert "A" in table_text
	assert "B" in table_text
	assert "1" in table_text
	assert "2" in table_text


def test_format_html_lxml_basic():
	raw_html = "<div><p>Text</p><ul><li>A</li><li>B</li></ul></div>"
	formatted = string_functions.format_html_lxml(raw_html)
	assert "<div" in formatted
	assert "<li" in formatted


def test_format_html_lxml_skips_script(capsys):
	raw_html = "<script>var x = 1;</script><div>ok</div>"
	formatted = string_functions.format_html_lxml(raw_html)
	out = capsys.readouterr().out
	assert "skipping" in out
	assert formatted == raw_html
