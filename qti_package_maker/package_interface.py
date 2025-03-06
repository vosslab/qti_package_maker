#!/usr/bin/env python

# Standard Library
import re

# Pip3 Library

# QTI Package Maker
from qti_package_maker.item_bank import ItemBank
from qti_package_maker.engines.engine_registration import ENGINE_REGISTRY

class QTIPackageInterface:
	#=====================================================================
	def __init__(self, package_name: str, input_engine_name: str, verbose: bool = False):
		package_name = package_name.strip()
		self.verbose = verbose
		self.item_bank = ItemBank()
		if not package_name:
			raise ValueError("package_name not defined")
		self._init_engine(input_engine_name, verbose)

	#=====================================================================
	def _init_engine(self, input_engine_name: str, verbose: bool = False):
		"""Initialize the engine based on the given engine name."""
		# Normalize engine name
		input_engine_name = re.sub(r"[^a-z0-9]", "", input_engine_name.lower())
		# Match against registered engines
		for key, engine_info in ENGINE_REGISTRY.items():
			engine_name = re.sub(r"[^a-z0-9]", "", engine_info["engine_name"].lower())
			if input_engine_name.startswith(key) or input_engine_name.startswith(engine_name):
				self.engine = engine_info["engine_class"](self.package_name, verbose)
				break
		else:
			raise ValueError(f"Unknown engine: {input_engine_name}")
		if self.verbose:
			print(f"Initialized Engine: {self.engine.__class__.__name__} ({engine_info['engine_name']})")

	#=====================================================================
	def show_available_engines(self):
		"""Print all registered engines and their capabilities."""
		print("Available Engines:")
		for key, engine_info in ENGINE_REGISTRY.items():
			print(f"- {engine_info['engine_name']}"
				f"(can_read = {engine_info['can_read']})"
				f"(can_write = {engine_info['can_write']})"
			)

	#=====================================================================
	def add_item(self, item_type: str, item_tuple: tuple):
		self.item_bank.add_item(item_type, item_tuple)

	#=====================================================================
	def read_package(self, input_file: str):
		"""
		Reads an assessment package from the given input file and loads items into the item bank.
		"""
		# Ensure the selected engine supports reading
		if not hasattr(self.engine, "read_items"):
			raise NotImplementedError(f"Engine {self.engine.__class__.__name__} does not support reading.")

		# Retrieve the assessment items from the input file
		new_item_bank = self.engine.read_items(input_file)

		# If no items were read, notify the user and return
		if not new_item_bank or len(new_item_bank) == 0:
			print(f"Warning: No assessment items were found in the file: {input_file}.")
			return

		# Merge the newly read items into the existing item bank, avoiding duplicates
		self.item_bank |= new_item_bank

		# Provide detailed output if verbosity is enabled
		if self.verbose:
			print(
				f"Successfully loaded {len(new_item_bank)} new assessment items from {input_file}.\n"
				f"The item bank now contains a total of {len(self.item_bank)} unique assessment items."
			)

	#=====================================================================
	def save_package(self, outfile: str = None):
		if len(self.item_bank.items_tree) == 0:
			print("No assessment items to write, skipping save_package()")
			return
		if self.verbose is True:
			print(
				f"Saving package {self.engine.package_name}\n"
				f"  with engine {self.engine.engine_name} and\n"
				f"  {len(self.item_bank.items_tree)} assessment items."
			)
		self.engine.write_items(outfile, self.item_bank.items_tree)


#===========================================================
# This function serves as the entry point for generating and saving questions.
def main():
	"""
	Main function that orchestrates question generation and file output.
	"""

	# Parse arguments from the command line
	#args = parse_arguments()

	qti_packer = QTIPackageInterface('example_pool_from_test_maker')
	qti_packer.show_available_engines()

	question_text = 'What is your favorite color?'
	answer_text = 'blue'
	choices_list = ['blue', 'red', 'yellow']
	qti_packer.add_item("MC", (question_text, choices_list, answer_text))

	question_text = 'Which are types of fruit?'
	answers_list = ['orange', 'banana', 'apple']
	choices_list = ['orange', 'banana', 'apple', 'lettuce', 'spinach']
	qti_packer.add_item("MA", (question_text, choices_list, answers_list))

	qti_packer.save_package()

if __name__ == "__main__":
	main()
