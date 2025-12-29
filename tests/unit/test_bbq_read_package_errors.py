#!/usr/bin/env python3

# Standard Library

# Pip3 Library
import pytest

# QTI Package Maker
from qti_package_maker.engines.bbq_text_upload import read_package


def test_make_item_cls_from_line_requires_correct_flag():
	line = "MC\t2+2?\t3\tincorrect\t4\tincorrect"
	with pytest.raises(ValueError):
		read_package.make_item_cls_from_line(line)
