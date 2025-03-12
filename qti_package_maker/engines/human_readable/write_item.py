ENGINE_NAME = "human_readable"

from qti_package_maker.common import string_functions

#==============================================================
def is_valid_content(content_text):
	if '<mathml' in content_text.lower():
		return False
	if 'rdkit' in content_text.lower():
		return False
	if '<table' in content_text.lower():
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
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	if not is_valid_content(item_cls.question_text):
		return None
	if not is_valid_list(item_cls.choices_list):
		return None
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(item_cls.question_text)
	assessment_text += '\n'
	already_has_prefix = string_functions.has_prefix(item_cls.choices_list)
	for i, choice_text in enumerate(item_cls.choices_list):
		if choice_text == item_cls.answer_text:
			prefix = '*'
		else:
			prefix = ' '
		pretty_choice = string_functions.make_question_pretty(choice_text)
		if already_has_prefix:
			assessment_text += f"- [{prefix}] {pretty_choice}\n"
		else:
			letter_prefix = string_functions.number_to_letter(i+1)
			assessment_text += f"- [{prefix}] {letter_prefix}. {pretty_choice}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def MA(item_cls):
	#item_number: int, crc16_text: str, question_text: str, choices_list: list, answers_list: list):
	"""Create a Multiple Answer (Checkboxes) question."""
	if not is_valid_content(item_cls.question_text):
		return None
	if not is_valid_list(item_cls.choices_list):
		return None
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(item_cls.question_text)
	assessment_text += '\n'
	already_has_prefix = string_functions.has_prefix(item_cls.choices_list)
	for i, choice_text in enumerate(item_cls.choices_list):
		if choice_text in item_cls.answers_list:
			prefix = '*'
		else:
			prefix = ' '
		pretty_choice = string_functions.make_question_pretty(choice_text)
		if already_has_prefix:
			assessment_text += f"- [{prefix}] {pretty_choice}\n"
		else:
			letter_prefix = string_functions.number_to_letter(i+1)
			assessment_text += f"- [{prefix}] {letter_prefix}. {pretty_choice}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def MATCH(item_cls):
	#item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	"""Create a Matching question where users match items from two lists."""
	#MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text
	if not is_valid_content(item_cls.question_text):
		return None
	if not is_valid_list(item_cls.prompts_list):
		return None
	if not is_valid_list(item_cls.choices_list):
		return None
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(item_cls.question_text)
	assessment_text += '\n'
	already_has_prefix = string_functions.has_prefix(item_cls.prompts_list) or string_functions.has_prefix(item_cls.choices_list)
	num_items = min(len(item_cls.prompts_list), len(item_cls.choices_list))
	max_prompt_length = max(len(prompt_text) for prompt_text in item_cls.prompts_list)
	for i in range(num_items):
		prompt_text = string_functions.make_question_pretty(item_cls.prompts_list[i])
		choice_text = string_functions.make_question_pretty(item_cls.choices_list[i])
		if already_has_prefix:
			assessment_text += f"- {prompt_text.rjust(max_prompt_length)} / {choice_text}\n"
		else:
			letter_prefix = string_functions.number_to_letter(i+1)
			assessment_text += f"- {letter_prefix}. {prompt_text.rjust(max_prompt_length)} / {i+1}. {choice_text}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def NUM(item_cls):
	#item_number: int, crc16_text: str,
	#question_text: str, answer_float: float, tolerance_float: float, tolerance_message=True):
	"""Create a Numerical question with an accepted tolerance range."""
	if not is_valid_content(item_cls.question_text):
		return None
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(item_cls.question_text)
	if item_cls.tolerance_message:
		assessment_text += f"\n(Note: Answer must be within &pm;{item_cls.tolerance_float} of the correct value)"
	assessment_text += '\n'
	assessment_text += f"- Answer: [____] (Correct: {item_cls.answer_float:.3f})"  # Display correct answer
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answers_list: list):
	"""Create a Fill-in-the-Blank (Single Blank) question."""
	if not is_valid_content(item_cls.question_text):
		return None
	if not is_valid_list(item_cls.answers_list):
		return None
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(item_cls.question_text)
	assessment_text = assessment_text.replace("____", "[____]")  # Ensure consistent blank formatting
	assessment_text += '\n'
	for i, answer_text in enumerate(item_cls.answers_list):
		letter_prefix = string_functions.number_to_lowercase(i+1)
		pretty_answer_text = string_functions.make_question_pretty(answer_text)
		assessment_text += f"- Answer: [{letter_prefix}] {pretty_answer_text}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
# Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping.
def MULTI_FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping."""
	if not is_valid_content(item_cls.question_text):
		return None
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(item_cls.question_text)
	assessment_text += '\n'
	for i, fib_variable_name in enumerate(item_cls.answer_map.keys()):
		assessment_text += f"Blank {i+1}. {fib_variable_name}:\n"
		answers_list = item_cls.answer_map[fib_variable_name]
		for j, answer_text in enumerate(answers_list):
			letter_prefix = string_functions.number_to_lowercase(j+1)
			pretty_answer_text = string_functions.make_question_pretty(answer_text)
			# Show correct answers per blank
			assessment_text += f"- [{letter_prefix}] {pretty_answer_text}\n"
		assessment_text += '\n'
	assessment_text += '\n'
	return assessment_text

#==============================================================
def ORDER(item_cls):
	#item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	"""Create an Ordered List question where users arrange items in a correct sequence."""
	if not is_valid_content(item_cls.question_text):
		return None
	if not is_valid_list(item_cls.ordered_answers_list):
		return None
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(item_cls.question_text)
	assessment_text += '\n'
	for i, answer_text in enumerate(item_cls.ordered_answers_list):
		# Display correct answer next to blank
		assessment_text += f"- [{i+1}] [____] (Correct: {answer_text})\n"
	assessment_text += '\n\n'
	return assessment_text
