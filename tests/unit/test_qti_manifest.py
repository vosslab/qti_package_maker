#!/usr/bin/env python3

# Standard Library

# Pip3 Library
import pytest

# QTI Package Maker
from qti_package_maker.common import qti_manifest


def test_manifest_qti12_rejects_multiple_files():
	with pytest.raises(ValueError):
		qti_manifest.generate_manifest("dummy", ["a/a.xml", "b/b.xml"], version="1.2")


def test_manifest_qti12_rejects_mismatched_dir_and_base():
	with pytest.raises(ValueError):
		qti_manifest.generate_manifest("dummy", ["qti12_items/assessment.xml"], version="1.2")


def test_manifest_qti12_resources_include_meta():
	tree = qti_manifest.generate_manifest("dummy", ["qti12_items/qti12_items.xml"], version="1.2")
	root = tree.getroot()
	resources = root.findall(".//resources/resource")
	assert len(resources) >= 2

	resource_ids = {resource.get("identifier") for resource in resources}
	assert "assessment_meta" in resource_ids
