#!/usr/bin/env python3

# Standard Library

# Pip3 Library
import pytest

# QTI Package Maker
from qti_package_maker.assessment_items.item_bank import ItemBank


def test_item_bank_rejects_mixed_types_by_default():
	bank = ItemBank()
	bank.add_item("MC", ("Q1?", ["A", "B"], "A"))
	with pytest.raises(ValueError):
		bank.add_item("MA", ("Q2?", ["A", "B", "C"], ["A", "B"]))


def test_item_bank_allows_mixed_types():
	bank = ItemBank(allow_mixed=True)
	bank.add_item("MC", ("Q1?", ["A", "B"], "A"))
	bank.add_item("MA", ("Q2?", ["A", "B", "C"], ["A", "B"]))
	assert len(bank) == 2


def test_item_bank_skips_duplicate_crc(capsys):
	bank = ItemBank()
	bank.add_item("MC", ("Q1?", ["A", "B"], "A"))
	bank.add_item("MC", ("Q1?", ["A", "B"], "A"))
	out = capsys.readouterr().out
	assert "Duplicate item" in out
	assert len(bank) == 1


def test_item_bank_merge_and_operators():
	bank1 = ItemBank()
	bank1.add_item("MC", ("Q1?", ["A", "B"], "A"))
	bank2 = ItemBank()
	bank2.add_item("MC", ("Q2?", ["A", "B"], "B"))

	merged = bank1.merge(bank2)
	assert len(merged) == 2
	assert merged == bank1 + bank2
	assert merged == bank1 | bank2
	assert bank2.merge(bank1) == merged


def test_item_bank_getitem_slice_and_index():
	bank = ItemBank()
	bank.add_item("MC", ("Q1?", ["A", "B"], "A"))
	bank.add_item("MC", ("Q2?", ["A", "B"], "B"))
	bank.add_item("MC", ("Q3?", ["A", "B"], "A"))

	sub_bank = bank[:2]
	assert isinstance(sub_bank, ItemBank)
	assert len(sub_bank) == 2
	assert bank[0].question_text == "Q1?"


def test_item_bank_setitem_reorders():
	bank = ItemBank()
	bank.add_item("MC", ("Q1?", ["A", "B"], "A"))
	bank.add_item("MC", ("Q2?", ["A", "B"], "B"))
	bank.add_item("MC", ("Q3?", ["A", "B"], "A"))

	first_item = bank[0]
	last_item = bank[2]
	bank[0] = last_item
	bank[2] = first_item
	assert bank[0] == last_item


def test_item_bank_histogram_empty(capsys):
	bank = ItemBank()
	bank.print_histogram()
	out = capsys.readouterr().out
	assert out == ""


def test_item_bank_histogram_mc_output(capsys):
	bank = ItemBank()
	bank.add_item("MC", ("Q1?", ["A", "B"], "A"))
	bank.add_item("MC", ("Q2?", ["A", "B"], "B"))
	bank.print_histogram()
	out = capsys.readouterr().out
	assert "Histogram" in out
