
import html
import random

# PIP3 modules
import lxml.html
import lxml.etree

#==============
def create_assessment_item_header(question_crc16: str):
	"""
	Create the root <assessmentItem> element with common namespaces and attributes.
	"""
	rand_crc16 = f"{random.randrange(16**4):04x}"
	identifier = f"{question_crc16}_{rand_crc16}"
	item_title = identifier
	# Define all required XML namespaces, including the missing ones
	nsmap = {
		None: "http://www.imsglobal.org/xsd/imsqti_v2p1",  # Default namespace
		"xsi": "http://www.w3.org/2001/XMLSchema-instance",
		"ns8": "http://www.w3.org/1999/xlink",
		"ns9": "http://www.imsglobal.org/xsd/apip/apipv1p0/imsapip_qtiv1p0"
	}
	# Create the root <assessmentItem> element with required attributes
	item_tree = lxml.etree.Element(
		"assessmentItem",
		nsmap=nsmap,
		attrib={
			"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": (
				"http://www.imsglobal.org/xsd/imsqti_v2p1 "
				"http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1.xsd"
			),
			"title": item_title,
			"adaptive": "false",
			"timeDependent": "false",
			"identifier": identifier,
		},
	)
	return item_tree

#==============
def create_response_declaration(correct_values: list) -> lxml.etree.Element:
	## IMPORTANT !!!
	"""
	Create a <responseDeclaration> element.
	Returns:
		lxml.etree.Element: The <responseDeclaration> element.
  <responseDeclaration cardinality="multiple" baseType="identifier" identifier="RESPONSE">
    <correctResponse>
      <value>answer_1</value>
      <value>answer_2</value>
    </correctResponse>
  </responseDeclaration>
	"""
	responseDeclaration = lxml.etree.Element(
		"responseDeclaration",
		attrib={
			"baseType": "identifier",
			"cardinality": "single" if len(correct_values) == 1 else "multiple",
			"identifier": "RESPONSE",
		},
	)
	correct_response = lxml.etree.SubElement(responseDeclaration, "correctResponse")
	for value in correct_values:
		lxml.etree.SubElement(correct_response, "value").text = value
	return responseDeclaration

#==============
def create_response_declaration_FIB(answers_list: list) -> lxml.etree.Element:
	## IMPORTANT !!!
	responseDeclaration = lxml.etree.Element(
		"responseDeclaration",
		attrib={
			"baseType": "string",
			"cardinality": "single",
			"identifier": "RESPONSE",
		},
	)
	# Create <correctResponse> and <mapping>
	correct_response = lxml.etree.SubElement(responseDeclaration, "correctResponse")
	mapping = lxml.etree.SubElement(responseDeclaration, "mapping")
	# Iterate once to create both <value> and <mapEntry>
	for value in answers_list:
		lxml.etree.SubElement(correct_response, "value").text = value
		lxml.etree.SubElement(mapping, "mapEntry", {
			"mapKey": value,
			"caseSensitive": "false",
			"mappedValue": "100.0",
		})
	return responseDeclaration

#==============
def create_item_body(question_html_text: str, choices_list: list, max_choices: int, shuffle: bool=True):
	## IMPORTANT !!!
	"""
	Create the <itemBody> element with the question text and choices.
	"""
	item_body = lxml.etree.Element("itemBody")

	unescaped_text = html.unescape(question_html_text)
	parsed_html = lxml.html.fragment_fromstring(unescaped_text, create_parent='div')
	#if len(parsed_html.getchildren()) > 1:
	#	raise ValueError(f"Question text contains multiple elements: {unescaped_text}")
	item_body.append(parsed_html)

	# Create <choiceInteraction> with proper attributes
	choice_interaction = lxml.etree.SubElement(item_body, "choiceInteraction", {
		"maxChoices": f"{max_choices:d}",
		"responseIdentifier": "RESPONSE",
		"shuffle": str(shuffle).lower(),
	})
	# Add choices without extra <p> tags
	for idx, choice_html_text in enumerate(choices_list, start=1):
		simple_choice = lxml.etree.SubElement(
			choice_interaction, "simpleChoice",
			{
				"fixed": "true",
				"identifier": f"answer_{idx}",
			}
		)
		# Unescape choice text
		unescaped_text = html.unescape(choice_html_text)
		# Ensure choice text is wrapped in <p>
		parsed_choice_html = lxml.html.fragment_fromstring(unescaped_text, create_parent='p')
		# Ensure the parsed choice has only one top-level <p> element
		#if len(parsed_choice_html.getchildren()) > 1:
		#	raise ValueError(f"Choice text contains multiple elements: {choice_html_text}")
		# Append the single <p> element inside <simpleChoice>
		simple_choice.append(parsed_choice_html)
	return item_body

