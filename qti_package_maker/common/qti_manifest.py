#!/usr/bin/env python3

import os
import datetime
from lxml import etree

#========================================================
def generate_manifest(
			package_name: str,
			assessment_file_name_list: list,
			version: str = "1.2"):
	"""
	Generates the imsmanifest.xml file as an lxml ElementTree.

	Args:
		assessment_file_name_list (list[str]): List of assessment item file names.

	Returns:
		etree.ElementTree: The generated XML tree for imsmanifest.xml.
	"""
	if not assessment_file_name_list:
		raise ValueError("no assessment files provided")
	if version.startswith("1"):
		if len(assessment_file_name_list) > 1:
			raise ValueError("QTI version 1, only supports one assessment_file")
		file_name = assessment_file_name_list[0]
		base_name = os.path.splitext(os.path.basename(file_name))[0]
		dir_name = os.path.dirname(file_name)
		if base_name != dir_name:
			raise ValueError("QTI version 1, requires file_name to match dir_name")

	manifest = create_manifest_header()
	metadata = create_metadata_section(package_name, version)
	#organizations = etree.Element("organizations")
	sorted_file_list = sorted(assessment_file_name_list)
	resources = create_resources_section(sorted_file_list, version)



	# Add sections to the manifest
	manifest.append(metadata)
	#manifest.append(organizations)
	manifest.append(resources)

	return etree.ElementTree(manifest)

#========================================================
def create_manifest_header() -> etree.Element:
	"""
	Creates the header element for the manifest, including namespaces and identifiers.

	Returns:
		etree.Element: The root 'manifest' element with attributes.
	"""
	# Define namespaces
	nsmap = {
		None: "http://www.imsglobal.org/xsd/imscp_v1p1",  # Default namespace
		"lom": "http://ltsc.ieee.org/xsd/LOM",
		"imsmd": "http://www.imsglobal.org/xsd/imsmd_v1p2",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance",
	}

	# Create the root element with namespaces and identifier attribute
	manifest = etree.Element("manifest", nsmap=nsmap, identifier="main manifest")

	# Define the xsi:schemaLocation attribute with correct values
	manifest.attrib["{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"] = (
		"http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd "
		"http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2.xsd "
		"http://ltsc.ieee.org/xsd/LOM http://ieee-sa.imeetcentral.com/ltsc/"
	)

	return manifest

#========================================================
def create_metadata_section(package_name: str, version: str = "1.2") -> etree.Element:
	"""
	Creates the metadata section of the manifest.

	Args:
		package_name (str): The name of the package.
		version (str): The version of QTI (default is "1.2").

	Returns:
		etree.Element: The 'metadata' element with its child elements.
	"""
	# Define the IMSMD namespace
	ns_imsmd = "http://www.imsglobal.org/xsd/imsmd_v1p2"

	# Create the root metadata element
	metadata = etree.Element("metadata")

	# Add schema and schemaversion
	schema = etree.SubElement(metadata, "schema")
	schema.text = f"QTIv{version}"

	schema_version = etree.SubElement(metadata, "schemaversion")
	if version.startswith("2"):
		schema_version.text = "2.0"
	else:
		schema_version.text ="1.1.3"

	# Create the <imsmd:lom> structure
	lom = etree.SubElement(metadata, f"{{{ns_imsmd}}}lom", nsmap={"imsmd": ns_imsmd})

	# <imsmd:general> section
	general = etree.SubElement(lom, f"{{{ns_imsmd}}}general")
	title = etree.SubElement(general, f"{{{ns_imsmd}}}title")
	title_string = etree.SubElement(title, f"{{{ns_imsmd}}}string")
	title_string.text = package_name

	# <imsmd:lifeCycle> section
	life_cycle = etree.SubElement(lom, f"{{{ns_imsmd}}}lifeCycle")
	contribute = etree.SubElement(life_cycle, f"{{{ns_imsmd}}}contribute")

	# Get the current date in ISO format (YYYY-MM-DD)
	current_date = datetime.date.today().isoformat()
	date = etree.SubElement(contribute, f"{{{ns_imsmd}}}date")
	date_time = etree.SubElement(date, f"{{{ns_imsmd}}}dateTime")
	date_time.text = current_date

	# <imsmd:rights> section
	rights = etree.SubElement(lom, f"{{{ns_imsmd}}}rights")

	# CC BY 4.0 License
	description = etree.SubElement(rights, f"{{{ns_imsmd}}}description")
	license_string = etree.SubElement(description, f"{{{ns_imsmd}}}string")
	license_string.text = "CC Attribution - http://creativecommons.org/licenses/by/4.0"

	return metadata

#========================================================
def create_resources_section(assessment_file_name_list: list[str], version: str = "1.2") -> etree.Element:
	"""
	Creates the resources section of the manifest, adding each assessment item.

	Args:
		assessment_file_name_list (list[str]): List of assessment item file names.

	Returns:
		etree.Element: The 'resources' element containing resource elements.
	"""
	resources = etree.Element("resources")

	if version.startswith("2"):
		meta_type = "imsqti_test_xmlv2p1"
		item_type = "imsqti_item_xmlv2p1"
	else:
		meta_type = "imsqti_xmlv1p2"
		item_type = "imsqti_item_xmlv1p2"

	dir_name = os.path.dirname(assessment_file_name_list[0])
	meta_file_path = f"{dir_name}/assessment_meta.xml"

	# Create the assessment meta resource (we will add dependencies later)
	assessment_meta_resource = etree.Element(
		"resource",
		identifier="assessment_meta",
		type=meta_type,
		#href=meta_file_path,
	)
	etree.SubElement(assessment_meta_resource, "file", href=meta_file_path)

	# Create individual assessment item resources
	for file_name in assessment_file_name_list:
		base_name = os.path.splitext(os.path.basename(file_name))[0]
		resource = etree.Element(
			"resource",
			identifier=base_name,
			type=item_type,
		)
		etree.SubElement(resource, "file", href=file_name)

		# Add dependency to assessment_meta
		etree.SubElement(resource, "dependency", identifierref="assessment_meta")

		# Also add reverse dependency in assessment_meta
		etree.SubElement(assessment_meta_resource, "dependency", identifierref=base_name)

		resources.append(resource)

	# Append assessment_meta after all assessment items
	resources.append(assessment_meta_resource)

	return resources

#========================================================
def dummy_test_run():
	# Generate imsmanifest.xml
	assessment_file_name_list = [
		'qti21_items/assessmentItem00001.xml',
		'qti21_items/assessmentItem00002.xml',
		#'qti21_items/assessmentItem00003.xml',
	]
	manifest_etree = generate_manifest("dummy set", assessment_file_name_list, version="2.1")
	manifest_xml_string = etree.tostring(manifest_etree, pretty_print=True,
		xml_declaration=True, encoding="UTF-8")
	manifest_path = "imsmanifest_v2_1.xml"
	with open(manifest_path, "w", encoding="utf-8") as f:
		f.write(manifest_xml_string.decode("utf-8"))

	# Generate imsmanifest.xml
	assessment_file_name_list = [
		'qti12_items/qti12_items.xml',
	]
	manifest_etree = generate_manifest("dummy set", assessment_file_name_list, version="1.2")
	manifest_xml_string = etree.tostring(manifest_etree, pretty_print=True,
		xml_declaration=True, encoding="UTF-8")
	manifest_path = "imsmanifest_v1_2.xml"
	with open(manifest_path, "w", encoding="utf-8") as f:
		f.write(manifest_xml_string.decode("utf-8"))

#========================================================
if __name__ == "__main__":
	dummy_test_run()
