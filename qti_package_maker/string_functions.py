
# Standard Library
import re
import os
import copy
import random
import subprocess

# Pip3 Library
#import lxml
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
	pretty_question = re.sub(r'h[0-9]\>', 'p>', pretty_question)
	pretty_question = re.sub('<br/>', '\n', pretty_question)
	pretty_question = re.sub('<li>', '\n* ', pretty_question)
	pretty_question = re.sub('<span [^>]*>', ' ', pretty_question)
	pretty_question = re.sub(r'<\/?strong>', ' ', pretty_question)
	pretty_question = re.sub('</span>', '', pretty_question)
	pretty_question = re.sub(r'\<hr\/\>', '', pretty_question)
	pretty_question = re.sub(r'\<\/p\>\s*\<p\>', '\n', pretty_question)
	pretty_question = re.sub(r'\<p\>\s*\<\/p\>', '\n', pretty_question)
	pretty_question = re.sub(r'\n\<\/p\>', '', pretty_question)
	pretty_question = re.sub(r'\n\<p\>', '\n', pretty_question)
	pretty_question = re.sub('\n\n', '\n', pretty_question)
	pretty_question = re.sub('  *', ' ', pretty_question)

	#print(len(pretty_question))
	return pretty_question

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
