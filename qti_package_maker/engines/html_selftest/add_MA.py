# Import modules from the standard library

# Import modules from external pypi libraries

# Import modules from local libraries
from qti_package_maker.common import string_functions
from qti_package_maker.engines.html_selftest import html_functions
from qti_package_maker.engines.html_selftest import javascript_functions

#==============
# This function generates HTML for a multiple-choice question.
def generate_core_html(crc16_text: str, question_text: str, choices_list: list, answers_list: list):
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
	# Loop through each answer choice
	for idx, choice_text in enumerate(choices_list):
		# Extract the choice text and whether it is the correct answer
		is_correct_bool = (choice_text in answers_list)
		# Add a list item to contain the checkbox button and label
		html_content += "  <li>\n"
		# Add an input element of type "checkbox"
		html_content += f"    <input type=\"checkbox\" id=\"option{idx}\" "
		# Set the name attribute to group checkbox buttons together under the question's hex value
		html_content += f" name=\"answer_{crc16_text}\" "
		# Store whether the choice is correct as a custom data attribute
		html_content += f" data-correct=\"{str(is_correct_bool).lower()}\">\n"
		# Add a label for the checkbox button, associated by its ID
		html_content += f"    <label for=\"option{idx}\">{choice_text}</label>\n"
		# Close the list item
		html_content += "  </li>\n"
	# Close the unordered list of choices
	html_content += "</ul>\n"
	html_content += html_functions.add_check_answer_button(crc16_text)
	html_content += html_functions.add_clear_selection_button(crc16_text)
	html_content += html_functions.add_result_div(crc16_text)
	# Close the form element
	html_content += "</form><br/>\n"
	# Close the question div element
	html_content += "</div>"
	# Return the complete HTML content
	return html_content

def generate_javascript(crc16_text) -> str:
	"""
	Generate JavaScript code for validating multiple answers in a multiple-answer question.

	Args:
		crc16_text (str): Unique identifier for the question.

	Returns:
		str: JavaScript code as a string.
	"""
	# Begin the JavaScript with a script tag
	javascript_html = "<script>\n"

	# Define the function to check selected answers
	javascript_html += f"function checkAnswer_{crc16_text}() {{\n"

	# Get all checkbox options for this question
	javascript_html += f"\tconst options = Array.from(document.getElementsByName('answer_{crc16_text}'));\n"

	# Find all correct answers using data attribute
	javascript_html += "\tconst correctOptions = options.filter(option => option.dataset.correct === 'true');\n"

	# Find selected answers
	javascript_html += "\tconst selectedOptions = options.filter(option => option.checked);\n"

	# Get the result display element
	javascript_html += f"\tconst resultDiv = document.getElementById('result_{crc16_text}');\n"

	# Count correct and incorrect selections
	javascript_html += "\tconst numCorrectSelected = selectedOptions.filter(option => correctOptions.includes(option)).length;\n"
	javascript_html += "\tconst numIncorrectSelected = selectedOptions.length - numCorrectSelected;\n"
	javascript_html += "\tconst totalCorrect = correctOptions.length;\n"
	javascript_html += "\tconst totalSelected = selectedOptions.length;\n"

	# Check for a fully correct answer
	javascript_html += "\tif (numCorrectSelected === totalCorrect && totalSelected === totalCorrect) {\n"
	javascript_html += "\t\tresultDiv.style.color = 'green';\n"
	javascript_html += "\t\tresultDiv.textContent = 'CORRECT';\n"

	# Case: Too many choices (some correct, some incorrect)
	javascript_html += "\t} else if (totalSelected > totalCorrect) {\n"
	javascript_html += "\t\tresultDiv.style.color = 'red';\n"
	javascript_html += "\t\tresultDiv.textContent = `Too many answers selected. You selected ${numCorrectSelected} correct answers, but also included ${numIncorrectSelected} incorrect choices.`;\n"

	# Case: Too few correct answers selected
	javascript_html += "\t} else if (numCorrectSelected < totalCorrect && totalSelected < totalCorrect) {\n"
	javascript_html += "\t\tresultDiv.style.color = 'orange';\n"
	javascript_html += "\t\tresultDiv.textContent = `Too few answers selected. You got ${numCorrectSelected} out of ${totalCorrect} correct.`;\n"

	# Case: Correct number of boxes checked, but contains incorrect answers
	javascript_html += "\t} else if (totalSelected === totalCorrect && numCorrectSelected < totalCorrect) {\n"
	javascript_html += "\t\tresultDiv.style.color = 'goldenrod';\n"
	javascript_html += "\t\tresultDiv.textContent = `You selected the right number of choices, but only ${numCorrectSelected} out of ${totalCorrect} are correct.`;\n"

	# Case: No selection
	javascript_html += "\t} else if (totalSelected === 0) {\n"
	javascript_html += "\t\tresultDiv.style.color = 'black';\n"
	javascript_html += "\t\tresultDiv.textContent = 'Please select an answer.';\n"

	javascript_html += "\t}\n"  # Close the if statement

	# Close function
	javascript_html += "}\n"

	# Close script tag
	javascript_html += "</script>\n"

	return javascript_html

#==============

def generate_html(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""
	Main conversion function to generate HTML and JavaScript
	"""
	# Generate the HTML content for the question
	html_content = generate_core_html(crc16_text, question_text, choices_list, answer_text)
	# Format the generated HTML for better readability, do not use for JavaScript
	html_content = string_functions.format_html_lxml(html_content)
	# Append the generated JavaScript to the HTML content
	html_content += generate_javascript(crc16_text)
	html_content += javascript_functions.add_clear_selection_javascript(crc16_text)
	return html_content

