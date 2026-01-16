# Standard Library

# Pip3 Library
import pytest

# QTI Package Maker
from qti_package_maker.assessment_items import item_types
from qti_package_maker.engines.bbq_text_upload import read_package


def test_indices_helper():
	assert read_package.indices([0, 0, 1, 0, 0], 1) == [2]
	assert read_package.indices([0, 1, 0, 1, 0, 1], 1) == [1, 3, 5]


def test_make_item_cls_from_line_mc():
	line = "MC\t2+2?\t3\tincorrect\t4\tcorrect"
	item = read_package.make_item_cls_from_line(line)
	assert isinstance(item, item_types.MC)


def test_make_item_cls_from_line_ma():
	line = "MA\tPrime numbers?\t2\tcorrect\t3\tcorrect\t4\tincorrect\t5\tcorrect"
	item = read_package.make_item_cls_from_line(line)
	assert isinstance(item, item_types.MA)


def test_make_item_cls_from_line_match():
	line = "MAT\tMatch capital to country.\tUSA\tWashington\tFrance\tParis"
	item = read_package.make_item_cls_from_line(line)
	assert isinstance(item, item_types.MATCH)


def test_make_item_cls_from_line_order():
	line = "ORD\tOrder these.\tOne\tTwo\tThree"
	item = read_package.make_item_cls_from_line(line)
	assert isinstance(item, item_types.ORDER)


def test_make_item_cls_from_line_fib():
	line = "FIB\tCapital of France?\tParis"
	item = read_package.make_item_cls_from_line(line)
	assert isinstance(item, item_types.FIB)


def test_make_item_cls_from_line_multi_fib():
	line = "FIB_PLUS\tFill in: [animal] and [color].\tanimal\tcow\t\tcolor\tbrown"
	item = read_package.make_item_cls_from_line(line)
	assert isinstance(item, item_types.MULTI_FIB)
	assert item.answer_map["animal"] == ["cow"]
	assert item.answer_map["color"] == ["brown"]


def test_make_item_cls_from_line_num():
	line = "NUM\tApprox pi?\t3.14\t0.01"
	item = read_package.make_item_cls_from_line(line)
	assert isinstance(item, item_types.NUM)


def test_make_item_cls_from_line_blank():
	assert read_package.make_item_cls_from_line("") is None


def test_make_item_cls_from_line_unknown():
	with pytest.raises(ValueError):
		read_package.make_item_cls_from_line("NOPE\tQ?\tA")


def test_read_items_from_file(tmp_path):
	bbq_file = tmp_path / "bbq-test.txt"
	bbq_file.write_text(
		"MC\t2+2?\t3\tincorrect\t4\tcorrect\nFIB\tCapital of France?\tParis\n",
		encoding="utf-8",
	)
	bank = read_package.read_items_from_file(str(bbq_file), allow_mixed=True)
	assert len(bank) == 2
