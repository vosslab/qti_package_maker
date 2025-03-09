
# Standard Library
import os
import random
import pathlib

# Pip3 Library

# QTI Package Maker


class BaseEngine:
	#==============
	def __init__(self, package_name: str, verbose: bool = False):
		self.package_name = package_name
		self.verbose = verbose
		self.name = self._get_name()
		# Must be overridden by child classes
		self.write_item = None

	#==============
	def _get_name(self) -> str:
		"""
		Returns the engine's directory name, assuming the engine class is inside:
		qti_package_maker/engines/<engine_name>/engine_class.py
		"""
		# Extract module path as a string
		module_string = self.__class__.__module__
		# Get the second-to-last element, which should be the engine folder name
		return module_string.split(".")[-2]

	#==============
	def validate_write_item_module(self):
		"""
		Validates that the correct write_item and read_package modules are imported.
		This should be called in subclasses after setting self.write_item and self.read_package.
		"""
		if not self.write_item:
			raise ImportError(f"No write_item module assigned for {self.name} engine.")
		write_item_path = pathlib.Path(self.write_item.__file__).resolve()
		if self.name not in write_item_path.parts:
			raise ImportError(f"Incorrect write_item module imported for {self.name} engine. "
					f"Expected to find {self.name} in {write_item_path}.")

	#==============
	def read_package(self, infile: str):
		raise NotImplementedError("Subclasses must implement read_package().")

	#==============
	def save_package(self, item_bank, outfile: str=None):
		raise NotImplementedError("Subclasses must implement save_package().")

	#==============
	def process_one_item_from_item_bank(self, item_bank):
		"""
		Processes the given ItemBank and converts assessment items into the required format.
		"""
		if len(item_bank) == 0:
			print("No items to write out skipping")
			return
		random.shuffle(item_bank)
		for item_cls in item_bank:
			write_item_function = getattr(self.write_item, item_cls.item_type, None)
			if not write_item_function:
				print(f"Warning: No write function found for item type '{item_cls.item_type}'.")
				continue
			item_engine_data = write_item_function(item_cls)
			if item_engine_data is not None:
				return item_engine_data
		return None

	#=============
	def process_item_bank(self, item_bank):
		"""
		Processes the given ItemBank and converts assessment items into the required format.
		"""
		if len(item_bank) == 0:
			print("No items to write, skipping processing.")
			return []
		assessment_items_tree = []
		for item_cls in item_bank:
			write_item_function = getattr(self.write_item, item_cls.item_type, None)
			if not write_item_function:
				print(f"Warning: No write function found for item type '{item_cls.item_type}'.")
				continue
			item_engine_data = write_item_function(item_cls)
			if item_engine_data is not None:
				assessment_items_tree.append(item_engine_data)
		return assessment_items_tree

	#==============
	def get_available_question_types(self) -> list:
		""" Returns a list of available question types based on callable methods in `write_item`. """
		if not self.write_item:
			print(f"No write_item module assigned for engine {self.name}.")
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
			print(f"No available question types found for engine {self.name}.")

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
