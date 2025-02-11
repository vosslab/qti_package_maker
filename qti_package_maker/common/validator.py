
# Standard Library
import re
import xml.etree.ElementTree as ET

# Pip3 Library

# QTI Package Maker
# none allowed here!!

#========================================================
def validate_html(html_str: str) -> bool:
	"""
	Validates if the input HTML string is well-formed by removing entities
	and wrapping the content in a root element for XML parsing.
	"""
	html_str = html_str.replace('<', '\n<')
	# Remove HTML entities by finding '&' followed by alphanumerics or '#' and a semicolon
	cleaned_html = re.sub(r'&[#a-zA-Z0-9]+;', '', html_str)
	# Wrap in a root tag for XML parsing as XML requires a single root element
	wrapped_html = f"<root>{cleaned_html}</root>"
	# Parse the cleaned and wrapped HTML with XML parser
	ET.fromstring(wrapped_html)
	return True
assert validate_html('simple string') == True
assert validate_html('<p>simple html paragraph</p>') == True

#========================================================
def validate_string_text(string_text: str, name: str, min_length: int = 3):
	"""
	Validate a string text.
	"""
	if not isinstance(string_text, str):
		raise ValueError(f"The {name} must be a string.")
	if not string_text.strip():
		raise ValueError(f"The {name} cannot be empty.")
	if len(string_text.strip()) < min_length:
		raise ValueError(f"'{name}' must have at least {min_length} length (found {len(string_text.strip())}).")
	validate_html(string_text)
	return True
assert validate_string_text("What is 2 + 2?", 'assert_question') == True
assert validate_string_text("2", 'assert_choice', 1) == True

#========================================================
def validate_list_of_strings(list_of_strings: list, name: str, min_length: int = 2) -> bool:
	"""
	Validate a list of strings to ensure it meets basic requirements.
	"""
	# Ensure the input is a list
	if not isinstance(list_of_strings, list):
		raise ValueError(f"'{name}' must be a list.")
	# Ensure the list is not empty and meets the minimum length requirement
	if not list_of_strings:
		raise ValueError(f"'{name}' cannot be empty.")
	if len(list_of_strings) < min_length:
		raise ValueError(f"'{name}' must have at least {min_length} items (found {len(list_of_strings)}).")
	# Ensure all elements in the list are non-empty strings
	for string_text in list_of_strings:
		validate_string_text(string_text, f'string_text from {name}', 1)
	# Ensure there are no duplicate items
	if len(list_of_strings) > len(set(list_of_strings)):
		raise ValueError(f"'{name}' cannot contain duplicate items.")
	return True
assert validate_list_of_strings(["4", "3"], 'assert') == True

#========================================================
def validate_MC(question_text: str, choices_list: list, answer_text: str):
	"""
	Validate a Multiple Choice (Single Answer) question.

	Args:
		question_text (str): The question text.
		choices_list (list): List of possible choices.
		answer_text (str): The correct answer.
	"""
	validate_string_text(question_text, 'question_text')
	validate_list_of_strings(choices_list, 'choices_list')
	validate_string_text(answer_text, 'answer_text', 1)
	# Validation logic
	if answer_text not in choices_list:
		raise ValueError("Error: The correct answer is not in the list of choices.")
	if choices_list.count(answer_text) > 1:
		raise ValueError("Error: The correct answer appears more than once in list of choices.")
	return True
assert validate_MC("What is 2 + 2?", ["4", "3"], "4") == True

#========================================================
def validate_MA(question_text: str, choices_list: list, answers_list: list):
	"""
	Validate a Multiple Answer question.

	Args:
		question_text (str): The question text.
		choices_list (list): List of possible choices.
		answers_list (list): List of correct answers.
	"""
	validate_string_text(question_text, 'question_text')
	validate_list_of_strings(choices_list, 'choices_list', 3)
	validate_list_of_strings(answers_list, 'answers_list', 2)
	choices_set = set(choices_list)
	answers_set = set(answers_list)
	# Check that there is at least one non-answer (choice that is not in answers_set)
	if choices_set == answers_set:
		raise ValueError("There must be at least one non-answer choice.")
	# Ensure all answers are valid choices
	if not answers_set.issubset(choices_set):
		raise ValueError("One or more correct answers are not in the list of choices.")
	return True
assert validate_MA("Select all fruits", ["apple", "banana", "carrot"], ["apple", "banana"]) == True

#========================================================
def validate_FIB(question_text: str,  answers_list: list):
	"""
	Validate a Fill-in-the-Blank question.
	"""
	validate_string_text(question_text, 'question_text')
	validate_list_of_strings(answers_list, 'answers_list', 2)
	return True
assert validate_FIB("What color are bananas at the store?", ["green", "yellow"]) == True

#========================================================
def validate_FIB_PLUS(question_text: str, answer_map: dict) -> str:
	"""
	Validate a Fill-in-the-Blank-Plus question.
	"""
	validate_string_text(question_text, 'question_text')
	if not answer_map:
		raise ValueError("Answer map cannot be empty.")
	for key_text, value_list in answer_map.items():
		# Ensure each key appears in the question text
		if not f"[{key_text}]" in question_text:
				raise ValueError(f"Key '{key_text}' must appear in the question text.")
		# Ensure the value list is valid
		if not isinstance(value_list, list):
				raise ValueError(f"Values for key '{key_text}' must be a list.")
		if not value_list:
				raise ValueError(f"Value list for key '{key_text}' cannot be empty.")
		if not all(isinstance(value, str) and value.strip() for value in value_list):
				raise ValueError(f"All values for key '{key_text}' must be non-empty strings.")
	return True
test_answer_map = {'colors': ['red', 'blue'], 'cities': ['Chicago', 'New York']}
assert validate_FIB_PLUS("What [colors] is which [cities]?", test_answer_map) == True

#========================================================
def validate_NUM(question_text: str, answer_float: float, tolerance_float: float, tol_message: bool=True):
	"""
	Validate a Numeric question.
	"""
	validate_string_text(question_text, 'question_text')
	if not isinstance(answer_float, (int, float)):
		raise ValueError("Answer must be a number.")
	if not isinstance(tolerance_float, (int, float)) or tolerance_float < 0:
		raise ValueError("Tolerance must be a non-negative number.")
	return True
assert validate_NUM("What year was this written?", 2025, 0.5) == True

#========================================================
def validate_MATCH(question_text: str,  answers_list: list, matching_list: list):
	"""
	Validate a Matching question.
	"""
	validate_string_text(question_text, 'question_text')
	validate_list_of_strings(answers_list, 'answers_list', 2)
	validate_list_of_strings(matching_list, 'matching_list', 2)
	if len(answers_list) != len(matching_list):
		raise ValueError("Answers list and matching list must have the same length.")
	return True
assert validate_MATCH("Match the fruit to their color?", ["orange", "strawberry"], ["orange", "red"]) == True

#========================================================
def validate_ORDER(question_text: str,  ordered_answers_list: list):
	"""
	Validate an Order question.
	"""
	validate_string_text(question_text, 'question_text')
	validate_list_of_strings(ordered_answers_list, 'ordered_answers_list', 3)
	return True
assert validate_ORDER("In what order do the numbers go?", ["1", "2", "3"]) == True