#==============
def create_item_body_FIB(question_html_text: str, choices_list: list):
	## IMPORTANT !!!
	"""
	Create the <itemBody> element with the question text and choices.
	"""
	item_body = lxml.etree.Element("itemBody")

	unescaped_text = html.unescape(question_html_text)
	parsed_html = lxml.html.fragment_fromstring(unescaped_text, create_parent='div')
	#if len(parsed_html.getchildren()) > 1:
	#	raise ValueError(f"Question text contains multiple elements: {question_html_text}")
	item_body.append(parsed_html)

	# Create a <p> wrapper for the <textEntryInteraction> field
	text_entry_p = lxml.etree.SubElement(item_body, "p")
	# Create the <textEntryInteraction> element inside <p>
	lxml.etree.SubElement(text_entry_p, "textEntryInteraction", {
		"responseIdentifier": "RESPONSE"
	})

	return item_body

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
			attrib={
				"baseType": "float",
				"cardinality": "single",
				"identifier": "SCORE",
			},
		)
	]
	return outcome_declare_tree

#==============
def create_outcome_declarations_big() -> list:
	"""
	Create a list of <outcomeDeclaration> elements for SCORE, FEEDBACKBASIC, and MAXSCORE.

	Returns:
		list: A list of <outcomeDeclaration> elements.
	"""
	outcome_declare_tree = []

	# SCORE outcome declaration (Default Value = 0)
	score_declaration = lxml.etree.Element("outcomeDeclaration", {
		"baseType": "float",
		"cardinality": "single",
		"identifier": "SCORE",
	})
	default_value = lxml.etree.SubElement(score_declaration, "defaultValue")
	lxml.etree.SubElement(default_value, "value").text = "0"
	outcome_declare_tree.append(score_declaration)

	# FEEDBACKBASIC outcome declaration (No default value needed)
	feedback_declaration = lxml.etree.Element("outcomeDeclaration", {
		"baseType": "identifier",
		"cardinality": "single",
		"identifier": "FEEDBACKBASIC",
	})
	outcome_declare_tree.append(feedback_declaration)

	# MAXSCORE outcome declaration (Default Value = 0)
	maxscore_declaration = lxml.etree.Element("outcomeDeclaration", {
		"baseType": "float",
		"cardinality": "single",
		"identifier": "MAXSCORE",
	})
	default_value_max = lxml.etree.SubElement(maxscore_declaration, "defaultValue")
	lxml.etree.SubElement(default_value_max, "value").text = "0"
	outcome_declare_tree.append(maxscore_declaration)

	return outcome_declare_tree

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
def create_response_processing_big() -> lxml.etree.Element:
	"""
	Create a <responseProcessing> element with correct feedback and scoring.
	"""
	# Create root <responseProcessing> element
	response_processing = lxml.etree.Element("responseProcessing")

	# Create <responseCondition>
	response_condition = lxml.etree.SubElement(response_processing, "responseCondition")

	# <responseIf> block for correct response
	response_if = lxml.etree.SubElement(response_condition, "responseIf")

	# Match correct response
	match = lxml.etree.SubElement(response_if, "match")
	lxml.etree.SubElement(match, "variable", identifier="RESPONSE")
	lxml.etree.SubElement(match, "correct", identifier="RESPONSE")

	# Assign MAXSCORE when correct
	set_outcome_score = lxml.etree.SubElement(response_if, "setOutcomeValue", identifier="SCORE")
	lxml.etree.SubElement(set_outcome_score, "variable", identifier="MAXSCORE")

	# Set correct feedback value
	set_feedback_correct = lxml.etree.SubElement(response_if, "setOutcomeValue", identifier="FEEDBACKBASIC")
	lxml.etree.SubElement(set_feedback_correct, "baseValue", baseType="identifier").text = "correct_fb"

	# <responseElse> block for incorrect response
	response_else = lxml.etree.SubElement(response_condition, "responseElse")

	# Set incorrect feedback value
	set_feedback_incorrect = lxml.etree.SubElement(response_else, "setOutcomeValue", identifier="FEEDBACKBASIC")
	lxml.etree.SubElement(set_feedback_incorrect, "baseValue", baseType="identifier").text = "incorrect_fb"

	return response_processing

