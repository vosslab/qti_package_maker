
# Standard Library
import re
import os
import copy
import html
import random
import subprocess

# Pip3 Library
import lxml.etree
import lxml.html
import num2words
import crcmod.predefined #pip

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
answer_histogram = {}
question_count = 0
crc16_dict = {}

#==========================
#==========================
#==========================
def number_to_letter(integer):
	"""
	Convert a number to its alphabetical representation.
	"""
	#letters = 'ABCDEFGHJKMNPQRSTUWXYZ'
	#letters = 'abcdefghijklmnopqrstuvwxyz'
	letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	if integer < 1 or integer > len(letters):
		raise ValueError(f"Invalid input: {integer}. Must be between 1 and {len(letters)}.")
	return letters[integer-1]
assert number_to_letter(3) == 'C'

#==========================
def number_to_lowercase(integer):
	"""
	Convert a number to its alphabetical representation.
	"""
	#letters = 'ABCDEFGHJKMNPQRSTUWXYZ'
	lowercase_letters = 'abcdefghijklmnopqrstuvwxyz'
	if integer < 1 or integer > len(lowercase_letters):
		raise ValueError
	return lowercase_letters[integer-1]
assert number_to_lowercase(3) == 'c'

#==========================
def number_to_ordinal(integer):
	"""
	Convert a number to its ordinal representation.
	Args:
		integer (int): A positive integer to be converted.
	Returns:
		str: The ordinal representation of the number in English.
	"""
	return num2words.num2words(integer, to='ordinal', lang='en_US')
assert number_to_ordinal(3) == 'third'

#==========================
def number_to_cardinal(integer):
	"""
	Convert a number to its cardinal representation.
	Args:
		integer (int): A positive integer to be converted.
	Returns:
		str: The cardinal representation of the number in English.
	"""
	return num2words.num2words(integer, to='cardinal', lang='en_US')
assert number_to_cardinal(3) == 'three'

