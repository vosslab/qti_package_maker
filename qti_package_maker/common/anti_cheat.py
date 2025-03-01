
# Standard Library
import os
import re
import random
import subprocess

# Pip3 Library

# QTI Package Maker
# none allowed here!!

#anticheating measures
use_nocopy_script = False
use_insert_hidden_terms = False
hidden_term_density = 0.7
use_add_no_click_div = False
noPrint = True
noCopy = True
noScreenshot = False
autoBlur = True

hidden_term_bank = None

#==========================
def get_git_root(path=None):
	"""Return the absolute path of the repository root."""
	if path is None:
		# Use the path of the script
		path = os.path.dirname(os.path.abspath(__file__))
	try:
		base = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=path, universal_newlines=True).strip()
		return base
	except subprocess.CalledProcessError:
		# Not inside a git repository
		return None

#==========================
def load_hidden_term_bank():
	git_root = get_git_root()
	data_file_path = os.path.join(git_root, 'data/all_short_words.txt')
	with open(data_file_path, 'r') as file:
		terms = file.readlines()
	return [term.strip() for term in terms]

#==========================
def insert_hidden_terms(text_content):
	if use_insert_hidden_terms is False:
		return text_content

	global hidden_term_bank
	if hidden_term_bank is None:
		hidden_term_bank = load_hidden_term_bank()

	# Separate table, code and non-table/non-code content
	parts = re.split(r'(<table>.*?</table>|<code>.*?</code>)', text_content, flags=re.DOTALL)

	# Process each part
	new_parts = []
	for part in parts:
		if part.startswith('<table>') or part.startswith('<code>'):
			# Keep table and code content unchanged
			new_parts.append(part)
		else:  # Apply the modified logic to non-table parts
			# Replace spaces adjacent to words with '@'
			#part = re.sub(r'([a-z]) +(?![^<>]*>)', r'\1@', part)
			part = re.sub(r'([a-z]) +([a-z])(?![^<>]*>)', r'\1@\2', part)
			#part = re.sub(r'([A-Za-z]) +(?![^<>]*>)', r'\1@', part)
			#part = re.sub(r' +([A-Za-z])(?![^<>]*>)', r'@\1', part)
			words = part.split('@')
			new_words = []
			for word in words:
				new_words.append(word)
				if random.random() < hidden_term_density:
					hidden_term = random.choice(hidden_term_bank)
					new_words.append(f"<span style='font-size: 1px; color: white;'>{hidden_term}</span>")
				else:
					new_words.append(" ")
			new_parts.append(''.join(new_words))
	return ''.join(new_parts)

#==========================
def add_no_click_div(text):
	if use_add_no_click_div is False:
		return text
	number = random.randint(1000,9999)
	output  = f'<div id="drv_{number}" '
	output += 'oncopy="return false;" onpaste="return false;" oncut="return false;" '
	output += 'oncontextmenu="return false;" onmousedown="return false;" onselectstart="return false;" '
	output += '>'
	output += text
	output += '</div>'
	return output

#==========================
def generate_js_function():
	if use_nocopy_script is False:
		return ''
	return jsdelivr_js_function()
	#return pdfanticopy_js_function()

#==========================
def pdfanticopy_js_function():
	# Using Python f-string to include global variables in the JavaScript code
	js_code = f'<script>var noPrint={str(noPrint).lower()};var noCopy={str(noCopy).lower()};var noScreenshot={str(noScreenshot).lower()};var autoBlur={str(autoBlur).lower()};</script>'
	js_code += '<script type="text/javascript" '
	js_code += 'src="https://pdfanticopy.com/noprint.js"'
	js_code += '></script>'
	return js_code

#==========================
def jsdelivr_js_function():
	# Similar technique is applied here, variables are inserted dynamically
	js_code = f'<script>var noPrint={str(noPrint).lower()};var noCopy={str(noCopy).lower()};var noScreenshot={str(noScreenshot).lower()};var autoBlur={str(autoBlur).lower()};</script>'
	js_code += '<script type="text/javascript" '
	js_code += 'src="https://cdn.jsdelivr.net/gh/vosslab/biology-problems@main/javascript/noprint.js"'
	js_code += '></script>'
	return js_code


