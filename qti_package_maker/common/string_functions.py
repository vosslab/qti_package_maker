# Standard Library
import re
import copy
import html
import random

# Pip3 Library
import lxml.etree
import lxml.html
import num2words
import crcmod.predefined #pip

# QTI Package Maker
# none allowed here!!

#==========================
def number_to_letter(integer):
	"""
	Convert a number to its alphabetical representation.
	"""
	#letters = 'ABCDEFGHJKMNPQRSTUWXYZ'
	#letters = 'abcdefghijklmnopqrstuvwxyz'
	letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	if not (1 <= integer <= len(letters)):
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
	if not (1 <= integer <= len(lowercase_letters)):
		raise ValueError(f"Invalid input: {integer}. Must be between 1 and {len(lowercase_letters)}.")
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
			# If any choice does not match, return False
			return False
	# If all choices have a recognized prefix, return True
	return True

#==========================
def get_crc16_from_string(mystr):
	crc16 = crcmod.predefined.Crc('xmodem')
	try:
		crc16.update(mystr.encode('ascii', errors='strict'))
	except UnicodeEncodeError as e:
		check_ascii(mystr)
		raise ValueError(f"Cannot encode string to ASCII: {mystr}. Original error: {e}")
	return crc16.hexdigest().lower()

#==========================
def get_random_crc16():
	rand_crc16 = f"{random.randrange(16**4):04x}"
	return rand_crc16

#==========================
def check_ascii(mystr):
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
		raise ValueError("Table tag detected but not processed.")
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
	pretty_question = re.sub(r'\<\/?[^>]+\>', '', pretty_question)
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
	if '<script' in html_string or '</script>' in html_string:
		print("Warning: format_html_lxml() will cause syntax errors in JavaScript.")
		print("skipping...")
		return html_string
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

#========================================
def html_monospace(txt, use_nbsp=True):
	local_txt = copy.copy(txt)
	if use_nbsp is True:
		local_txt = local_txt.replace(' ', '&nbsp;')
	return f"<span style='font-family: monospace;'>{local_txt}</span>"

#==========================
def html_color_text(text, hex_code):
	return f'<span style="color: #{hex_code};">{text}</span>'

#=====================
def generate_gene_letters(num_genes: int, shift: int=-1, clear: bool=False) -> str:
	"""
	Generate a string of unique gene letters based on deterministic or random selection.
	"""
	# Define alphabets
	full_alphabet = "abcdefghijklmnopqrstuvwxyz"
	ambiguous_letters = "giloqsuvz"  # Ambiguous or easily confused letters
	clear_alphabet = ''.join(sorted(set(full_alphabet) - set(ambiguous_letters)))

	# Select alphabet based on the `clear` flag
	alphabet = clear_alphabet if clear else full_alphabet

	# Validate input
	if num_genes > len(alphabet):
		raise ValueError(f"num_genes ({num_genes}) cannot exceed the length of the alphabet ({len(alphabet)}).")

	if shift >= 0:
		# Generate a deterministic sequence with a valid shift
		shift = shift % (len(alphabet) - num_genes + 1)
		return alphabet[shift:shift + num_genes]
	else:
		# Generate random unique letters
		return ''.join(sorted(random.sample(alphabet, num_genes)))
assert generate_gene_letters(5, 3) == "defgh"  # Deterministic with full alphabet
assert generate_gene_letters(5, 3, clear=True) == "defhj"  # Deterministic with clear alphabet
assert len(generate_gene_letters(5)) == 5  # Random with full alphabet
