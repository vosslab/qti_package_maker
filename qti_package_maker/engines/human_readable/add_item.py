ENGINE_NAME = "human_readable"

from qti_package_maker.common import string_functions


#==============================================================
def MC(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	already_has_prefix = string_functions.has_prefix(choices_list)
	for i, choice_text in enumerate(choices_list):
		if choice_text == answer_text:
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
def MA(item_number: int, crc16_text: str, question_text: str, choices_list: list, answers_list: list):
	"""Create a Multiple Answer (Checkboxes) question."""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	already_has_prefix = string_functions.has_prefix(choices_list)
	for i, choice_text in enumerate(choices_list):
		if choice_text in answers_list:
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
def MATCH(item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	"""Create a Matching question where users match items from two lists."""
	#MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	already_has_prefix = string_functions.has_prefix(prompts_list) or string_functions.has_prefix(choices_list)
	num_items = min(len(prompts_list), len(choices_list))
	max_prompt_length = max(len(prompt_text) for prompt_text in prompts_list)
	for i in range(num_items):
		prompt_text = string_functions.make_question_pretty(prompts_list[i])
		choice_text = string_functions.make_question_pretty(choices_list[i])
		if already_has_prefix:
			assessment_text += f"- {prompt_text.rjust(max_prompt_length)} / {choice_text}\n"
		else:
			letter_prefix = string_functions.number_to_letter(i+1)
			assessment_text += f"- {letter_prefix}. {prompt_text.rjust(max_prompt_length)} / {i+1}. {choice_text}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def NUM(item_number: int, crc16_text: str, question_text: str, answer_float: float,
		  tolerance_float: float, tolerance_message=True):
	"""Create a Numerical question with an accepted tolerance range."""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	if tolerance_message:
		assessment_text += f"\n(Note: Answer must be within &pm;{tolerance_float} of the correct value)"
	assessment_text += '\n'
	assessment_text += f"- Answer: [____] (Correct: {answer_float:.3f})"  # Display correct answer
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
def FIB(item_number: int, crc16_text: str, question_text: str, answers_list: list):
	"""Create a Fill-in-the-Blank (Single Blank) question."""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text = assessment_text.replace("____", "[____]")  # Ensure consistent blank formatting
	assessment_text += '\n'
	for i, answer_text in enumerate(answers_list):
		letter_prefix = string_functions.number_to_lowercase(i+1)
		pretty_answer_text = string_functions.make_question_pretty(answer_text)
		assessment_text += f"- Answer: [{letter_prefix}] {pretty_answer_text}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============================================================
# Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping.
def MULTI_FIB(item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping."""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	for i, fib_variable_name in enumerate(answer_map.keys()):
		assessment_text += f"Blank {i+1}. {fib_variable_name}:\n"
		answers_list = answer_map[fib_variable_name]
		for j, answer_text in enumerate(answers_list):
			letter_prefix = string_functions.number_to_lowercase(j+1)
			pretty_answer_text = string_functions.make_question_pretty(answer_text)
			# Show correct answers per blank
			assessment_text += f"- [{letter_prefix}] {pretty_answer_text}\n"
		assessment_text += '\n'
	assessment_text += '\n'
	return assessment_text

#==============================================================
def ORDER(item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	"""Create an Ordered List question where users arrange items in a correct sequence."""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	for i, answer_text in enumerate(ordered_answers_list):
		# Display correct answer next to blank
		assessment_text += f"- [{i+1}] [____] (Correct: {answer_text})\n"
	assessment_text += '\n\n'
	return assessment_text
