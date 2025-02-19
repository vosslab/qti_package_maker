#!/usr/bin/env python

# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines.human_readable.engine_class import HumanReadable
from qti_package_maker.engines.canvas_qti_v1_2.engine_class import QTIv1Engine
from qti_package_maker.engines.blackboard_qti_v2_1.engine_class import QTIv2Engine
from qti_package_maker.engines.blackboard_text_upload.engine_class import BBQTextEngine

class MasterQTIPackage:
	def __init__(self, package_name: str, engine_name: str):
		engine_name = engine_name.lower()
		if engine_name.startswith('qti_v1') or engine_name.startswith('canvas'):
			self.engine = QTIv1Engine(package_name)
		elif engine_name.startswith('qti_v2'):
			self.engine = QTIv2Engine(package_name)
		elif engine_name.startswith('human'):
			self.engine = HumanReadable(package_name)
		elif engine_name.startswith('bbq'):
			self.engine = BBQText(package_name)
		else:
			raise ValueError(f"Unknown engine: {engine_name}")
		print(f"Initialized Engine: {self.engine.engine_name}")

	def add_MC(self, question_text: str, choices_list: list, answer_text: str):
		self.engine.MC(question_text, choices_list, answer_text)

	def add_MA(self, question_text: str, choices_list: list, answers_list: list):
		self.engine.MA(question_text, choices_list, answers_list)

	def add_MATCH(self, question_text: str, answers_list: list, matching_list: list):
		self.engine.MATCH(question_text, answers_list, matching_list)

	def save_package(self):
		print(
			f"Saving package {self.engine.package_name}\n"
			f"  with engine {self.engine.engine_name} and\n"
			f"  {len(self.engine.assessment_items_tree)} questions."
		)
		self.engine.save_package()

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
