# Standard Library

# Pip3 Library
import pytest

# QTI Package Maker
from tools import bbq_converter


def test_extract_core_name_success():
	assert bbq_converter.extract_core_name("bbq-biology-questions.txt") == "biology"
	assert bbq_converter.extract_core_name("/tmp/bbq-chem-questions.txt") == "chem"


def test_extract_core_name_rejects_bad_names():
	with pytest.raises(ValueError):
		bbq_converter.extract_core_name("biology-questions.txt")
