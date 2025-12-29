ENGINE_NAME = "moodle_aiken"

from qti_package_maker.common import string_functions

#==============================================================
def is_valid_content(content_text):
	#override for now
	return True

	if '<mathml' in content_text.lower():
		#print("problem contains mathml")
		return False
	if 'rdkit' in content_text.lower():
		#print("problem contains rdkit")
		return False
	if '<table' in content_text.lower():
		#print("problem contains a table")
		return False
	return True

#====================
def is_valid_list(list_of_strings):
	for content_text in list_of_strings:
		if not is_valid_content(content_text):
			return False
	return True

#==============================================================
def MC(item_cls):
	#item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""Render an MC item in Moodle Aiken format."""
	local_question_text = string_functions.make_question_pretty(item_cls.question_text)
	if not is_valid_content(local_question_text):
		return None
	if not is_valid_list(item_cls.choices_list):
		return None
	assessment_text = ''
	assessment_text += item_cls.question_text
	assessment_text += '\n'
	already_has_prefix = string_functions.has_prefix(item_cls.choices_list)
	for i, choice_text in enumerate(item_cls.choices_list):
		local_choice_text = choice_text
		if already_has_prefix:
			local_choice_text = string_functions.strip_prefix_from_string(local_choice_text)
		letter_prefix = string_functions.number_to_letter(i+1)
		assessment_text += f"{letter_prefix}. {local_choice_text}\n"
	answer_letter = string_functions.number_to_letter(item_cls.answer_index+1)
	assessment_text += f"ANSWER: {answer_letter}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def MA(item_cls):
	#item_number: int, crc16_text: str, question_text: str, choices_list: list, answers_list: list):
	"""Moodle Aiken writer does not implement MA items."""
	return None

#==============================================================
def MATCH(item_cls):
	#item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	"""Moodle Aiken writer does not implement MATCH items."""
	#MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text
	return None

#==============================================================
def NUM(item_cls):
	#item_number: int, crc16_text: str,
	#question_text: str, answer_float: float, tolerance_float: float, tolerance_message=True):
	"""Moodle Aiken writer does not implement NUM items."""
	return None

#==============================================================
def FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answers_list: list):
	"""Moodle Aiken writer does not implement FIB items."""
	return None

#==============================================================
# Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping.
def MULTI_FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Moodle Aiken writer does not implement MULTI_FIB items."""
	return None

#==============================================================
def ORDER(item_cls):
	#item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	"""Moodle Aiken writer does not implement ORDER items."""
	return None
