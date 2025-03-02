
# Standard Library
import os
import re
import inspect
from collections import defaultdict

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import validator
from qti_package_maker.common import string_functions

# engine_base.py (shared base for all engines)
class BaseEngine:
	#==============
	def __init__(self, package_name: str):
		self.package_name = package_name
		self.assessment_items_tree = []
		self.number_of_assessment_items = 0
		self.crc16_pattern = re.compile(r"\b([0-9a-f]{4})(?:_[0-9a-f]{4})*\b")
		self.item_type_pattern = re.compile(r"^[A-Z_]+$")
		#self.add_item must be overridden in all implementations of engine class
		self.add_item = None

	#==============
	def save_package(self, outfile: str=None):
		raise NotImplementedError

	#==============
	@property
	def engine_name(self):
		# Dynamically get the class name
		return self.__class__.__name__

	#==============
	def add_assessment_item(self, crc16: str, item_type: str, assessment_item_data):
		"""Stores the assessment item in the internal structure."""
		# Validate CRC16 format pattern of (4-character hex pairs separated by underscores)
		if not self.crc16_pattern.fullmatch(crc16):
			raise ValueError(f"Invalid CRC16 format: '{crc16}'")
		# Validate item_type format pattern of (ALL CAPS + UNDERSCORES ONLY)
		if not self.item_type_pattern.fullmatch(item_type):
			raise ValueError(f"Invalid item_type format: '{item_type}'.")
		# Catch both `None` and empty structures like `{}` or `[]`
		if assessment_item_data is None or not assessment_item_data:
			raise ValueError(f"Error: 'assessment_item_data' is empty for item_type '{item_type}'")
		# Debugging print to confirm it's being called
		print(f"Adding assessment item: {item_type}, CRC16: {crc16}")
		# Format item dict
		assessment_item_dict = {
				'crc16': crc16,
				'item_type': item_type,
				'assessment_item_data': assessment_item_data,
		}
		# Append to list
		self.assessment_items_tree.append(assessment_item_dict)
		self.number_of_assessment_items += 1

	#==============
	def summarize_assessment_items(self):
		"""Summarizes the count of each item type in assessment_items_tree."""
		item_type_counts = defaultdict(int)  # Fix: Use `int` for default zero values
		# Count item types
		for item in self.assessment_items_tree:
			item_type = item['item_type']
			item_type_counts[item_type] += 1
		# Sort the dictionary by item_type
		sorted_items = sorted(item_type_counts.items(), key=lambda x: x[0], reverse=True)
		# Print results
		print("count\titem_type")
		for item_type, count in sorted_items:
			print(f"{count}\t{item_type}")

	#==============
	def process_assessment_item(self, item_type: str, question_text: str, crc16secondary: str, *args):
		"""
		Processes different types of assessment items before adding them.
			item_type: The type of assessment item (e.g., "MC", "MA", "MATCH", etc.).
			question_text: The main question text.
			crc16secondary: Precomputed CRC16 for additional data (choices, answers, etc.).
			Additional arguments required for each type (choices, answers, etc.).
		"""
		# Validate CRC16 format pattern of (4-character hex pairs separated by underscores)
		if not self.crc16_pattern.fullmatch(crc16secondary):
			raise ValueError(f"Invalid CRC16 format: '{crc16secondary}'")
		# Validate item_type format pattern of (ALL CAPS + UNDERSCORES ONLY)
		if not self.item_type_pattern.fullmatch(item_type):
			raise ValueError(f"Invalid item_type format: '{item_type}'.")
		item_number = self.number_of_assessment_items + 1
		# Step 1: Validate the item
		validate_function = getattr(validator, f"validate_{item_type}")
		validate_function(question_text, *args)
		# Step 2: Compute CRC16 for question text
		crc16question = string_functions.get_crc16_from_string(question_text)
		# Step 3: Merge CRC16 hashes
		crc16merge = f"{crc16question}_{crc16secondary}"
		# Step 4: Call the appropriate add_item function dynamically
		add_item_function = getattr(self.add_item, item_type)
		assessment_item_data = add_item_function(item_number, crc16merge, question_text, *args)
		# Step 5: Store the processed assessment item
		self.add_assessment_item(crc16merge, item_type, assessment_item_data)

	#==============
	# Wrapper functions with explicit item type and CRC16 computation
	def MC(self, question_text: str, choices_list: list, answer_text: str):
		item_type = "MC"
		if inspect.currentframe().f_code.co_name != item_type:
			raise ValueError(f"Please update question type to {item_type}")
		crc16secondary = string_functions.get_crc16_from_string('|'.join(choices_list))
		self.process_assessment_item(item_type, question_text, crc16secondary, choices_list, answer_text)

	#==============
	def MA(self, question_text: str, choices_list: list, answers_list: list):
		item_type = "MA"
		if inspect.currentframe().f_code.co_name != item_type:
			raise ValueError(f"Please update question type to {item_type}")
		crc16secondary = string_functions.get_crc16_from_string('|'.join(choices_list))
		self.process_assessment_item(item_type, question_text, crc16secondary, choices_list, answers_list)

	#==============
	def MATCH(self, question_text: str, prompts_list: list, choices_list: list):
		item_type = "MATCH"
		if inspect.currentframe().f_code.co_name != item_type:
			raise ValueError(f"Please update question type to {item_type}")
		# Compute CRC16 from both lists combined
		crc16secondary = string_functions.get_crc16_from_string('|'.join(prompts_list+choices_list))
		self.process_assessment_item(item_type, question_text, crc16secondary, prompts_list, choices_list)

	#==============
	def NUM(self, question_text: str, answer_float: float, tolerance_float: float, tolerance_message=True):
		item_type = "NUM"
		if inspect.currentframe().f_code.co_name != item_type:
			raise ValueError(f"Please update question type to {item_type}")
		crc16secondary = string_functions.get_crc16_from_string(f"{answer_float:.2e},{tolerance_float:.2e}")
		self.process_assessment_item(item_type, question_text, crc16secondary, answer_float, tolerance_float, tolerance_message)

	#==============
	def FIB(self, question_text: str, answers_list: list):
		item_type = "FIB"
		if inspect.currentframe().f_code.co_name != item_type:
			raise ValueError(f"Please update question type to {item_type}")
		crc16secondary = string_functions.get_crc16_from_string('|'.join(answers_list))
		self.process_assessment_item(item_type, question_text, crc16secondary, answers_list)

	#==============
	def MULTI_FIB(self, question_text: str, answer_map: dict):
		item_type = "MULTI_FIB"
		if inspect.currentframe().f_code.co_name != item_type:
			raise ValueError(f"Please update question type to {item_type}")
		answer_map_str = '|'.join(f"{k}:{v}" for k, v in sorted(answer_map.items()))
		crc16secondary = string_functions.get_crc16_from_string(answer_map_str)
		self.process_assessment_item(item_type, question_text, crc16secondary, answer_map)

	#==============
	def ORDER(self, question_text: str, ordered_answers_list: list):
		item_type = "ORDER"
		if inspect.currentframe().f_code.co_name != item_type:
				raise ValueError(f"Please update question type to {item_type}")
		crc16secondary = string_functions.get_crc16_from_string('|'.join(ordered_answers_list))
		self.process_assessment_item(item_type, question_text, crc16secondary, ordered_answers_list)

	#==============
	def get_available_question_types(self) -> list:
		""" Returns a list of available question types based on callable methods in `add_item`. """
		if not self.add_item:
			print(f"No add_item module assigned for engine {self.engine_name}.")
			return []
		# Extract function names dynamically
		functions = [
			name for name in dir(self.add_item)
			if callable(getattr(self.add_item, name)) and not name.startswith("__")
		]
		return functions

	#==============
	def show_available_question_types(self):
		""" Displays the available question types. """
		available_types = self.get_available_question_types()
		if available_types:
			print(f"Available question types: {', '.join(available_types)}")
		else:
			print(f"No available question types found for engine {self.engine_name}.")

	#==============
	def get_outfile_name(self, prefix: str, extension: str, outfile: str = None) -> str:
		"""Generate an output filename based on prefix and extension unless the user specifies one."""
		# If the user provides an outfile, return it unchanged
		if outfile:
			return outfile
		# Default to self.package_name if no outfile is provided
		outfile = self.package_name
		# Ensure the prefix is added if it's missing
		if not outfile.startswith(f"{prefix}-"):
			outfile = f"{prefix}-{outfile}"
		# Extract the root filename (remove existing extension)
		outfile_root, _ = os.path.splitext(outfile)
		# Construct the final filename with the correct extension
		return f"{outfile_root}.{extension}"
