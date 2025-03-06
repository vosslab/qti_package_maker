#!/usr/bin/env python

# Standard Library
import re

# Pip3 Library

# QTI Package Maker
from qti_package_maker.assessment_items import item_bank
from qti_package_maker.engines.engine_registration import ENGINE_REGISTRY

class QTIPackageInterface:
	#=====================================================================
	def __init__(self, package_name: str, input_engine_name: str, verbose: bool = False):
		package_name = package_name.strip()
		self.verbose = verbose
		self.item_bank = item_bank.ItemBank()
		if not package_name:
			raise ValueError("package_name not defined")
		self._set_engine_data()

	#=====================================================================
	def _set_engine_data(self):
		self.engine_data = {}
		for engine_info in ENGINE_REGISTRY.values():
			self.engine_data['name'] =
				{
					"name": engine_info["engine_name"],
					"can_read": engine_info["can_read"],
					"can_write": engine_info["can_write"],
					"class": engine_info["engine_class"]
				}

	#=====================================================================
	def init_engine(self, input_engine_name: str):
		"""Retrieve the engine class based on the given engine name."""
		input_engine_name = re.sub(r"[^a-z0-9]", "", input_engine_name.lower())

		# Use preloaded engine data
		for engine_info in self.engine_data:
			engine_name = re.sub(r"[^a-z0-9]", "", engine_info["name"].lower())
			if input_engine_name.startswith(engine_name):
				engine_cls = engine_info["class"](self.package_name, self.verbose)
				if self.verbose:
					print(f"Initialized Engine: {engine_cls.__class__.__name__} ({engine_info['name']})")
				return engine_cls

		raise ValueError(f"Unknown engine: {input_engine_name}")

	#=====================================================================
	def show_available_engines(self):
		"""
		Print all registered engines and their capabilities in a formatted tabulate table.
		"""
		engine_data = []
		for key, engine_info in ENGINE_REGISTRY.items():
			engine_data.append([
				engine_info["engine_name"],
				engine_info["can_read"],
				engine_info["can_write"]
			])

		# Print the engine table
		print("\nAvailable Engines")
		print(tabulate(engine_data, headers=["Engine Name", "Can Read", "Can Write"], tablefmt="grid"))

	#=====================================================================
	def summarize_item_bank(self):
		"""Print all registered engines and their capabilities."""
		self.item_bank.summarize_items()

	#=====================================================================
	def print_item_bank_histogram(self):
		"""Print all registered engines and their capabilities."""
		self.item_bank.print_histogram()

	#=====================================================================
	def add_item(self, item_type: str, item_tuple: tuple):
		self.item_bank.add_item(item_type, item_tuple)

	#=====================================================================
	def read_package(self, input_file: str, engine_name: str):
		"""
		Reads an assessment package from the given input file and loads items into the item bank.
		"""
		engine_cls = self.load_engine(engine_name)

		# Ensure the selected engine supports reading
		if not hasattr(engine_cls, "read_items"):
			raise NotImplementedError(f"Engine {self.engine.__class__.__name__} does not support reading.")

		# Retrieve the assessment items from the input file
		self.item_bank += engine_cls.read_items_from_file(input_file)

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
	def save_package(self, engine_name: str, outfile: str = None):
		"""
		Saves the current item bank using the specified engine.
		"""
		if len(self.item_bank) == 0:
			print("No assessment items to write, skipping save_package()")
			return

		engine_cls = self.init_engine(engine_name)  # Initialize the engine
		if not hasattr(engine_cls, "save_package"):
			raise NotImplementedError(f"Engine {engine_cls.name} does not support writing.")

		if self.verbose:
			print(
				f"Saving package {engine_cls.name}\n"
				f"  with {len(self.item_bank)} assessment items."
			)
		engine_cls.save_package(self.item_bank, outfile)

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
