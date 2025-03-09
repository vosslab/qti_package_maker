
# Standard Library
import os
import re
import random

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import string_functions

# =====================================================================================

class AntiCheat:
	"""
	Applies anti-cheating protections to assessment content.

	Features:
	- Inserts hidden terms to track unauthorized content sharing.
	- Wraps text in a no-click div to prevent copying, selection, and right-click.
	- Injects anti-copy JavaScript to block printing and screenshots.
	"""

	def __init__(self, hidden_terms=False, no_click_div=False, anticopy_script=False):
		"""
		Initializes anti-cheating settings.
		"""
		# 1. Hidden Terms: Inserts nearly invisible words to detect unauthorized content-sharing.
		self.use_insert_hidden_terms = hidden_terms
		self.hidden_term_density = 0.7  # Probability of inserting hidden terms
		self.hidden_term_bank = self._load_hidden_term_bank()

		# 2. No-Click Div: Prevents right-click, text selection, copying, and context menu.
		# Enable/Disable anti-click div wrapper
		self.use_no_click_div = no_click_div

		# 3. Anti-Copy JavaScript: Prevents printing, copying, and screenshots.
		self.use_anticopy_script = anticopy_script
		# Additional settings
		self.noPrint = True  # Disable printing
		self.noCopy = True  # Disable copying
		self.noScreenshot = False  # Disable screenshots (not foolproof)
		self.autoBlur = True  # Blur content when switching tabs (prevents screen recording)

	# ============= MODIFY ITEM TYPE CLASS =================

	def modify_item_cls(self, item_cls):
		"""
		Applies anti-cheating modifications to an assessment item.

		- Modifies `question_text`
		- Modifies each supporting field dynamically

		Args:
				item_cls (BaseItem): The assessment item object.

		Returns:
				BaseItem: A new item instance with anti-cheat modifications.
		"""
		# Copy item to avoid modifying the original
		item_copy = item_cls.copy()
		# Modify question text
		item_copy.question_text = self.modify_string(item_copy.question_text)
		# Modify supporting fields dynamically
		for field_name in item_copy.get_supporting_field_names():
				value = getattr(item_copy, field_name)
				if isinstance(value, str):
					setattr(item_copy, field_name, self.modify_string(value))
				elif isinstance(value, list):
					setattr(item_copy, field_name, self.modify_list(value))
		return item_copy

	# ============= MODIFY STRINGS/LISTS =============

	def modify_list(self, string_list):
		"""
		Applies anti-cheating modifications to a list of strings.
		"""
		return [self.modify_string(text) for text in string_list]

	def modify_string(self, string_text):
		"""
		Applies anti-cheating modifications to a single string.

		- Inserts hidden terms (if enabled)
		- Wraps in a no-click div (if enabled)
		- Injects anti-copy JavaScript (if enabled)

		Returns:
				str: Modified text with anti-cheating protections.
		"""
		if self.use_insert_hidden_terms:
			string_text = self.insert_hidden_terms(string_text, self.hidden_term_bank)
		if self.use_no_click_div:
			string_text = wrap_text_in_no_click_div(string_text)
		if self.use_anticopy_script:
			js_function_string = self.get_anticopy_js_function()
			string_text = js_function_string + string_text  # Prepend JavaScript
		return string_text


	# =======================================================================
	# Anti-Copy JavaScript: Disables printing, copying, and screenshots
	# =======================================================================


	def get_anticopy_js_function(self):
		"""
		Generates JavaScript to prevent various forms of content theft.

		- `noPrint`: Disables printing via `window.print()`
		- `noCopy`: Disables right-click and copying
		- `noScreenshot`: Attempts to block screenshots (not foolproof)
		- `autoBlur`: Detects tab-switching and blurs content

		Returns:
			str: JavaScript `<script>` tag with anti-copy functionality.
		"""
		js_code = (
			'<script>'
			f'var noPrint={str(self.noPrint).lower()};'
			f'var noCopy={str(self.noCopy).lower()};'
			f'var noScreenshot={str(self.noScreenshot).lower()};'
			f'var autoBlur={str(self.autoBlur).lower()};'
			'</script>'
		)
		js_code += (
			'<script type="text/javascript" '
			'src="https://cdn.jsdelivr.net/gh/vosslab/biology-problems@main/javascript/noprint.js">'
			'</script>'
		)
		return js_code

	# =======================================================================
	# Hidden Terms: Embeds invisible markers to detect unauthorized sharing
	# =======================================================================

	# ============
	def _load_hidden_term_bank():
		"""
		Loads a list of hidden words from a predefined file.

		These words are inserted randomly into assessment content to help detect unauthorized content sharing.

		Returns:
			list: A list of words to be hidden in the text.
		"""
		git_root = string_functions.get_git_root(string_functions.__file__)
		data_file_path = os.path.join(git_root, 'data/all_short_words.txt')
		with open(data_file_path, 'r') as file:
			terms = file.readlines()
		return [term.strip() for term in terms]

	# ============
	def insert_hidden_terms(self, text_content):
		"""
		Randomly inserts hidden words into the text to detect unauthorized distribution.

		- Invisible words are added inside `<span>` elements with `font-size: 1px; color: white;`
		- Spaces between words are replaced with '@' to create valid insertion points.
		- Words inside `<table>` and `<code>` blocks are left untouched to avoid breaking syntax.

		Args:
			text_content (str): The original assessment content.

		Returns:
			str: The modified content with hidden words.
		"""
		if self.hidden_term_bank is None:
			raise ValueError()
		# Split the content into sections, preserving tables and code blocks
		parts = re.split(r'(<table>.*?</table>|<code>.*?</code>)', text_content, flags=re.DOTALL)
		new_parts = []
		for part in parts:
			if part.startswith('<table>') or part.startswith('<code>'):
				new_parts.append(part)  # Keep structured content unchanged
			else:
				part = re.sub(r'([a-z]) +([a-z])(?![^<>]*>)', r'\1@\2', part)  # Preserve inline elements
				words = part.split('@')  # Split words where spaces were
				new_words = []
				for word in words:
					new_words.append(word)
					if random.random() < self.hidden_term_density:
						hidden_term = random.choice(self.hidden_term_bank)
						new_words.append(f"<span style='font-size: 1px; color: white;'>{hidden_term}</span>")
					else:
						new_words.append(" ")  # Restore spaces
				new_parts.append(''.join(new_words))
		return ''.join(new_parts)

# =======================================================================
# Anti-Copy Protection: Prevents text selection, copying, right-clicking
# =======================================================================

def wrap_text_in_no_click_div(string_text):
	"""
	Wraps the given text in a non-clickable <div> to prevent copying, selecting, and right-clicking.

	- Blocks text selection
	- Disables context menu (right-click)
	- Prevents pasting and cutting
	- Stops onmousedown selection

	Args:
		string_text (str): The text content to be protected.

	Returns:
		str: Wrapped HTML string with anti-cheating properties.
	"""
	rand_crc16 = string_functions.get_random_crc16()  # Generate a unique identifier
	output = (
		f'<div id="drv_{rand_crc16}" '
			'oncopy="return false;" '
			'onpaste="return false;" '
			'oncut="return false;" '
			'oncontextmenu="return false;" '
			'onmousedown="return false;" '
			'onselectstart="return false;" '
		'>')
	output += string_text
	output += '</div>'
	return output






