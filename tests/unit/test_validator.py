#!/usr/bin/env python3

# Standard Library

# Pip3 Library
import pytest
import lxml.etree

# QTI Package Maker
from qti_package_maker.assessment_items import validator


def test_validate_string_text_rejects_empty():
	with pytest.raises(ValueError):
		validator.validate_string_text("", "question_text")


def test_validate_string_text_rejects_short():
	with pytest.raises(ValueError):
		validator.validate_string_text("ab", "question_text", min_length=3)


def test_validate_string_text_rejects_bad_html():
	with pytest.raises(lxml.etree.XMLSyntaxError):
		validator.validate_string_text("<p><b>", "question_text")


def test_validate_list_of_strings_rejects_duplicates():
	with pytest.raises(ValueError):
		validator.validate_list_of_strings(["A", "A"], "choices_list")


def test_validate_multi_fib_requires_placeholders():
	with pytest.raises(ValueError):
		validator.validate_MULTI_FIB("Fill in [animal].", {"color": ["red"]})


def test_validate_num_rejects_negative_tolerance():
	with pytest.raises(ValueError):
		validator.validate_NUM("Q?", 3.14, -0.01)
