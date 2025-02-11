#!/usr/bin/env python3

import os
from lxml import etree

#==============
def generate_manifest(assessment_file_name_list: list[str]) -> etree.ElementTree:
	"""
	Generates the imsmanifest.xml file as an lxml ElementTree.

	Args:
		assessment_file_name_list (list[str]): List of assessment item file names.

	Returns:
		etree.ElementTree: The generated XML tree for imsmanifest.xml.
	"""
	assessment_file_name_list.sort()
	manifest = create_manifest_header()
	metadata = create_metadata_section()
	#organizations = etree.Element("organizations")
	resources = create_resources_section(assessment_file_name_list)

	# Add sections to the manifest
	manifest.append(metadata)
	#manifest.append(organizations)
	manifest.append(resources)

	return etree.ElementTree(manifest)

def create_manifest_header() -> etree.Element:
	"""
	Creates the header element for the manifest, including namespaces and identifiers.

	Returns:
		etree.Element: The root 'manifest' element with attributes.
	"""
	# Define namespaces
	nsmap = {
		None: "http://www.imsglobal.org/xsd/imscp_v1p1",  # Default namespace
		"imsmd": "http://www.imsglobal.org/xsd/imsmd_v1p2",
		"lom": "http://ltsc.ieee.org/xsd/LOM",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance",
	}

	# Create the root element with namespaces and identifier attribute
	manifest = etree.Element("manifest", nsmap=nsmap, identifier="main_manifest")

	# Define the xsi:schemaLocation attribute with proper pairs
	manifest.attrib["{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"] = (
		"http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd "
		"http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2.xsd "
		"http://ltsc.ieee.org/xsd/LOM http://ieee-sa.imeetcentral.com/ltsc/"
	)

	return manifest

#==============
def create_metadata_section(version="1.2") -> etree.Element:
	"""
	Creates the metadata section of the manifest.

	Returns:
		etree.Element: The 'metadata' element with its child elements.
	"""
	metadata = etree.Element("metadata")
	schema = etree.SubElement(metadata, "schema")
	schema.text = f"QTIv{version}"

	schema_version = etree.SubElement(metadata, "schemaversion")
	if version.startswith("2"):
		schema_version.text = "2.0"
	else:
		schema_version.text = "1.1.3"

	return metadata

#==============
def create_resources_section(assessment_file_name_list: list[str]) -> etree.Element:
	"""
	Creates the resources section of the manifest, adding each assessment item.

	Args:
		assessment_file_name_list (list[str]): List of assessment item file names.

	Returns:
		etree.Element: The 'resources' element containing resource elements.
	"""
	resources = etree.Element("resources")

	# Create the question bank resource
	question_bank_resource = etree.Element(
		"resource",
		href="qti21/question_bank00001.xml",
		identifier="question_bank00001",
		type="imsqti_test_xmlv2p1"
	)
	etree.SubElement(question_bank_resource, "file", href="qti21/question_bank00001.xml")

	# Add dependencies for each assessment item file
	for file_name in assessment_file_name_list:
		base_name = os.path.splitext(file_name)[0]
		etree.SubElement(
			question_bank_resource,
			"dependency",
			identifierref=base_name
		)

	resources.append(question_bank_resource)

	# Create individual assessment item resources
	for file_name in assessment_file_name_list:
		base_name = os.path.splitext(file_name)[0]
		resource = etree.Element(
			"resource",
			href=f"qti21/{file_name}",
			identifier=base_name,
			type="imsqti_item_xmlv2p1"
		)
		etree.SubElement(resource, "file", href=f"qti21/{file_name}")
		resources.append(resource)

	return resources

#==============
#==============
def dummy_test_run():
	# Generate imsmanifest.xml
	assessment_file_name_list = [
		'assessmentItem00001.xml',
		'assessmentItem00002.xml',
		'assessmentItem00003.xml',
	]
	manifest_etree = generate_manifest(assessment_file_name_list)
	manifest_xml_string = etree.tostring(manifest_etree, pretty_print=True,
		xml_declaration=True, encoding="UTF-8")
	manifest_path = "imsmanifest.xml"
	with open(manifest_path, "w", encoding="utf-8") as f:
		f.write(manifest_xml_string.decode("utf-8"))

#==============
#==============
if __name__ == "__main__":
	dummy_test_run()
