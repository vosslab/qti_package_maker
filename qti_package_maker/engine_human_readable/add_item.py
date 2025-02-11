ENGINE_NAME = "human_readable"

from qti_package_maker import string_functions

letters = 'ABCDEFGHJKMNPQRSTUWXYZ'

#==============
def MC(question_text: str, choices_list: list, answer_text: str):
	"""
	Create a Multiple Choice (Single Answer) question in QTI-compliant XML format.

	Args:
	question_text (str): The question text.
	choices_list (list): List of possible choices.
	answer_text (str): The correct answer.
	"""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	for i, choice_text in enumerate(choices_list):
		if choice_text == answer_text:
			prefix = 'x'
		else:
			prefix = ' '
		pretty_choice = string_functions.make_question_pretty(choice_text)
		assessment_text += f"- [{prefix}] {letters[i]}. {pretty_choice}\n"
	assessment_text += '\n\n'
	return assessment_text

#==============
def MA(question_text: str, choices_list: list, answers_list: list):
	"""
	Create a Multiple Choice (Single Answer) question in QTI-compliant XML format.

	Args:
	question_text (str): The question text.
	choices_list (list): List of possible choices.
	answers_list (list): List of correct answers.
	"""
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	for i, choice_text in enumerate(choices_list):
		if choice_text in answers_list:
			prefix = 'x'
		else:
			prefix = ' '
		pretty_choice = string_functions.make_question_pretty(choice_text)
		assessment_text += f"- [{prefix}] {letters[i]}. {pretty_choice}\n"
	assessment_text += '\n\n'
	return assessment_text

#=====================
def MATCH(question_text: str, answers_list: list, matching_list: list):
	#MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text
	assessment_text = ''
	assessment_text += string_functions.make_question_pretty(question_text)
	assessment_text += '\n'
	num_items = min(len(answers_list), len(matching_list))
	for i in range(num_items):
		answer_text = string_functions.make_question_pretty(answers_list[i])
		match_text = string_functions.make_question_pretty(matching_list[i])
		assessment_text += f"- {letters[i]}. {answer_text} == {match_text}\n"
	assessment_text += '\n\n'
	return assessment_text
