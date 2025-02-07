
# Standard Library

# Pip3 Library

# QTI Package Maker
import item_helpers
import string_functions

#==============
def MC(question_text: str, choices_list: list, answer_text: str):
	"""
	Create a Multiple Choice (Single Answer) question in QTI-compliant XML format.

	Args:
		question_text (str): The question text.
		choices_list (list): List of answer choices.
		answer (str): The correct answer.

	Returns:
		lxml.etree.Element: XML element for the question.
	"""
	if len(choices_list) <= 1:
		raise ValueError("not enough choices to choose from, you need two choices for multiple choice")
	if answer_text not in choices_list:
		raise ValueError("Error: The correct answer is not in the list of choices.")
	if choices_list.count(answer_text) > 1:
		raise ValueError("Error: The correct answer appears more than once in list of choices.")
	if len(choices_list) > len(set(choices_list)):
		raise ValueError("Error: Duplicate choices.")

	crc16question = string_functions.get_crc16_from_string(question_text)
	choices_str = '|'.join(choices_list)
	crc16choice = string_functions.get_crc16_from_string(choices_str)
	crc_merge = f"{crc16question}_{crc16choice}"

	assessment_item_etree = item_helpers.create_assessment_item_header(crc_merge)
	answer_id = f"answer_{choices_list.index(answer_text) + 1}"
	# takes a list as input
	response_declaration = item_helpers.create_response_declaration([answer_id, ])
	outcome_declarations = item_helpers.create_outcome_declarations()
	item_body = item_helpers.create_item_body(question_text, choices_list, max_choices=1)
	response_processing = item_helpers.create_response_processing()

	# Assemble the XML tree
	assessment_item_etree.append(response_declaration)
	for outcome in outcome_declarations:
		assessment_item_etree.append(outcome)
	assessment_item_etree.append(item_body)
	assessment_item_etree.append(response_processing)

	return assessment_item_etree


def MA(question_text: str, choices_list: list, answers_list: list):
	"""
	Create a Multiple Answer question in QTI-compliant XML format.

	Args:
		question_text (str): The question text.
		choices_list (list): List of answer choices.
		answers_list (list): List of correct answers.

	Returns:
		lxml.etree.Element: XML element for the question.
	"""
	# Check for a minimum number of choices and duplicates
	if len(choices_list) < 3:
		raise ValueError("You need at least three choices for a multiple answer question.")

	choices_set = set(choices_list)
	if len(choices_list) > len(choices_set):
		raise ValueError("Duplicate choices are not allowed.")

	# Check for multiple answers and duplicates in answers
	if len(answers_list) < 2:
		raise ValueError("You need at least two correct answers for a multiple answer question.")

	answers_set = set(answers_list)
	if len(answers_list) > len(answers_set):
		raise ValueError("Duplicate answers are not allowed.")

	# Check that there is at least one non-answer (choice that is not in answers_set)
	if choices_set == answers_set:
		raise ValueError("There must be at least one non-answer choice.")

	# Ensure all answers are valid choices
	if not answers_set.issubset(choices_set):
		raise ValueError("One or more correct answers are not in the list of choices.")

	crc16question = string_functions.get_crc16_from_string(question_text)
	choices_str = '|'.join(choices_list)
	crc16choice = string_functions.get_crc16_from_string(choices_str)
	crc_merge = f"{crc16question}_{crc16choice}"

	assessment_item_etree = item_helpers.create_assessment_item_header(crc_merge)

	answer_id_list = []
	for answer_text in answers_list:
		answer_id = f"answer_{choices_list.index(answer_text) + 1}"
		answer_id_list.append(answer_id)
	answer_id_list.sort()
	response_declaration = item_helpers.create_response_declaration(answer_id_list)

	outcome_declarations = item_helpers.create_outcome_declarations()
	item_body = item_helpers.create_item_body(question_text, choices_list, max_choices=len(answers_list))
	response_processing = item_helpers.create_response_processing()

	# Assemble the XML tree
	assessment_item_etree.append(response_declaration)
	for outcome in outcome_declarations:
		assessment_item_etree.append(outcome)
	assessment_item_etree.append(item_body)
	assessment_item_etree.append(response_processing)
	return assessment_item_etree


def FIB(question_text: str,  answers_list):
	pass

def FIB_PLUS(question_text: str, answer_map: dict) -> str:
	pass

def NUM(question_text: str,  answer, tolerance, tol_message=True):
	pass

def MATCH(question_text: str,  answers_list, matching_list):
	pass

def ORDER(question_text: str,  ordered_answers_list):
	pass
