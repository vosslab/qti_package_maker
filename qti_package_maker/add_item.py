
# Standard Library

# Pip3 Library

# QTI Package Maker
import xml_helpers
import item_helpers

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
		print("not enough choices to choose from, you need two choices for multiple choice")
		print("answer=", answer_text)
		print("choices_list=", choices_list)
		raise ValueError

	if answer_text not in choices_list:
		raise ValueError("Error: The correct answer is not in the list of choices.")
	if choices_list.count(answer_text) > 1:
		raise ValueError("Error: The correct answer appears more than once in list of choices.")

	crc16question = item_helpers.get_crc16_from_string(question_text)
	choices_str = '|'.join(choices_list)
	crc16choice = item_helpers.get_crc16_from_string(choices_str)
	crc_merge = f"{crc16question}-{crc16choice}"

	assessment_item_etree = xml_helpers.create_assessment_item_header(crc_merge)
	response_declaration = xml_helpers.create_response_declaration(
		"RESPONSE", [f"answer_{choices_list.index(answer_text) + 1}"]
	)
	outcome_declarations = xml_helpers.create_outcome_declarations()
	item_body = xml_helpers.create_item_body(question_text, choices_list)
	response_processing = xml_helpers.create_response_processing("RESPONSE")

	# Assemble the XML tree
	assessment_item_etree.append(response_declaration)
	for outcome in outcome_declarations:
		assessment_item_etree.append(outcome)
	assessment_item_etree.append(item_body)
	assessment_item_etree.append(response_processing)

	return assessment_item_etree


def MA(question_text: str,  choices_list, answers_list):
    pass

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
