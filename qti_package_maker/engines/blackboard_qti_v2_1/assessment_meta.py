#!/usr/bin/env python3

import os
from lxml import etree

#==============
def generate_assessment_meta(package_name: str, assessment_file_name_list: list[str]) -> etree.ElementTree:
	"""
	Generates the XML for the question bank (assessment_meta.xml).

	Args:
		package_name (str): The title for the set of assessments.
		assessment_file_name_list (list[str]): List of assessment item file names.

	Returns:
		etree.ElementTree: The generated XML tree for assessment_meta.xml.
	"""
	assessment_file_name_list.sort()
	assessment_meta = create_assessment_meta_header(package_name)
	assessment_section = create_assessment_section(assessment_file_name_list)
	assessment_meta.append(assessment_section)

	return etree.ElementTree(assessment_meta)

#==============
def create_assessment_meta_header(package_name: str) -> etree.Element:
	"""
	Creates the root element for the question bank XML, including namespaces and custom attribute order.

	Args:
		package_name (str): The title for the set of assessments.

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
	assessment_test.set("identifier", "assessment_meta")
	assessment_test.set("title", package_name)

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
	test_part = etree.Element("testPart", identifier="test_part",
		navigationMode="nonlinear", submissionMode="simultaneous")

	# Add an assessment section referencing each assessment item file
	assessment_ref = etree.Element("assessmentSection",
		identifier="section_part", visible="false", title="Question Pool")
	for file_name in assessment_file_name_list:
		base_name = os.path.splitext(file_name)[0]
		item_ref = etree.SubElement(assessment_ref, "assessmentItemRef",
			identifier=base_name,
			href=f"{file_name}")
		#assessment_ref.append(item_ref)
	test_part.append(assessment_ref)

	return test_part

#==============
#==============
def dummy_test_run():
	# Generate assessment_meta00001.xml
	assessment_file_name_list = [
		'item_00001.xml',
		'item_00002.xml',
		#'item_00003.xml',
	]
	package_name = "Questions about Blah Blah Blah"
	assessment_meta_etree = generate_assessment_meta(package_name, assessment_file_name_list)

	#write to file
	assessment_meta_xml_string = etree.tostring(assessment_meta_etree, pretty_print=True,
		xml_declaration=True, encoding="UTF-8")
	assessment_meta_path = "assessment_meta.xml"
	with open(assessment_meta_path, "w", encoding="utf-8") as f:
		f.write(assessment_meta_xml_string.decode("utf-8"))

#==============
#==============
if __name__ == "__main__":
	dummy_test_run()


