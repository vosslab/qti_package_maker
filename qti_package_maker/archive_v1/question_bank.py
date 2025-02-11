#!/usr/bin/env python3

import os
from lxml import etree

#==============
def generate_question_bank(package_title: str, assessment_file_name_list: list):
	"""
	Generates the XML for the question bank (question_bank00001.xml).

	Args:
		assessment_file_name_list (list[str]): List of assessment item file names.

	Returns:
		etree.ElementTree: The generated XML tree for question_bank00001.xml.
	"""
	assessment_file_name_list.sort()
	question_bank = create_question_bank_header(package_title)
	assessment_section = create_assessment_section(assessment_file_name_list)
	question_bank.append(assessment_section)

	return etree.ElementTree(question_bank)

#==============
def create_question_bank_header(package_title: str) -> etree.Element:
	"""
	Creates the root element for the question bank XML, including namespaces and custom attribute order.

	Args:
		package_title (str): The title for the assessment test.

	Returns:
		etree.Element: The root 'assessmentTest' element with attributes in the desired order.
	"""
	# Define namespaces
	nsmap = {
		None: "http://www.imsglobal.org/xsd/imsqti_v2p1",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance"
	}

	# Create the root element with namespaces
	assessment_test = etree.Element("assessmentTest", nsmap=nsmap)

	# Add the xsi:schemaLocation attribute first
	assessment_test.attrib["{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"] = (
		"http://www.imsglobal.org/xsd/imsqti_v2p1 "
		"http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1.xsd"
	)

	# Add identifier and title attributes next
	assessment_test.set("identifier", "question_bank00001")
	assessment_test.set("title", package_title)

	return assessment_test

#==============
def create_assessment_section(assessment_file_name_list: list[str]) -> etree.Element:
	"""
	Creates the assessment section, which references all assessment items.

	Args:
		assessment_file_name_list (list[str]): List of assessment item file names.

	Returns:
		etree.Element: The 'testPart' element containing assessment item references.
	"""
	test_part = etree.Element("testPart", identifier="question_bank00001_1",
		navigationMode="nonlinear", submissionMode="simultaneous")

	# Add an assessment section referencing each assessment item file
	assessment_ref = etree.Element("assessmentSection",
		identifier="question_bank00001_1_1", visible="false", title="Section 1")
	for file_name in assessment_file_name_list:
		base_name = os.path.splitext(file_name)[0]
		item_ref = etree.SubElement(assessment_ref, "assessmentItemRef",
			identifier=base_name,
			href=f"{file_name}")
		assessment_ref.append(item_ref)
	test_part.append(assessment_ref)

	return test_part

#==============
#==============
def dummy_test_run():
	# Generate question_bank00001.xml
	assessment_file_name_list = [
		'assessmentItem00001.xml',
		'assessmentItem00002.xml',
		'assessmentItem00003.xml',
	]
	package_title = "Simple_Pool"
	question_bank_etree = generate_question_bank(package_title, assessment_file_name_list)
	question_bank_xml_string = etree.tostring(question_bank_etree, pretty_print=True,
		xml_declaration=True, encoding="UTF-8")
	question_bank_path = "question_bank00001.xml"
	with open(question_bank_path, "w", encoding="utf-8") as f:
		f.write(question_bank_xml_string.decode("utf-8"))

#==============
#==============
if __name__ == "__main__":
	dummy_test_run()


