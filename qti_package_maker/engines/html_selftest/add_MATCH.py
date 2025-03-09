# Import modules from the standard library

# Import modules from external pypi libraries

# Import modules from local libraries
from qti_package_maker.common import string_functions
from qti_package_maker.engines.html_selftest import html_functions
from qti_package_maker.engines.html_selftest import javascript_functions
#============================================
def generate_drag_and_drop_js():
	"""
	Generate JavaScript for drag-and-drop functionality in matching questions.

	Returns:
		str: JavaScript content as a string.
	"""
	js_content = ""
	# Open script tag
	js_content += "<script>\n"
	# Define the dragged item
	js_content += "\tlet draggedItem = null;\n\n"

	# Enable drag functionality for each choice
	js_content += '\tdocument.querySelectorAll(".draggable").forEach(item => {\n'
	js_content += '\t\titem.addEventListener("dragstart", function() {\n'
	js_content += "\t\t\tdraggedItem = this;\n"
	js_content += '\t\t\tsetTimeout(() => this.style.opacity = "0.5", 0);\n'  # Reduce opacity while dragging
	js_content += "\t\t});\n\n"

	js_content += '\t\titem.addEventListener("dragend", function() {\n'
	js_content += '\t\t\tthis.style.opacity = "1";\n'  # Restore opacity
	js_content += "\t\t});\n"
	js_content += "\t});\n\n"

	# Enable drop functionality for each drop zone
	js_content += '\tdocument.querySelectorAll(".dropzone").forEach(zone => {\n'

	#  Store the original background color when an item is dropped
	js_content += '\t\tzone.addEventListener("drop", function() {\n'
	js_content += "\t\t\tthis.dataset.originalBgColor = draggedItem.style.backgroundColor;\n"  # Store choice color
	js_content += "\t\t\tthis.style.backgroundColor = this.dataset.originalBgColor;\n"  # Maintain color
	js_content += '\t\t\tthis.style.border = "2px solid gray";\n'  # Change border to solid
	js_content += "\t\t\tthis.style.color = draggedItem.querySelector(\"span\").style.color;\n"  # Match letter color
	js_content += '\t\t\tthis.style.fontWeight = "bold";\n\n'

	# Handle text truncation for drop zones
	js_content += "\t\t\tlet choiceText = draggedItem.innerText.trim();\n"
	js_content += '\t\t\tthis.innerHTML = choiceText.length > 30 ? choiceText.substring(0, 27) + "..." : choiceText;\n'
	js_content += "\t\t\tthis.dataset.value = draggedItem.dataset.value;\n"
	js_content += '\t\t\tthis.title = draggedItem.getAttribute("title");\n'  # Add tooltip with full text
	js_content += "\t\t});\n\n"

	#  Restore the stored background color on drag leave
	js_content += '\t\tzone.addEventListener("dragleave", function() {\n'
	js_content += '\t\t\tif (!this.dataset.value) {\n'
	js_content += '\t\t\t\tthis.style.backgroundColor = "#f8f8f8";\n'  # Default if empty
	js_content += '\t\t\t} else {\n'
	js_content += '\t\t\t\tthis.style.backgroundColor = this.dataset.originalBgColor;\n'  # Restore previous color
	js_content += '\t\t\t}\n'
	js_content += "\t\t});\n\n"

	#  Prevents accidental clearing when dragging over a filled drop zone
	js_content += '\t\tzone.addEventListener("dragover", function(e) {\n'
	js_content += "\t\t\te.preventDefault();\n"  # Allow drop action
	js_content += '\t\t\tthis.style.backgroundColor = "#e6e6e6";\n'  # Temporary highlight
	js_content += "\t\t});\n"

	js_content += "\t});\n"
	# Close script tag
	js_content += "</script>\n"
	return js_content