#==============================================================
# Convert a number to its Roman numeral representation.
def number_to_roman(integer: int) -> str:
	"""Convert a number to its Roman numeral representation."""
	val_map = [
		(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
		(100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
		(10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
	]
	roman_numeral = ''
	for value, numeral in val_map:
		while integer >= value:
			roman_numeral += numeral
			integer -= value
	return roman_numeral
assert number_to_roman(3) == 'III'
assert number_to_roman(9) == 'IX'
assert number_to_roman(44) == 'XLIV'
assert number_to_roman(1999) == 'MCMXCIX'

#==============================================================
# Check if choices in choices_list start with a prefix pattern.
def has_prefix(choices_list: list) -> bool:
	"""Determine if items in choices_list start with a common prefix using regex."""
	# Define regex pattern to match common prefixes such as letters, numbers, and symbols.
	prefix_pattern = re.compile(r'^[A-Za-z0-9][\.\:\)]\s*')
	# Define regex pattern to properly remove HTML tags
	html_tag_pattern = re.compile(r'<[^>]+>')
	# Iterate through choices to check for the presence of prefixes
	for choice in choices_list:
		# Remove proper HTML tags before checking for prefix
		cleaned_choice = re.sub(html_tag_pattern, '', choice)
		if not prefix_pattern.match(cleaned_choice):
			return False  # If any choice does not match, return False
	# If all choices have a recognized prefix, return True
	return True

#==========================
def get_crc16_from_string(mystr):
	crc16 = crcmod.predefined.Crc('xmodem')
	try:
		crc16.update(mystr.encode('ascii', errors='strict'))
	except UnicodeEncodeError:
		checkAscii(mystr)
		raise ValueError
	return crc16.hexdigest().lower()

#==========================
def checkAscii(mystr):
	#destructive function
	mystr = mystr.replace('. ', '\n')
	mystr = mystr.replace(', ', '\n')
	mystr = mystr.replace('<p>', '\n')
	mystr = mystr.replace('</p>', '\n')
	mystr = mystr.replace('<br/>', '\n')
	mystr = mystr.replace('\n\n', '\n')
	for i,line in enumerate(mystr.split('\n')):
		for j,c in enumerate(list(line)):
			try:
				c.encode('ascii', errors='strict')
			except UnicodeEncodeError:
				print(line)
				print(i, j, c)
				print("^ is not ascii")
				raise ValueError
	return True

#==========================
def make_question_pretty(question):
	pretty_question = copy.copy(question)
	#print(len(pretty_question))
	pretty_question = re.sub(r'\<table .+\<\/table\>', '\n[TABLE]\n', pretty_question)
	pretty_question = re.sub(r'\<table .*\<\/table\>', '\n[TABLE]\n', pretty_question)
	if '<table' in pretty_question or '</table' in pretty_question:
		print("MISSED A TABLE")
		print(pretty_question)
		raise ValueError
		pass
	#print(len(pretty_question))
	pretty_question = re.sub('&nbsp;', ' ', pretty_question)
	pretty_question = re.sub(r'<h[0-9]\>', '<p>', pretty_question)
	pretty_question = re.sub('<br/>', '\n', pretty_question)
	pretty_question = re.sub('<li>', '\n* ', pretty_question)
	pretty_question = re.sub('<span [^>]*>', ' ', pretty_question)
	pretty_question = re.sub(r'<\/?strong>', ' ', pretty_question)
	pretty_question = re.sub(r'<\/?[bi]>', ' ', pretty_question)
	pretty_question = re.sub('</span>', '', pretty_question)
	pretty_question = re.sub(r'\<hr\/\>', '', pretty_question)
	pretty_question = re.sub(r'\<\/p\>\s*\<p\>', '\n', pretty_question)
	pretty_question = re.sub(r'\<p\>\s*\<\/p\>', '\n', pretty_question)
	pretty_question = re.sub(r'\n\<\/p\>', '', pretty_question)
	pretty_question = re.sub(r'\n\<p\>', '\n', pretty_question)
	pretty_question = re.sub('\n\n', '\n', pretty_question)
	pretty_question = re.sub('  *', ' ', pretty_question)

	# Define subscript and superscript mappings
	pretty_question = convert_sub_sup(pretty_question)

	pretty_question = html.unescape(pretty_question)
	#print(len(pretty_question))
	return pretty_question

#=====================
def convert_sub_sup(pretty_question):
	"""Replace <sub> and <sup> HTML tags with Unicode equivalents using regex."""

	# Define subscript and superscript mappings
	subscript_map = str.maketrans("0123456789+-=()", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")
	superscript_map = str.maketrans("0123456789+-=()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")

	# Convert <sub> tags
	def subscript_replace(match):
		return match.group(1).translate(subscript_map)

	# Convert <sup> tags
	def superscript_replace(match):
		return match.group(1).translate(superscript_map)

	# Replace <sub> and <sup> content using regex
	pretty_question = re.sub(r'<sub>(.*?)</sub>', subscript_replace, pretty_question)
	pretty_question = re.sub(r'<sup>(.*?)</sup>', superscript_replace, pretty_question)

	return pretty_question

#==============
# This function formats HTML content using the lxml library.
def format_html_lxml(html_string):
	"""
	Format an HTML string using lxml library for cleaner output.

	Args:
		html_string (str): The HTML content to be formatted.

	Returns:
		str: The formatted HTML string.
	"""
	# Create an HTML parser that removes blank text nodes
	parser = lxml.html.HTMLParser(remove_blank_text=True)
	# Parse the input HTML string into an HTML tree
	tree = lxml.html.fromstring(html_string, parser=parser)
	# Convert the parsed HTML tree to a formatted string with indentation and line breaks
	formatted_html = lxml.etree.tostring(tree, pretty_print=True, encoding="unicode").strip()
	# Ensure the string is formatted for HTML output
	formatted_html = lxml.etree.tostring(tree, pretty_print=True, encoding="unicode", method="html").strip()
	formatted_html = formatted_html.replace("&amp;", "&")
	# Return the formatted HTML string
	return formatted_html

#=====================
def question_header(question: str, N: int, crc16: str = None) -> str:
	"""
	Generate a standardized header for a question.

	Args:
		question (str): The question text.
		N (int): The question ID or number.
		crc16 (str): Optional CRC16 checksum for uniqueness (default: None).

	Returns:
		str: Formatted question header.
	"""
	# Generate a CRC16 if not provided
	if crc16 is None:
		crc16 = get_crc16_from_string(question)

	# Log the question header
	print(f"{N:03d}. {crc16} -- {make_question_pretty(question)}")

	# Generate the header
	header = f"<p>{crc16}</p>\n"
	header +=  insert_hidden_terms(question)

	return header

#==============

def choice_header(choice_text: str, index: int) -> str:
	"""
	Format a choice in a standardized way.

	Args:
		choice_text (str): The text of the choice.
		index (int): The index of the choice (e.g., 0 for 'A', 1 for 'B').

	Returns:
		str: Formatted choice header.
	"""
	# Generate a label for the choice (e.g., A, B, C, ...)
	letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
	label = letters[index]

	# Log the choice
	print(f"- [{label}] {make_question_pretty(choice_text)}")

	# Add hidden terms for obfuscation, if needed
	noisy_choice_text = insert_hidden_terms(choice_text)

	# Wrap in a div or any other required format
	return add_no_click_div(f"{label}. {noisy_choice_text}")

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
def add_no_click_div(text):
	#global use_add_no_click_div
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
