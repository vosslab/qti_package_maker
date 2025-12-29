#!/usr/bin/env python3

# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.assessment_items.item_bank import ItemBank


class _DummyWriteItem:
	@staticmethod
	def MC(item_cls):
		return "ok"


class DummyEngine(base_engine.BaseEngine):
	def __init__(self, package_name: str):
		super().__init__(package_name, verbose=False)
		self.write_item = _DummyWriteItem

	def _get_name(self) -> str:
		return "dummy"

	def read_package(self, infile: str):
		raise NotImplementedError

	def save_package(self, item_bank, outfile: str = None):
		raise NotImplementedError


def test_get_outfile_name_default_prefix():
	engine = DummyEngine("sample")
	assert engine.get_outfile_name("qti12", "zip") == "qti12-sample.zip"


def test_get_outfile_name_respects_existing_prefix():
	engine = DummyEngine("sample")
	assert engine.get_outfile_name("qti12", "zip", "qti12-sample.zip") == "qti12-sample.zip"


def test_process_item_bank_empty():
	engine = DummyEngine("sample")
	empty_bank = ItemBank()
	assert engine.process_item_bank(empty_bank) == []
	assert engine.process_one_item_from_item_bank(empty_bank) is None
