
# PIP3 modules
import xml.etree.ElementTree as ET

def create_assessment_item(N: int, title: str) -> ET.Element:
	"""
	Create the root <assessmentItem> element with common namespaces and attributes.

	Args:
		N (int): Question ID.
		title (str): Title of the question.

	Returns:
		ET.Element: The root <assessmentItem> element.
	"""
	# Namespaces
	ns = {
		"": "http://www.imsglobal.org/xsd/imsqti_v2p1",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance"
	}
	ET.register_namespace("", ns[""])
	ET.register_namespace("xsi", ns["xsi"])

	# Create root element
	assessment_item = ET.Element(
		"assessmentItem",
		{
			"xmlns": ns[""],
			"xmlns:xsi": ns["xsi"],
			"xsi:schemaLocation": (
				"http://www.imsglobal.org/xsd/imsqti_v2p1 "
				"http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1.xsd"
			),
			"title": title,
			"adaptive": "false",
			"timeDependent": "false",
			#TODO make this a timestamp instead??
			"identifier": f"QUE__{N}"
		}
	)
	return assessment_item


def add_item_body(parent: ET.Element, question: str, choices: list):
	"""
	Add the <itemBody> element with the question text and choices.

	Args:
		parent (ET.Element): Parent element to add the item body to.
		question (str): The question text.
		choices (list): List of choices.
	"""
	item_body = ET.SubElement(parent, "itemBody")
	div = ET.SubElement(item_body, "div")
	ET.SubElement(div, "p").text = question

	# Add choices
	choice_interaction = ET.SubElement(item_body, "choiceInteraction", {
		"responseIdentifier": "RESPONSE",
		"maxChoices": "1",
		"shuffle": "true"
	})
	for idx, choice in enumerate(choices, start=1):
		simple_choice = ET.SubElement(
			choice_interaction, "simpleChoice",
			{"identifier": f"answer_{idx}", "fixed": "true"}
		)
		ET.SubElement(simple_choice, "p").text = choice

def add_response_processing(parent: ET.Element, response_id: str):
	"""
	Add <responseProcessing> logic to the XML.

	Args:
		parent (ET.Element): Parent element to add the response processing to.
		response_id (str): Identifier for the response.
	"""
	response_processing = ET.SubElement(parent, "responseProcessing")
	response_condition = ET.SubElement(response_processing, "responseCondition")
	response_if = ET.SubElement(response_condition, "responseIf")

	# Match correct response
	match = ET.SubElement(response_if, "match")
	ET.SubElement(match, "variable", {"identifier": response_id})
	ET.SubElement(match, "correct", {"identifier": response_id})

	# Set outcome values for correct response
	set_outcome_value = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "SCORE"})
	ET.SubElement(set_outcome_value, "variable", {"identifier": "MAXSCORE"})

	feedback_if = ET.SubElement(response_if, "setOutcomeValue", {"identifier": "FEEDBACKBASIC"})
	ET.SubElement(feedback_if, "baseValue", {"baseType": "identifier"}).text = "correct_fb"

	# Response else
	response_else = ET.SubElement(response_condition, "responseElse")
	feedback_else = ET.SubElement(response_else, "setOutcomeValue", {"identifier": "FEEDBACKBASIC"})
	ET.SubElement(feedback_else, "baseValue", {"baseType": "identifier"}).text = "incorrect_fb"

def add_outcome_declarations(parent: ET.Element):
	"""
	Add common <outcomeDeclaration> elements to the XML.

	Args:
		parent (ET.Element): Parent element to add the outcome declarations to.
	"""
	ET.SubElement(
		parent, "outcomeDeclaration",
		{"identifier": "SCORE", "cardinality": "single", "baseType": "float"}
	)
	ET.SubElement(
		parent, "outcomeDeclaration",
		{"identifier": "FEEDBACKBASIC", "cardinality": "single", "baseType": "identifier"}
	)
	ET.SubElement(
		parent, "outcomeDeclaration",
		{"identifier": "MAXSCORE", "cardinality": "single", "baseType": "float"}
	)

def add_response_declaration(parent: ET.Element, response_id: str, correct_values: list):
	"""
	Add a <responseDeclaration> to the XML with correct responses.

	Args:
		parent (ET.Element): Parent element to add the response declaration to.
		response_id (str): Identifier for the response.
		correct_values (list): List of correct response values.
	"""
	response_declaration = ET.SubElement(
		parent, "responseDeclaration",
		{
			"identifier": response_id,
			"cardinality": "single" if len(correct_values) == 1 else "multiple",
			"baseType": "identifier"
		}
	)
	correct_response = ET.SubElement(response_declaration, "correctResponse")
	for value in correct_values:
		ET.SubElement(correct_response, "value").text = value


