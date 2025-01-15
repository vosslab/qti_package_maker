
# Standard Library
import xml.etree.ElementTree as ET

from qti_package_maker import xml_helpers

#=====================
def question_header(question: str, N: int, crc16: str = None) -> str:
	"""
	Generate a standardized header for a question.

	Args:
		question (str): The question text.
		N (int): The question ID or number.
		crc16 (str): Optional CRC16 checksum for uniqueness (default: None).

	Returns:
		str: Formatted question header.
	"""
	# Generate a CRC16 if not provided
	if crc16 is None:
		crc16 = get_crc16_from_string(question)

	# Log the question header
	print(f"{N:03d}. {crc16} -- {make_question_pretty(question)}")

	# Generate the header
	header = f"<p>{crc16}</p>\n"
	header += add_hidden_terms(question)  # Add any hidden terms for obfuscation, if needed

	return header

#==============

def choice_header(choice_text: str, index: int) -> str:
	"""
	Format a choice in a standardized way.

	Args:
		choice_text (str): The text of the choice.
		index (int): The index of the choice (e.g., 0 for 'A', 1 for 'B').

	Returns:
		str: Formatted choice header.
	"""
	# Generate a label for the choice (e.g., A, B, C, ...)
	letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
	label = letters[index]

	# Log the choice
	print(f"- [{label}] {make_question_pretty(choice_text)}")

	# Add hidden terms for obfuscation, if needed
	noisy_choice_text = insert_hidden_terms(choice_text)

	# Wrap in a div or any other required format
	return add_no_click_div(f"{label}. {noisy_choice_text}")


#==============
def add_QTI_MC_Question(N: int, question: str, choices_list: list, answer: str) -> ET.Element:
	"""
	Create a Multiple Choice (Single Answer) question in QTI-compliant XML format.

	Args:
		N (int): Question ID.
		question (str): The question text.
		choices_list (list): List of answer choices.
		answer (str): The correct answer.

	Returns:
		ET.Element: XML element for the question.
	"""
	if answer not in choices_list:
		print("Error: The correct answer is not in the list of choices.")
		sys.exit(1)

	# Create root
	assessment_item = xml_helpers.create_assessment_item(N, "title")

	# Add components
	xml_helpers.add_response_declaration(assessment_item, "RESPONSE", [f"answer_{choices_list.index(answer) + 1}"])
	xml_helpers.add_outcome_declarations(assessment_item)
	xml_helpers.add_item_body(assessment_item, question, choices_list)
	xml_helpers.add_response_processing(assessment_item, "RESPONSE")

	return assessment_item


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
