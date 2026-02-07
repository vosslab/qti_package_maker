# Standard Library
import zipfile

# Pip3 Library
import lxml.etree

# QTI Package Maker
from qti_package_maker.assessment_items.item_bank import ItemBank
from qti_package_maker.engines.canvas_qti_v1_2 import engine_class as qti12_engine
from qti_package_maker.engines.blackboard_qti_v2_1 import engine_class as qti21_engine


def _build_bank_qti12():
	bank = ItemBank(allow_mixed=True)
	bank.add_item("MC", ("Q1?", ["A", "B"], "A"))
	bank.add_item("FIB", ("Q2?", ["alpha", "beta"]))
	return bank


def _build_bank_qti21():
	bank = ItemBank(allow_mixed=True)
	bank.add_item("MC", ("Q1?", ["A", "B"], "B"))
	bank.add_item("NUM", ("Q2?", 3.14, 0.01))
	return bank


def _parse_xml_bytes(xml_bytes):
	return lxml.etree.fromstring(xml_bytes)


def _find_first_by_local_name(root, name):
	for node in root.iter():
		if node.tag.endswith(name):
			return node
	return None


def _assert_manifest_refs_present(manifest_bytes, zip_names):
	root = _parse_xml_bytes(manifest_bytes)
	file_hrefs = [node.get("href") for node in root.findall(".//file")]
	resource_hrefs = [node.get("href") for node in root.findall(".//resource")]
	for href in file_hrefs + resource_hrefs:
		if href:
			assert href in zip_names


def test_qti12_zip_layout_and_manifest(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	engine = qti12_engine.EngineClass("sample", verbose=False)
	outfile = tmp_path / "qti12.zip"
	engine.save_package(_build_bank_qti12(), outfile=str(outfile))
	assert outfile.exists()

	with zipfile.ZipFile(outfile, "r") as zipf:
		zip_names = set(zipf.namelist())
		assert "imsmanifest.xml" in zip_names
		assert "canvas_qti12_questions/assessment_meta.xml" in zip_names
		assert "canvas_qti12_questions/canvas_qti12_questions.xml" in zip_names

		manifest_bytes = zipf.read("imsmanifest.xml")
		_assert_manifest_refs_present(manifest_bytes, zip_names)

		items_bytes = zipf.read("canvas_qti12_questions/canvas_qti12_questions.xml")
		items_text = items_bytes.decode("utf-8")
		assert "</item>\n\n      <item" in items_text
		assert "</itemmetadata>\n\n        <presentation>" in items_text
		root = _parse_xml_bytes(items_bytes)
		assert root.tag.endswith("questestinterop")


def test_qti21_zip_layout_and_manifest(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	engine = qti21_engine.EngineClass("sample", verbose=False)
	outfile = tmp_path / "qti21.zip"
	engine.save_package(_build_bank_qti21(), outfile=str(outfile))
	assert outfile.exists()

	with zipfile.ZipFile(outfile, "r") as zipf:
		zip_names = set(zipf.namelist())
		assert "imsmanifest.xml" in zip_names
		assert "qti21_items/assessment_meta.xml" in zip_names
		assert "qti21_items/item_00001.xml" in zip_names
		assert "qti21_items/item_00002.xml" in zip_names

		manifest_bytes = zipf.read("imsmanifest.xml")
		_assert_manifest_refs_present(manifest_bytes, zip_names)

		item_bytes = zipf.read("qti21_items/item_00001.xml")
		item_text = item_bytes.decode("utf-8")
		assert "</responseDeclaration>\n\n  <outcomeDeclaration" in item_text
		assert "/>\n\n  <itemBody>" in item_text
		item_root = _parse_xml_bytes(item_bytes)
		assert item_root.tag.endswith("assessmentItem")
		assert _find_first_by_local_name(item_root, "responseDeclaration") is not None
		assert _find_first_by_local_name(item_root, "itemBody") is not None
		assert _find_first_by_local_name(item_root, "responseProcessing") is not None
