
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import string_functions
from qti_package_maker.engine_blackboard_qti_v2_1 import item_xml_helpers

#==============================================================
def MC(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	assessment_item_etree = xml_helpers.create_assessment_item_header(crc_merge)
	answer_id = f"answer_{choices_list.index(answer_text) + 1}"
	# takes a list as input
	response_declaration = xml_helpers.create_response_declaration([answer_id, ])
	outcome_declarations = xml_helpers.create_outcome_declarations()
	item_body = xml_helpers.create_item_body(question_text, choices_list, max_choices=1)
	response_processing = xml_helpers.create_response_processing()

	# Assemble the XML tree
	assessment_item_etree.append(response_declaration)
	for outcome in outcome_declarations:
		assessment_item_etree.append(outcome)
	assessment_item_etree.append(item_body)
	assessment_item_etree.append(response_processing)

	return assessment_item_etree

#==============================================================
def MA(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_list: list):
	"""Create a Multiple Answer (Checkboxes) question."""
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

#==============================================================
def MATCH(item_number: int, crc16_text: str, question_text: str, answers_list: list, matching_list: list):
	"""Create a Matching question where users match items from two lists."""
	pass

#==============================================================
def NUM(item_number: int, crc16_text: str, question_text: str, answer: float, tolerance: float, tol_message=True):
	"""Create a Numerical question with an accepted tolerance range."""
	pass

#==============================================================
def FIB(item_number: int, crc16_text: str, question_text: str, answers_list: list):
	"""Create a Fill-in-the-Blank (Single Blank) question."""
	pass

#==============================================================
def MULTI_FIB(item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping."""
	pass

#==============================================================
def ORDER(item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	"""Create an Ordered List question where users arrange items in a correct sequence."""
	pass