def generate_check_answers_js(crc16_text: str):
	"""
	Generate JavaScript function for checking answers and updating feedback.
	"""
	js_content = ""

	# Open script tag
	js_content += "<script>\n"

	# Function definition with unique identifier
	js_content += f"\tfunction checkAnswer_{crc16_text}() {{\n"

	# Initialize score tracking
	js_content += "\t\tlet score = 0;\n"
	js_content += "\t\tlet possible = 0;\n"
	js_content += "\t\tlet feedbackText = \"\";\n\n"

	# Loop through each dropzone to check answers
	js_content += "\t\tdocument.querySelectorAll(\".dropzone\").forEach((zone, index) => {\n"
	js_content += "\t\t\tlet selectedValue = zone.dataset.value;\n"
	js_content += "\t\t\tlet correctValue = zone.dataset.correct;\n"
	js_content += "\t\t\tlet feedbackCell = document.querySelectorAll(\".feedback\")[index];\n\n"

	# Check if the answer is correct
	js_content += "\t\t\tif (selectedValue === correctValue) {\n"
	js_content += "\t\t\t\tscore++;\n"
	js_content += "\t\t\t\tpossible++;\n"
	js_content += "\t\t\t\tfeedbackCell.innerHTML = \"<strong>"
	js_content += "<span style='color:#008000; font-size:large;'>&#9989;</span></strong>\";\n"
	js_content += "\t\t\t\tfeedbackCell.style.backgroundColor = \"#ccffcc\";\n"  # Green background for correct
	js_content += "\t\t\t} else {\n"
	js_content += "\t\t\t\tpossible++;\n"
	js_content += "\t\t\t\tfeedbackCell.innerHTML = \"&#10060;\";\n"  # Red X emoji
	js_content += "\t\t\t\tfeedbackCell.style.backgroundColor = \"#ffcccc\";\n"  # Red background for incorrect
	js_content += "\t\t\t}\n"
	js_content += "\t\t});\n\n"

	# Update feedback text
	js_content += "\t\tfeedbackText = `Total Score: ${score} out of ${possible}`;\n";
	js_content += "\t\tconst resultDiv = document.getElementById('result_"+crc16_text+"');\n";

	# If 100% correct, make feedback green
	js_content += "\t\tif (score === possible) {\n";
	js_content += "\t\t\tresultDiv.style.color = 'green';\n";
	js_content += "\t\t}\n";

	# If score is less than 50%, make feedback red
	js_content += "\t\telse if (score <= Math.floor(possible / 2)) {\n";
	js_content += "\t\t\tresultDiv.style.color = 'red';\n";
	js_content += "\t\t}\n";

	# Otherwise, use the default text color (inherit from theme)
	js_content += "\t\telse {\n";
	js_content += "\t\t\tresultDiv.style.color = 'inherit';\n";
	js_content += "\t\t}\n";

	# Update the result div
	js_content += "\t\tresultDiv.innerHTML = feedbackText;\n";

	# Close function
	js_content += "\t}\n"

	# Close script tag
	js_content += "</script>\n"

	return js_content

#============================================
def generate_prompts_table(crc16_text: str, prompts_list: list):
	"""
	Generate an HTML prompts table for a given list of prompts.
	"""
	table_content = ""
	# Start table
	table_content += "<!-- Matching Table -->\n"
	table_content += "<table style=\"border: 1px solid #999; border-collapse: collapse;\">\n"
	table_content += "\t<thead>\n"
	table_content += "\t\t<tr>\n"
	table_content += "\t\t\t<th style=\"width: 20px;\"></th>\n"  # Feedback Column
	table_content += "\t\t\t<th style=\"padding: 10px; width: 180px; text-align: center;\">Your Choice</th>\n"
	table_content += "\t\t\t<th style=\"padding: 10px;\">Prompt</th>\n"
	table_content += "\t\t</tr>\n"
	table_content += "\t</thead>\n"
	table_content += "\t<tbody>\n"
	# Generate rows for each prompt
	for index, prompt_text in enumerate(prompts_list, start=1):
		# Assign code for data-correct
		choice_data_value = crc16_text + "_" + string_functions.number_to_letter(index)
		table_content += "\t\t<tr>\n"
		table_content += "\t\t\t<td class=\"feedback\" style=\"border: 1px solid #999; text-align: center;\"></td>\n"
		table_content += f"\t\t\t<td class=\"dropzone\" data-correct=\"{choice_data_value}\" title=\"Drop Your Choice Here\" "
		table_content += "style=\"border: 2px dashed #bbb; padding: 8px; text-align: center; background-color: #f8f8f8; "
		table_content += "font-size: 12px; min-width: 120px; max-width: 200px; overflow: hidden; white-space: nowrap; "
		table_content += "text-overflow: ellipsis;\">"
		table_content += "<span style=\"font-style: italic;\">Drop Your Choice Here</span></td>\n"
		table_content += "\t\t\t<td style=\"border: 1px solid #999; padding: 10px;\">"
		table_content += f"{index}. {prompt_text}</td>\n"
		table_content += "\t\t</tr>\n"
	# Close table
	table_content += "\t</tbody>\n"
	table_content += "</table>\n"
	return table_content

