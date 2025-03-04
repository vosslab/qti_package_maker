#!/usr/bin/env python

# Standard Library
import re

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines.bbq_text_upload.engine_class import BBQTextEngine
from qti_package_maker.engines.html_selftest.engine_class import HTMLSelfTest
from qti_package_maker.engines.human_readable.engine_class import HumanReadable
from qti_package_maker.engines.canvas_qti_v1_2.engine_class import QTIv1Engine
from qti_package_maker.engines.blackboard_qti_v2_1.engine_class import QTIv2Engine

class MasterQTIPackage:
	def __init__(self, package_name: str, engine_name: str, verbose: bool=False):
		package_name = package_name.strip()
		self.verbose = verbose
		if not package_name:
			raise ValueError("package_name not defined")
		# Convert to lowercase
		engine_name = engine_name.lower()
		# Remove non-alphanumeric characters
		engine_name = re.sub("[^a-z0-9]", "", engine_name)
		if engine_name.startswith('bbq') or engine_name.startswith('blackboardtext'):
			# blackboard_text_upload
			self.engine = BBQTextEngine(package_name, verbose)
		elif engine_name.startswith('html'):
			# blackboard_text_upload
			self.engine = HTMLSelfTest(package_name, verbose)
		elif engine_name.startswith('human'):
			# human_readable
			self.engine = HumanReadable(package_name, verbose)
		elif engine_name.startswith('qtiv1') or engine_name.startswith('canvas'):
			# canvas_qti_v1_2
			self.engine = QTIv1Engine(package_name, verbose)
		elif engine_name.startswith('qtiv2') or engine_name.startswith('blackboardqti'):
			# blackboard_qti_v2_1
			self.engine = QTIv2Engine(package_name, verbose)
		else:
			raise ValueError(f"Unknown engine: {engine_name}")
		if self.verbose is True:
			print(f"Initialized Engine: {self.engine.engine_name}")

	#=====================================================================
	def add_question(self, question_type: str, question_tuple: tuple):
		""" General method to add a question to the engine. """
		supported_types = self.engine.get_available_question_types()
		if question_type not in supported_types:
			self.show_available_question_types()
			raise NotImplementedError(f"Error: Unsupported question type '{question_type}'")
		# Get method reference from `self.engine`, not `self`
		add_method = getattr(self.engine, question_type, None)
		if add_method is None:
			self.show_available_question_types()
			raise NotImplementedError(f"Error: No method found for question type '{question_type}'")
		# Check actual list length, not a counter
		prev_count = len(self.engine.assessment_items_tree)
		add_method(*question_tuple)
		# Verify that a new question was added
		if len(self.engine.assessment_items_tree) == prev_count:
			raise ValueError(f"Error: '{question_type}' failed to add a question")

	def add_MC(self, question_text: str, choices_list: list, answer_text: str):
		"""Handles adding a Multiple-Choice (MC) question."""
		self.engine.MC(question_text, choices_list, answer_text)

	def add_MA(self, question_text: str, choices_list: list, answers_list: list):
		"""Handles adding a Multiple-Answer (MA) question."""
		self.engine.MA(question_text, choices_list, answers_list)

	def add_MATCH(self, question_text: str, prompts_list: list, choices_list: list):
		"""Handles adding a Matching (MATCH) question."""
		self.engine.MATCH(question_text, prompts_list, choices_list)

	def add_FIB(self, question_text: str,  answers_list: list):
		"""Handles adding a Multiple-Choice (MC) question."""
		self.engine.FIB(question_text, answers_list)

	def add_MULTI_FIB(self, question_text: str, answer_map: dict):
		"""Handles adding a Multiple-Choice (MC) question."""
		self.engine.MULTI_FIB(question_text, answer_map)

	def add_NUM(self, question_text: str, answer_float: float,
				 tolerance_float: float, tolerance_message: bool=True):
		"""Handles adding a Multiple-Answer (MA) question."""
		self.engine.NUM(question_text, answer_float, tolerance_float, tolerance_message)

	def add_ORDER(self, question_text: str,  ordered_answers_list: list):
		"""Handles adding a Matching (MATCH) question."""
		self.engine.ORDER(question_text, ordered_answers_list)

	#=====================================================================
	def save_package(self, outfile: str=None):
		if self.verbose is True:
			print(
				f"Saving package {self.engine.package_name}\n"
				f"  with engine {self.engine.engine_name} and\n"
				f"  {len(self.engine.assessment_items_tree)} questions."
			)
		self.engine.save_package(outfile)

	#=====================================================================
	def show_available_question_types(self):
		self.engine.show_available_question_types()


#===========================================================
# This function serves as the entry point for generating and saving questions.
def main():
	"""
	Main function that orchestrates question generation and file output.
	"""

	# Parse arguments from the command line
	#args = parse_arguments()

	qti_packer = MasterQTIPackage('example_pool_from_test_maker')
	qti_packer.show_available_question_types()
	question_text = 'What is your favorite color?'
	answer_text = 'blue'
	choices_list = ['blue', 'red', 'yellow']
	qti_packer.add_MC(question_text, choices_list, answer_text)

	question_text = 'Which are types of fruit?'
	answers_list = ['orange', 'banana', 'apple']
	choices_list = ['orange', 'banana', 'apple', 'lettuce', 'spinach']
	qti_packer.add_MA(question_text, choices_list, answers_list)

	qti_packer.save_package()
