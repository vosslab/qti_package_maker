#!/usr/bin/env python3

# Standard Library
#import html
#import random

# PIP3 modules
import lxml.etree

#==============================================================
def create_assessment_items_file_xml_header() -> lxml.etree.Element:
	""" Create the root <questestinterop> element with common namespaces and attributes. """
	nsmap = {
		None: "http://www.imsglobal.org/xsd/ims_qtiasiv1p2",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance",
	}

	# Create the root element <questestinterop>
	assessment_items_file_xml_root = lxml.etree.Element(
		"questestinterop",
		nsmap=nsmap,
		attrib={
			"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": (
				"http://www.imsglobal.org/xsd/ims_qtiasiv1p2 "
				"http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd"
			),
		},
	)
	return assessment_items_file_xml_root

#==============================================================
def create_itemmetadata(choice_ids_list: list, question_type: str):
	"""Create the <itemmetadata> section with QTI metadata fields."""
	itemmetadata = lxml.etree.Element("itemmetadata")
	qtimetadata = lxml.etree.SubElement(itemmetadata, "qtimetadata")

	# Define QTI metadata fields
	metadata_fields = [
		("question_type", question_type),
		("points_possible", "1.0"),
		("original_answer_ids", ','.join(choice_ids_list))
	]

	for field_label, field_entry in metadata_fields:
		field = lxml.etree.SubElement(qtimetadata, "qtimetadatafield")
		lxml.etree.SubElement(field, "fieldlabel").text = field_label
		lxml.etree.SubElement(field, "fieldentry").text = field_entry

	return itemmetadata

#==============================================================
def create_material_mattext(question_text: str):
	"""Create the <material> section inside <presentation>."""
	material = lxml.etree.Element("material")
	mattext = lxml.etree.SubElement(material, "mattext", texttype="text/html")
	# Question text in HTML format
	mattext.text = question_text
	return material

#==============================================================
def create_choice_response_lid(choices_list: list, cardinality: str="Single"):
	"""Create the <response_lid> section with <render_choice> and answer options."""
	response_lid = lxml.etree.Element("response_lid", ident="response1", rcardinality=cardinality)
	render_choice = lxml.etree.SubElement(response_lid, "render_choice")

	# Create choices
	for index, choice_text in enumerate(choices_list, start=1):
		choice_id = f"choice_{index:03d}"
		response_label = lxml.etree.SubElement(render_choice, "response_label", ident=choice_id)
		material = lxml.etree.SubElement(response_label, "material")
		mattext = lxml.etree.SubElement(material, "mattext", texttype="text/html")
		mattext.text = choice_text  # Set choice text
	return response_lid

#==============================================================
def create_matching_response_lid(prompts_list: list, choices_list: list):
	"""Create the <response_lid> sections for matching questions."""
	response_lids = []
	# Iterate through answers and create a <response_lid> for each one
	for i, prompt_text in enumerate(prompts_list):
		response_lid = lxml.etree.Element("response_lid", ident=f"response_{i+1:03d}")
		#response_lid = lxml.etree.Element("response_lid", ident=f"prompt{i + 1}")

		# Add the main item (left-side term)
		material = lxml.etree.SubElement(response_lid, "material")
		mattext = lxml.etree.SubElement(material, "mattext", texttype="text/html")
		mattext.text = prompt_text  # Example: "orange", "banana", "lettuce"

		# Create <render_choice> section for match options
		render_choice = lxml.etree.SubElement(response_lid, "render_choice")

		# Add each matching choice as a response_label
		for j, choice_text in enumerate(choices_list):
			response_label = lxml.etree.SubElement(render_choice, "response_label", ident=f"choice_{j+1:03d}")
			label_material = lxml.etree.SubElement(response_label, "material")
			label_mattext = lxml.etree.SubElement(label_material, "mattext")
			label_mattext.text = choice_text  # Example: "orange", "yellow", "green", "distractor"

		response_lids.append(response_lid)

	return response_lids