#============================================
def generate_choices_list(crc16_text: str, choices_list: list):
	"""
	Generate an HTML choices list for draggable matching questions.
	"""
	html_content = ""
	# Add instructions
	html_content += '<p style="font-style: italic; font-size: 14px; margin-top: 10px;">Drag one of the choices below:</p>\n'
	html_content += '<ul id="choiceList" style="list-style: none; padding: 0;">\n'
	# Define colors for choices
	colors = [
		("#b37100", "#fff9e5"),  # Brown/Light Orange
		("#004080", "#e6e6ff"),  # Blue/Light Blue
		("#008066", "#e6fff3"),  # Green/Light Green
		("#803300", "#f5e6cc"),  # Dark Brown/Beige
		("#660033", "#ffccff")   # Dark Pink/Light Pink
	]
	# Generate list items
	for index, choice_text in enumerate(choices_list):
		clean_title = string_functions.make_question_pretty(choice_text)
		letter_label = string_functions.number_to_letter(index + 1)  # Ensure 1-based index
		choice_data_value = crc16_text + "_" + letter_label
		text_color, bg_color = colors[index % len(colors)]  # Cycle through colors
		html_content += f'\t<li class="draggable" draggable="true" data-value="{choice_data_value}" title="{clean_title}" '
		html_content += 'style="border: 1px solid #999; padding: 8px; margin: 5px; cursor: grab; '
		html_content += f'background-color: {bg_color}; display: inline-block;">\n'
		html_content += f'\t\t<span style="color: {text_color}; font-weight: bold;">{letter_label}</span> - {choice_text}\n'
		html_content += '\t</li>\n'
	# Close list
	html_content += "</ul>\n"
	return html_content

#============================================
# This function generates HTML for a multiple-choice question.
def generate_core_html(crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	"""
	Generate the HTML structure for a multiple-choice question.
	"""
	# Start the HTML content with a div containing a unique ID for the question
	html_content = f"<div id=\"question_html_{crc16_text}\">\n"
	# Add the question text inside another uniquely identified div
	html_content += html_functions.format_question_text(crc16_text, question_text)
	html_content += generate_prompts_table(crc16_text, prompts_list)
	html_content += generate_choices_list(crc16_text, choices_list)
	html_content += html_functions.add_check_answer_button(crc16_text)
	html_content += html_functions.add_reset_game_button(crc16_text)
	html_content += html_functions.add_result_div(crc16_text)
	# Close the question div element
	html_content += "</div>"
	# Return the complete HTML content
	return html_content

#============================================
def generate_html(item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	"""
	Main conversion function to generate HTML and JavaScript
	"""
	# Generate the HTML content for the question
	raw_html = generate_core_html(crc16_text, question_text, prompts_list, choices_list)
	# Format the generated HTML for better readability, do not use for JavaScript
	formatted_html = string_functions.format_html_lxml(raw_html)
	# Append JavaScript AFTER formatting (to avoid breaking <script> tags)
	full_page_html = formatted_html
	full_page_html += generate_drag_and_drop_js()
	full_page_html += generate_check_answers_js(crc16_text)
	full_page_html += javascript_functions.add_reset_game_javascript(crc16_text)
	return full_page_html
