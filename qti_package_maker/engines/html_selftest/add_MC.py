# Import modules from the standard library

# Import modules from external pypi libraries

# Import modules from local libraries
from qti_package_maker.common import string_functions
from qti_package_maker.engines.html_selftest import html_functions

#==============
# This function generates HTML for a multiple-choice question.
def generate_core_html(crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""
	Generate the HTML structure for a multiple-choice question.
	"""
	# Start the HTML content with a div containing a unique ID for the question
	html_content = f"<div id=\"question_html_{crc16_text}\">\n"
	# Add the question text inside another uniquely identified div
	html_content += html_functions.format_question_text(crc16_text, question_text)
	# Begin the form for the multiple-choice options
	html_content += "<form>\n"
	# Add an unordered list to contain the choices, identified by a unique ID
	html_content += f"<ul id=\"choices_{crc16_text}\">\n"
	# Loop through each answer choice
	for idx, choice_text in enumerate(choices_list):
		# Extract the choice text and whether it is the correct answer
		is_correct_bool = (choice_text == answer_text)
		# Add a list item to contain the radio button and label
		html_content += "  <li>\n"
		# Add an input element of type "radio"
		html_content += f"    <input type=\"radio\" id=\"option{idx}\" "
		# Set the name attribute to group radio buttons together under the question's hex value
		html_content += f" name=\"answer_{crc16_text}\" "
		# Store whether the choice is correct as a custom data attribute
		html_content += f" data-correct=\"{str(is_correct_bool).lower()}\">\n"
		# Add a label for the radio button, associated by its ID
		html_content += f"    <label for=\"option{idx}\">{choice_text}</label>\n"
		# Close the list item
		html_content += "  </li>\n"
	# Close the unordered list of choices
	html_content += "</ul>\n"
	html_content += html_functions.add_check_answer_button(crc16_text)
	html_content += html_functions.add_result_div(crc16_text)
	# Close the form element
	html_content += "</form><br/>\n"
	# Close the question div element
	html_content += "</div>"
	# Return the complete HTML content
	return html_content

#==============

# This function generates JavaScript to check the answer for a multiple-choice question.
def generate_javascript(crc16_text) -> str:
	"""
	Generate JavaScript code for validating the answer to a multiple-choice question.

	Args:
		crc16_text (str): Unique identifier for the question.

	Returns:
		str: JavaScript code as a string.
	"""
	# Begin the JavaScript with a script tag
	javascript_html = "<script>\n"
	# Define a function to check the selected answer, using the unique hex value
	javascript_html += f"function checkAnswer_{crc16_text}() {{\n"
	# Get all radio button options for this question
	javascript_html += f" const options = document.getElementsByName('answer_{crc16_text}');\n"
	# Find the correct option by checking the custom data attribute
	javascript_html += " const correctOption = Array.from(options).reduce(function(acc, option) {\n"
	javascript_html += "   return acc || (option.dataset.correct === 'true' ? option : null);\n"
	javascript_html += " }, null);\n"
	# Find the selected option by checking which radio button is checked
	javascript_html += " const selectedOption = Array.from(options).reduce(function(acc, option) {\n"
	javascript_html += "   return acc || (option.checked ? option : null);\n"
	javascript_html += " }, null);\n"
	# Get the result display element by its unique ID
	javascript_html += f" const resultDiv = document.getElementById('result_{crc16_text}');\n"
	# Check if the user selected an option
	javascript_html += " if (selectedOption) {\n"
	# If the selected option is correct, display a "CORRECT" message in green
	javascript_html += "  if (selectedOption === correctOption) {\n"
	javascript_html += "   resultDiv.style.color = 'green';\n"
	javascript_html += "   resultDiv.textContent = 'CORRECT';\n"
	# If the selected option is incorrect, display an "incorrect" message in red
	javascript_html += "  } else {\n"
	javascript_html += "   resultDiv.style.color = 'red';\n"
	javascript_html += "   resultDiv.textContent = 'incorrect';\n"
	javascript_html += "  }\n"
	# If no option was selected, prompt the user to select an answer
	javascript_html += " } else {\n"
	javascript_html += "  resultDiv.style.color = 'black';\n"
	javascript_html += "  resultDiv.textContent = 'Please select an answer.';\n"
	javascript_html += " }\n"
	# Close the function definition
	javascript_html += "}\n"
	# Close the script tag
	javascript_html += "</script>\n"
	# Return the complete JavaScript code
	return javascript_html

#==============

def generate_html(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""
	Main conversion function to generate HTML and JavaScript
	"""
	# Generate the HTML content for the question
	raw_html = generate_core_html(crc16_text, question_text, choices_list, answer_text)
	# Format the generated HTML for better readability, do not use for JavaScript
	formatted_html = string_functions.format_html_lxml(raw_html)
	# Append JavaScript AFTER formatting (to avoid breaking <script> tags)
	full_page_html = formatted_html
	full_page_html += generate_javascript(crc16_text)
	return full_page_html
