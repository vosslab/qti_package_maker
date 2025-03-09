
# Import modules from the standard library
import re

# Import modules from external Pypi libraries

# Import modules from local libraries
#from qti_package_maker.common import string_functions

#============================================
def format_question_text(crc16_text: str, question_text: str):
	# Replace adjacent paragraph tags with a line break for cleaner formatting
	question_text = re.sub(r'</p>\s*<p>', '<br/>', question_text, flags=re.MULTILINE)
	# Add the question text inside another uniquely identified div
	html_content = f"<div id=\"statement_text_{crc16_text}\">{question_text}</div>\n"
	return html_content

#============================================
def add_result_div(crc16_text: str):
	# Add a div to display the result message, styled with inline CSS
	style = (
		'style="display: block; '
		'margin: 0; '
		'padding: 0; '
		'font-size: large; '
		'font-weight: bold; '
		'font-family: monospace;"'
		)
	html_content = f"<div id=\"result_{crc16_text}\" {style}>&nbsp;</div>\n"
	return html_content

#============================================
def make_button(button_text: str, js_function: str, bgcolor: str=None):
	# Add a custom button
	button_content = ""
	# Set the button type to "button" to prevent form submission
	button_content += "<button type=\"button\" "
	# Set the class of the button to match the material design theme of the website
	button_content += 'class="md-button md-button--secondary custom-button" '
	if bgcolor:
		button_content += f"style=\"background-color: {bgcolor};\" "
	# Add an onclick event to call the answer-checking function for this question
	button_content += f"onclick=\"{js_function}()\">"
	# Set the button's visible text
	button_content += button_text
	# Close the button element
	button_content += "</button>\n"
	return button_content

#============================================
def add_check_answer_button(crc16_text: str, button_text: str="Check Answer"):
	# Add a button for submitting the answer
	js_function = f"checkAnswer_{crc16_text}"
	return make_button(button_text, js_function)

#============================================
def add_clear_selection_button(crc16_text: str, button_text: str="Clear Selection"):
	# "Clear Selection" button
	js_function = f"clearSelection_{crc16_text}"
	return make_button(button_text, js_function, "#e6eeff")

#============================================
def add_reset_game_button(crc16_text: str, button_text: str="Reset Game"):
	# "Reset Game" button
	js_function = f"resetGame_{crc16_text}"
	return make_button(button_text, js_function, "#fbe9eb")


