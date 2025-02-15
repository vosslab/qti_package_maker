ENGINE_NAME = "canvas_qti_v1_2"

# Standard Library

# Pip3 Library
import lxml.etree

# QTI Package Maker
from qti_package_maker.common import string_functions
from qti_package_maker.engine_canvas_qti_v1_2 import item_xml_helpers

#==============
def MC(crc16_text: str, question_text: str, choices_list: list, answer_text: str) -> str:
	"""
	Create a Multiple Choice (Single Answer) question in QTI-compliant XML format.

	Args:
		question_text (str): The question text.
		choices_list (list): List of answer choices.
		answer (str): The correct answer.

	Returns:
		lxml.etree.Element: XML element for the question.
	"""
	assessment_item_etree = lxml.etree.Element("item", ident=crc16_text)
	answer_id = f"answer_{choices_list.index(answer_text) + 1}"
	# takes a list as input
	response_declaration = item_xml_helpers.create_response_declaration([answer_id, ])
	outcome_declarations = item_xml_helpers.create_outcome_declarations()
	item_body = item_xml_helpers.create_item_body(question_text, choices_list, max_choices=1)
	response_processing = item_xml_helpers.create_response_processing()

	# Assemble the XML tree
	assessment_item_etree.append(response_declaration)
	for outcome in outcome_declarations:
		assessment_item_etree.append(outcome)
	assessment_item_etree.append(item_body)
	assessment_item_etree.append(response_processing)

	return assessment_item_etree


def MA(crc16_text: str, question_text: str, choices_list: list, answers_list: list):
	"""
	Create a Multiple Answer question in QTI-compliant XML format.

	Args:
		question_text (str): The question text.
		choices_list (list): List of answer choices.
		answers_list (list): List of correct answers.

	Returns:
		lxml.etree.Element: XML element for the question.
	"""
	assessment_item_etree = xml_helpers.create_assessment_item_header(crc_merge)

	answer_id_list = []
	for answer_text in answers_list:
		answer_id = f"answer_{choices_list.index(answer_text) + 1}"
		answer_id_list.append(answer_id)
	answer_id_list.sort()
	response_declaration = xml_helpers.create_response_declaration(answer_id_list)

	outcome_declarations = xml_helpers.create_outcome_declarations()
	item_body = xml_helpers.create_item_body(question_text, choices_list, max_choices=len(answers_list))
	response_processing = xml_helpers.create_response_processing()

	# Assemble the XML tree
	assessment_item_etree.append(response_declaration)
	for outcome in outcome_declarations:
		assessment_item_etree.append(outcome)
	assessment_item_etree.append(item_body)
	assessment_item_etree.append(response_processing)
	return assessment_item_etree


def FIB(crc16_text: str, question_text: str,  answers_list):
	raise NotImplementedError

def FIB_PLUS(crc16_text: str, question_text: str, answer_map: dict) -> str:
	raise NotImplementedError

def NUM(crc16_text: str, question_text: str,  answer, tolerance, tol_message=True):
	raise NotImplementedError

def MATCH(crc16_text: str, question_text: str,  answers_list, matching_list):
	raise NotImplementedError

def ORDER(crc16_text: str, question_text: str,  ordered_answers_list):
	raise NotImplementedError