#==============================================================
def _create_base_outcomes():
	"""
	Create the base <resprocessing> structure with <outcomes> and <decvar>.

	Returns:
		lxml.etree.Element: The <resprocessing> XML element.
	"""
	resprocessing = lxml.etree.Element("resprocessing")

	# Define outcomes (scoring)
	outcomes = lxml.etree.SubElement(resprocessing, "outcomes")
	lxml.etree.SubElement(outcomes, "decvar", maxvalue="100", minvalue="0", varname="SCORE", vartype="Decimal")

	return resprocessing

#==============================================================
def create_MC_resprocessing(choices_list, answer_text):
	"""
	Create the <resprocessing> section for Multiple Choice (Single Answer) questions.
	"""
	# Get the base <resprocessing>
	resprocessing = _create_base_outcomes()

	# Define response condition
	respcondition = lxml.etree.SubElement(resprocessing, "respcondition")
	conditionvar = lxml.etree.SubElement(respcondition, "conditionvar")

	# Multiple Choice (Single) → NO `<and>`, NO `<not>`, just a single `<varequal>`
	correct_choice_id = f"choice_{choices_list.index(answer_text)+1:03d}"
	lxml.etree.SubElement(conditionvar, "varequal", respident="response1").text = correct_choice_id

	# Assign full 100 points only if the condition is met
	lxml.etree.SubElement(respcondition, "setvar", action="Set", varname="SCORE").text = "100"

	return resprocessing

#==============================================================
def create_MA_resprocessing(choices_list, answers_list):
	"""
	Create the <resprocessing> section, automatically sorting correct and incorrect answers.
	"""
	# Get the base <resprocessing>
	resprocessing = _create_base_outcomes()

	# Define response condition
	respcondition = lxml.etree.SubElement(resprocessing, "respcondition")
	conditionvar = lxml.etree.SubElement(respcondition, "conditionvar")
	and_condition = lxml.etree.SubElement(conditionvar, "and")

	# Add correct answer conditions
	for i, choice_text in enumerate(choices_list):
		choice_id = f"choice_{i+1:03d}"
		if choice_text in answers_list:
			lxml.etree.SubElement(and_condition, "varequal", respident="response1").text = choice_id
		else:
			not_condition = lxml.etree.SubElement(and_condition, "not")
			lxml.etree.SubElement(not_condition, "varequal", respident="response1").text = choice_id

	# Assign full 100 points only if the condition is met
	lxml.etree.SubElement(respcondition, "setvar", action="Set", varname="SCORE").text = "100"

	return resprocessing

#==============================================================
def create_MATCH_resprocessing(prompts_list: list):
	"""
	Create the <resprocessing> section for matching questions, assigning scores for each match.
	"""
	# Get the base <resprocessing>
	resprocessing = _create_base_outcomes()

	# Distribute points evenly
	base_score = round(100 / len(prompts_list), 2)

	# Create conditions for each correct match
	for i in range(len(prompts_list)):
		respcondition = lxml.etree.SubElement(resprocessing, "respcondition")
		conditionvar = lxml.etree.SubElement(respcondition, "conditionvar")

		# Match the correct response
		lxml.etree.SubElement(conditionvar, "varequal", respident=f"response_{i+1:03d}").text = f"choice_{i+1:03d}"
		#lxml.etree.SubElement(conditionvar, "varequal", respident=f"prompt{i + 1}").text = f"choice_{i + 1}"

		# Assign a portion of the score
		lxml.etree.SubElement(respcondition, "setvar", varname="SCORE", action="Add").text = f"{base_score:.2f}"

	return resprocessing

#==============================================================
#==============================================================
def dummy_test_run():
	"""
	Run a test generation of assessment XML.
	"""
	assessment_xml = create_assessment_items_file_xml_header(
		assessment_id="qti12_questions",
		assessment_title="minimal_qti_1.2_sample",
		section_id="root_section"
	)

	# Pretty print XML
	assessment_xml_string = lxml.etree.tostring(
		assessment_xml, pretty_print=True, xml_declaration=True, encoding="UTF-8"
	)

	# Save to file
	with open("assessment.xml", "w", encoding="utf-8") as f:
		f.write(assessment_xml_string.decode("utf-8"))

#==============
if __name__ == "__main__":
	dummy_test_run()
