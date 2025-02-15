#!/usr/bin/env python3

# PIP3 modules
import lxml
import lxml.etree
import random

#==============
def create_assessment_items_file_xml_header() -> lxml.etree.Element:
	"""
	Create the root <questestinterop> element with common namespaces and attributes.
	Also adds <assessment> and <section> elements.

	Args:
		assessment_id (str): Unique identifier for the assessment.
		assessment_title (str): Title of the assessment.
		section_id (str): Unique identifier for the root section.

	Returns:
		lxml.etree.Element: The root <questestinterop> element with <assessment> and <section>.
	"""
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

	# Add <assessment>
	#assessment = lxml.etree.SubElement(questestinterop, "assessment", ident=assessment_id, title=assessment_title)

	# Add <section>
	#section = lxml.etree.SubElement(assessment, "section", ident=section_id)

	return assessment_items_file_xml_root

#==============
def create_response_declaration(correct_values: list) -> lxml.etree.Element:
	"""
	Create a <responseDeclaration> element.

	Args:
		response_id (str): Identifier for the response.
		correct_values (list): List of correct response values.

	Returns:
		lxml.etree.Element: The <responseDeclaration> element.
  <responseDeclaration cardinality="multiple" baseType="identifier" identifier="RESPONSE">
    <correctResponse>
      <value>answer_1</value>
      <value>answer_2</value>
    </correctResponse>
  </responseDeclaration>

	"""
	element = lxml.etree.Element(
		"responseDeclaration",
		attrib={
			"identifier": "RESPONSE",
			"cardinality": "single" if len(correct_values) == 1 else "multiple",
			"baseType": "identifier",
		},
	)
	correct_response = lxml.etree.SubElement(element, "correctResponse")
	for value in correct_values:
		lxml.etree.SubElement(correct_response, "value").text = value
	return element

#==============
def create_outcome_declarations() -> list:
	"""
	Create a minimal list of <outcomeDeclaration> elements.

	Returns:
		list: A list of <outcomeDeclaration> elements.
	"""
	outcome_declare_tree = [
		lxml.etree.Element(
			"outcomeDeclaration",
			attrib={"identifier": "SCORE", "cardinality": "single", "baseType": "float"},
		)
	]
	return outcome_declare_tree

#==============
def create_item_body(question_html_text: str, choices_list: list, max_choices: int, shuffle: bool=True):
	"""
	Create the <itemBody> element with the question text and choices.

	Args:
		question (str): The question text.
		choices (list): List of choices.

	Returns:
		lxml.etree.Element: The <itemBody> element.
	"""
	item_body = lxml.etree.Element("itemBody")
	div = lxml.etree.SubElement(item_body, "div")
	lxml.etree.SubElement(div, "p").text = question_html_text

	choice_interaction = lxml.etree.SubElement(item_body, "choiceInteraction", {
		"responseIdentifier": "RESPONSE",
		"maxChoices": f"{max_choices:d}",
		"shuffle": f"{str(shuffle).lower()}",
	})
	for idx, choice_html_text in enumerate(choices_list, start=1):
		simple_choice = lxml.etree.SubElement(
			choice_interaction, "simpleChoice",
			{"identifier": f"answer_{idx}", "fixed": "true"}
		)
		lxml.etree.SubElement(simple_choice, "p").text = choice_html_text
	return item_body

#==============
def create_response_processing() -> lxml.etree.Element:
	"""
	Create a minimal <responseProcessing> element compatible with Canvas and Blackboard.

	Args:
		response_id (str): Identifier for the response.

	Returns:
		lxml.etree.Element: The minimal <responseProcessing> element.
	"""
	response_processing = lxml.etree.Element("responseProcessing")
	response_condition = lxml.etree.SubElement(response_processing, "responseCondition")
	response_if = lxml.etree.SubElement(response_condition, "responseIf")

	# Match correct response
	match = lxml.etree.SubElement(response_if, "match")
	lxml.etree.SubElement(match, "variable", {"identifier": "RESPONSE"})
	lxml.etree.SubElement(match, "correct", {"identifier": "RESPONSE"})

	return response_processing


#==============
def dummy_test_run():
	"""
	Run a test generation of assessment XML.
	"""
	assessment_xml = create_assessment_xml_header(
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
