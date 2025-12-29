#!/usr/bin/env python3

# Standard Library

# Pip3 Library
import pytest

# QTI Package Maker
from qti_package_maker.common import yaml_tools


def test_unique_key_loader_rejects_duplicates(tmp_path):
	yaml_path = tmp_path / "dup.yaml"
	yaml_path.write_text("a: 1\na: 2\n", encoding="utf-8")
	with pytest.raises(AssertionError):
		yaml_tools.read_yaml_file(str(yaml_path), msg=False)


def test_apply_replacement_rules_to_text():
	text = " true false "
	out = yaml_tools.applyReplacementRulesToText(text)
	assert "<strong>" in out


def test_apply_replacement_rules_to_list():
	out_list = yaml_tools.applyReplacementRulesToList([" True ", " False "])
	assert all("<strong>" in item for item in out_list)
