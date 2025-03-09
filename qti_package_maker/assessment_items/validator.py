
# Standard Library
import re
import lxml.etree

# Pip3 Library

# QTI Package Maker
# none allowed here!!

def is_valid_crc16_code_string(code_string: str) -> bool:
	pattern = r"\b([0-9a-f]{4})(?:_[0-9a-f]{4})*\b"
	# Store the result in a variable
	is_valid = bool(re.fullmatch(pattern, code_string))
	# Return the variable
	return is_valid

#========================================================
def clean_html_for_xml(html_str: str) -> str:
	"""
	Cleans and prepares an HTML string for XML validation by:
	"""
	# Step 1: Remove JavaScript content but keep the <script> tags intact
	# This ensures that <script></script> remains valid but doesn't break XML parsing.
	html_str = re.sub(r'<script[^>]*>', '<script>', html_str)
	html_str = re.sub(r'<script\b[^>]*>.*?</script>', '<script></script>', html_str)

	# Step 2: Add newlines before < tags for better readability when debugging
	# This makes the HTML more human-readable but doesn't affect XML parsing.
	#html_str = html_str.replace('<', '\n<')

	# Step 3: Ensure that attributes like colspan=2 are properly quoted (colspan="2")
	# This is required for valid XML/XHTML since lxml enforces quoted attributes.
	html_str = re.sub(r'(\b(?:colspan|rowspan|width|height|size)\s*=\s*)(\d+)(?!["\w])', r'\1"\2"', html_str)

	# Step 4: Remove special HTML entities like &amp; or &copy; to prevent parsing errors.
	# This ensures that lxml doesn't break on unescaped entities.
	html_str = re.sub(r'&[#a-zA-Z0-9]+;', '', html_str)

	# Step 5: Clean up URLs by removing query parameters after '?' to simplify validation
	# Example: href="https://example.com/page?query=123" → href="https://example.com/page"
	html_str = re.sub(r'(href=[\'"])(https?://[^\'"]+?)\?.*?([\'"])', r'\1\2\3', html_str)

	# Step 6: Temporarily remove SMILES values (which contain special characters)
	# This prevents XML validation errors while keeping the structure intact.
	html_str = re.sub(r'smiles="[^"]*?"', r'smiles=""', html_str)

	clean_html = html_str.strip()
	return clean_html
"""
assert clean_html_for_xml('simple&copy;') == 'simple'
assert clean_html_for_xml('&amp;&gt;&lt;') == ''
assert clean_html_for_xml('<p></p>') == '<p>\n</p>'
assert clean_html_for_xml('<p>Valid content</p>') == '<p>Valid content\n</p>'
assert clean_html_for_xml('<script></script>') == '<script>\n</script>'
assert clean_html_for_xml('<script>let i=0;</script>') == '<script>\n</script>'
assert clean_html_for_xml('<script>let i=0;</script>html content<script>let i=0;</script>') == '<script>\n</script>html content\n<script>\n</script>'
assert clean_html_for_xml('<th colspan=2>Header</th>') == '<th colspan="2">Header\n</th>'
assert clean_html_for_xml('<td rowspan=3>Data</td>') == '<td rowspan="3">Data\n</td>'
assert clean_html_for_xml('<a href="https://x.com/page?q=123">Link</a>') == '<a href="https://x.com/page">Link\n</a>'
assert clean_html_for_xml('smiles="C[C@H](N)C(=O)O"') == 'smiles=""'
assert clean_html_for_xml('<div style="width=100">Content</div>') == '<div style="width=100">Content\n</div>'
assert clean_html_for_xml('<div style="width: 100px; height: 10px;">Content</div>') == '<div style="width: 100px; height: 10px;">Content\n</div>'
"""

#========================================================
def validate_html(html_str: str) -> bool:
	"""
	Validates if the input HTML string is well-formed by removing entities
	and wrapping the content in a root element for XML parsing using lxml.
	"""
	clean_html = clean_html_for_xml(html_str)
	wrapped_html = f"<root><cleaned>{clean_html}</cleaned></root>"
	# Parse the cleaned and wrapped HTML using lxml.etree
	try:
		lxml.etree.fromstring(wrapped_html)
	except lxml.etree.XMLSyntaxError as e:
		print("\n\n==== XML PARSING ERROR ====\n")
		print("Error Message:", e)  # Prints the exact error message
		print("\n==== Wrapped HTML Dump ====\n")
		print(f"<original>{html_str}</original>")
		print(wrapped_html)  # Prints the problematic HTML
		print("\n=================================\n")
		raise  # Re-raises the error so it doesn't silently fail
	return True
# Assertions to test the function
assert validate_html('simple string') == True
assert validate_html('<p>simple html paragraph</p>') == True
assert validate_html('<p>&copy; simple html paragraph &amp; escaped characters</p>') == True

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
	validate_list_of_strings(answers_list, 'answers_list', 1)
	return True
assert validate_FIB("What color are bananas at the store?", ["green", "yellow"]) == True

#========================================================
def validate_MULTI_FIB(question_text: str, answer_map: dict) -> str:
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
assert validate_MULTI_FIB("What [colors] is which [cities]?", test_answer_map) == True

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
def validate_MATCH(question_text: str, prompts_list: list, choices_list: list):
	"""
	Validate a Matching question.
	"""
	validate_string_text(question_text, 'question_text')
	validate_list_of_strings(prompts_list, 'prompts_list', 2)
	validate_list_of_strings(choices_list, 'choices_list', 2)
	if len(prompts_list) > len(choices_list):
		raise ValueError("choices_list must be greater or equal to the prompts_list.")
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
