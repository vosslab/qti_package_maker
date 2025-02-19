ENGINE_NAME = "human_readable"

from qti_package_maker.common import string_functions

letters = 'ABCDEFGHJKMNPQRSTUWXYZ'
#letters = 'abcdefghijklmnopqrstuvwxyz'


#==============================================================
def MC(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	for i, choice_text in enumerate(choices_list):
		if choice_text == answer_text:
			prefix = '*'
		else:
			prefix = ' '
		pretty_choice = string_functions.make_question_pretty(choice_text)
		assessment_text += f"- [{prefix}] {letters[i]}. {pretty_choice}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def MA(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_list: list):
	"""Create a Multiple Answer (Checkboxes) question."""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	for i, choice_text in enumerate(choices_list):
		if choice_text in answers_list:
			prefix = '*'
		else:
			prefix = ' '
		pretty_choice = string_functions.make_question_pretty(choice_text)
		assessment_text += f"- [{prefix}] {letters[i]}. {pretty_choice}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def MATCH(item_number: int, crc16_text: str, question_text: str, answers_list: list, matching_list: list):
	"""Create a Matching question where users match items from two lists."""
	#MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	num_items = min(len(answers_list), len(matching_list))
	for i in range(num_items):
		answer_text = string_functions.make_question_pretty(answers_list[i])
		match_text = string_functions.make_question_pretty(matching_list[i])
		assessment_text += f"- {letters[i]}. {answer_text} / {match_text}\n"
	assessment_text += '\n\n'
	return assessment_text

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
