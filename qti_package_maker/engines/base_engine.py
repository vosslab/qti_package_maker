
# Standard Library
import os
import random

# Pip3 Library

# QTI Package Maker

# engine_base.py (shared base for all engines)
class BaseEngine:
	#==============
	def __init__(self, package_name: str, verbose: bool=False):
		self.package_name = package_name
		self.verbose = verbose
		#self.write_item must be overridden in all implementations of engine class
		self.write_item = None

	#==============
	def save_package(self, item_bank, outfile: str=None):
		raise NotImplementedError

	#==============
	@property
	def engine_name(self):
		# Dynamically get the class name
		return self.__class__.__name__

	#==============
	def process_one_item_from_item_bank(self, item_bank):
		"""
		Processes the given ItemBank and converts assessment items into the required format.
		"""
		if len(self.item_bank) == 0:
			print("No items to write out skipping")
			return
		item_cls = random.choice(item_bank.get_item_list())
		write_item_function = getattr(self.write_item, item_cls.item_type, None)
		if not write_item_function:
			print(f"Warning: No write function found for item type '{item_cls.item_type}'.")
			return
		item_engine_data = write_item_function(item_cls)
		return item_engine_data

	#==============
	def process_item_bank(self, item_bank):
		"""
		Processes the given ItemBank and converts assessment items into the required format.
		"""
		if len(item_bank) == 0:
			print("No items to write out skipping")
			return
		assessment_items_tree = []
		for item_cls in item_bank.get_item_list():
			write_item_function = getattr(self.write_item, item_cls.item_type, None)
			if not write_item_function:
				print(f"Warning: No write function found for item type '{item_cls.item_type}'.")
				return
			item_engine_data = write_item_function(item_cls)
			assessment_items_tree.append(item_engine_data)
		return assessment_items_tree

	#==============
	# Wrapper functions
	def MC(self, question_text: str, choices_list: list, answer_text: str):
		self.process_assessment_item("MC", question_text, choices_list, answer_text)
	#==============
	def MA(self, question_text: str, choices_list: list, answers_list: list):
		self.process_assessment_item("MA", question_text, choices_list, answers_list)
	#==============
	def MATCH(self, question_text: str, prompts_list: list, choices_list: list):
		self.process_assessment_item("MATCH", question_text, prompts_list, choices_list)
	#==============
	def NUM(self, question_text: str, answer_float: float, tolerance_float: float, tolerance_message=True):
		self.process_assessment_item("NUM", question_text, answer_float, tolerance_float, tolerance_message)
	#==============
	def FIB(self, question_text: str, answers_list: list):
		self.process_assessment_item("FIB", question_text, answers_list)
	#==============
	def MULTI_FIB(self, question_text: str, answer_map: dict):
		self.process_assessment_item("MULTI_FIB", question_text, answer_map)
	#==============
	def ORDER(self, question_text: str, ordered_answers_list: list):
		self.process_assessment_item("ORDER", question_text, ordered_answers_list)

	#==============
	def get_available_question_types(self) -> list:
		""" Returns a list of available question types based on callable methods in `write_item`. """
		if not self.write_item:
			print(f"No write_item module assigned for engine {self.engine_name}.")
			return []
		# Extract function names dynamically
		functions = [
			name for name in dir(self.write_item)
			if callable(getattr(self.write_item, name)) and not name.startswith("__")
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
