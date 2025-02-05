
# Standard Library

# Pip3 Library

# QTI Package Maker
import xml_helpers
import item_helpers

#==============
def add_QTI_MC_Question(N: int, question_text: str, choices_list: list, answer_text: str):
	"""
	Create a Multiple Choice (Single Answer) question in QTI-compliant XML format.

	Args:
		N (int): Question ID.
		question_text (str): The question text.
		choices_list (list): List of answer choices.
		answer (str): The correct answer.

	Returns:
		lxml.etree.Element: XML element for the question.
	"""
	if len(choices_list) <= 1:
		print("not enough choices to choose from, you need two choices for multiple choice")
		print("answer=", answer)
		print("choices_list=", choices_list)
		raise ValueError

	if answer_text not in choices_list:
		raise ValueError("Error: The correct answer is not in the list of choices.")
	if choices_list.count(answer_text) > 1:
		raise ValueError("Error: The correct answer appears more than once in list of choices.")

	assessment_item_etree = xml_helpers.create_assessment_item_header(N, "title")
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


def add_QTI_MA_Question(N, question, choices_list, answers_list):
    pass

def add_QTI_FIB_Question(N, question, answers_list):
    pass

def add_QTI_FIB_PLUS_Question(N: int, question: str, answer_map: dict) -> str:
    pass

def add_QTI_NUM_Question(N, question, answer, tolerance, tol_message=True):
    pass

def add_QTI_MAT_Question(N, question, answers_list, matching_list):
    pass

def add_QTI_ORD_Question(N, question_text, ordered_answers_list):
    pass
