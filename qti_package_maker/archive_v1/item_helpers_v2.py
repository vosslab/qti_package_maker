
# PIP3 modules
import lxml
import lxml.etree
import random

#==============
def create_assessment_item_header(orig_crc16: str):
	"""
	Create the root <assessmentItem> element with common namespaces and attributes.

	Args:
		N (int): Question ID.
		title (str): Title of the question.

	Returns:
		lxml.etree.Element: The root <assessmentItem> element.
	"""
	rand_crc16 = f"{random.randrange(16**4):04x}"
	identifier = f"QUE__{orig_crc16}_{rand_crc16}"
	nsmap = {
		None: "http://www.imsglobal.org/xsd/imsqti_v2p1",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance",
	}
	item_tree = lxml.etree.Element(
		"assessmentItem",
		nsmap=nsmap,
		attrib={
			"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": (
				"http://www.imsglobal.org/xsd/imsqti_v2p1 "
				"http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1.xsd"
			),
			"title": orig_crc16,
			"adaptive": "false",
			"timeDependent": "false",
			"identifier": identifier,
		},
	)
	return item_tree

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

