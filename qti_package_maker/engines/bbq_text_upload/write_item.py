ENGINE_NAME="bbq_text_upload"

# Standard Library
import math
import random

# Pip3 Library (if applicable, add specific imports here)

# QTI Package Maker (if applicable, add specific imports here)
from qti_package_maker.common import string_functions

shuffle = True
letters = 'ABCDEFGHJKMNPQRSTUWXYZ'

"""
Follows the upload format documented here:
https://help.blackboard.com/Learn/Instructor/Original/Tests_Pools_Surveys/Orig_Reuse_Questions/Upload_Questions
"""

#==============================================================
# Create a Multiple Choice (Single Answer; Radio Buttons) question.
def MC(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str) -> str:
	"""Multiple Choice question."""
	# Initialize the question format with MC (Multiple Choice) identifier
	bb_question = 'MC\t'
	# Append the question text with a unique identifier (crc16_text)
	bb_question += f'<p>{crc16_text}</p> {question_text}'
	# Shuffle choices if shuffle is enabled
	already_has_prefix = string_functions.has_prefix(choices_list)
	if shuffle and not already_has_prefix:
		random.shuffle(choices_list)
	# Loop through answer choices and format them with letters
	for i, choice_text in enumerate(choices_list):
		if already_has_prefix:
			bb_question += f'\t{choice_text}'
		else:
			letter_prefix = string_functions.number_to_letter(i+1)
			bb_question += f'\t{letter_prefix}. {choice_text}'
		# Check if the current choice is the correct answer
		if choice_text == answer_text:
			bb_question += '\tCorrect'
		else:
			bb_question += '\tIncorrect'
	# Return the formatted question
	return bb_question + '\n'

#==============================================================
# Create a Multiple Answer (Checkboxes) question.
def MA(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_list: list) -> str:
	"""Multiple Answer question."""
	# Initialize the question format with MC (Multiple Answer) identifier
	bb_question = 'MC\t'
	# Append the question text with a unique identifier (crc16_text)
	bb_question += f'<p>{crc16_text}</p> {question_text}'
	already_has_prefix = string_functions.has_prefix(choices_list)
	if shuffle and not already_has_prefix:
		random.shuffle(choices_list)
	# Loop through answer choices and format them with letters
	for i, choice_text in enumerate(choices_list):
		if already_has_prefix:
			bb_question += f'\t{choice_text}'
		else:
			letter_prefix = string_functions.number_to_letter(i+1)
			bb_question += f'\t{letter_prefix}. {choice_text}'
		# Check if the current choice is in the correct answer list
		if choice_text in answer_list:
			bb_question += '\tCorrect'
		else:
			bb_question += '\tIncorrect'
	# Return the formatted question
	return bb_question + '\n'

#==============================================================
# Create a Matching question where users match items from two lists.
def MATCH(item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list) -> str:
	"""Matching question."""
	# Initialize the question format with MAT (Matching) identifier
	bb_question = 'MAT\t'
	# Append the question text with a unique identifier (crc16_text)
	bb_question += f'<p>{crc16_text}</p> {question_text}'
	already_has_prefix = string_functions.has_prefix(prompts_list) or string_functions.has_prefix(choices_list)
	# Ensure prompts and choices are the same length
	if len(prompts_list) < len(choices_list):
		print("Warning: bbq upload format does not allow extra distractors")
	# Loop through prompts and their matching choices
	for i in range(len(prompts_list)):
		if already_has_prefix:
			bb_question += f'\t{prompts_list[i]}\t{choices_list[i]}'
		else:
			letter_prefix = string_functions.number_to_letter(i+1)
			bb_question += f"- {letter_prefix}. {prompts_list[i]}\t{i+1}. {choices_list[i]}"
	# Return the formatted question
	return bb_question + '\n'

#==============================================================
# Create a Numerical question with an accepted tolerance range.
def NUM(item_number: int, crc16_text: str, question_text: str, answer_float: float,
		tolerance_float: float, tol_message: bool=True) -> str:
	"""Numerical question."""
	# Initialize the question format with NUM (Numerical) identifier
	bb_question = 'NUM\t'
	# Append optional tolerance message to question text
	if tol_message:
		question_text += '<p><i>Note: answers need to be within '
		question_text += f'{math.ceil(tolerance_float/answer_float*100):d}&percnt; '
		question_text += 'of the correct number to be correct.</i></p> '
	# Append question text with unique identifier (crc16_text)
	bb_question += f'<p>{crc16_text}</p> {question_text}'
	# Append numerical answer and tolerance values
	bb_question += f'\t{answer_float:.8f}'
	bb_question += f'\t{tolerance_float:.8f}'
	# Return the formatted question
	return bb_question + '\n'

#==============================================================
# Create a Fill-in-the-Blank (Single Blank) question.
def FIB(item_number: int, crc16_text: str, question_text: str, answers_list: list) -> str:
	"""Fill-in-the-Blank question."""
	# Initialize the question format with FIB (Fill in the Blank) identifier
	bb_question = 'FIB\t'
	# Append the question text with a unique identifier (crc16_text)
	bb_question += f'<p>{crc16_text}</p> {question_text}'
	# Loop through possible answers and append them
	for answer_text in answers_list:
		bb_question += f'\t{answer_text}'
	# Return the formatted question
	return bb_question + '\n'

#==============================================================
# Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping.
def MULTI_FIB(item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Multi-Blank Fill-in-the-Blank question."""
	# Initialize the question format with FIB_PLUS identifier
	bb_question = 'FIB_PLUS\t'
	# Append the question text with a unique identifier (crc16_text)
	bb_question += f'<p>{crc16_text}</p> {question_text}'
	# Sort and iterate through answer mappings
	keys_list = sorted(answer_map.keys())
	for key_text in keys_list:
		bb_question += f'\t{key_text}'
		value_list = answer_map[key_text]
		for value_text in value_list:
			bb_question += f'\t{value_text}'
		# Extra tab to denote next blank to fill-in
		bb_question += '\t'
	# Return the formatted question
	return bb_question + '\n'

#==============================================================
# Create an Ordered List question where users arrange items in a correct sequence.
def ORDER(item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list) -> str:
	"""Ordered List question."""
	# Initialize the question format with ORD (Ordered List) identifier
	bb_question = 'ORD\t'
	# Append the question text with a unique identifier (crc16_text)
	bb_question += f'<p>{crc16_text}</p> {question_text}'
	# Append answers in correct order
	for answer_text in ordered_answers_list:
		bb_question += f'\t{answer_text}'
	# Return the formatted question
	return bb_question + '\n'
