
# Standard Library
import inspect

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import string_functions
from qti_package_maker.common import validator

# engine_base.py (shared base for all engines)
class BaseEngine:
	#==============
	def __init__(self, package_name: str):
		self.package_name = package_name
		#need to override is engine class
		self.add_item = None
		self.assessment_items_tree = []
		self.number_of_assessment_items = 0

	#==============
	def save_package(self):
		raise NotImplementedError

	#==============
	@property
	def engine_name(self):
		# Dynamically get the class name
		return self.__class__.__name__

	#==============
	def add_assessment_item(self, title: str, crc16: str, item_type: str, assessment_item_data):
		assessment_item_dict = {
			'title': title,
			'crc16': crc16,
			'item_type': item_type,
			'assessment_item_data': assessment_item_data,
			}
		self.assessment_items_tree.append(assessment_item_dict)
		self.number_of_assessment_items += 1
		print(f"added assessment_item number {self.number_of_assessment_items} of type {item_type}")

	#==============
	def MC(self, question_text: str, choices_list: list, answer_text: str):
		title = None
		validator.validate_MC(question_text, choices_list, answer_text)
		crc16question = string_functions.get_crc16_from_string(question_text)
		choices_str = '|'.join(choices_list)
		crc16choice = string_functions.get_crc16_from_string(choices_str)
		crc16 = f"{crc16question}_{crc16choice}"
		assessment_item_data = self.add_item.MC(question_text, choices_list, answer_text)
		function_name = inspect.currentframe().f_code.co_name
		self.add_assessment_item(title, crc16, function_name, assessment_item_data)

	#==============
	def MA(self, question_text: str, choices_list: list, answers_list: list):
		title = None
		validator.validate_MA(question_text, choices_list, answers_list)
		crc16question = string_functions.get_crc16_from_string(question_text)
		choices_str = '|'.join(choices_list)
		crc16choices = string_functions.get_crc16_from_string(choices_str)
		crc16merge = f"{crc16question}_{crc16choices}"
		assessment_item_data = self.add_item.MA(question_text, choices_list, answers_list)
		function_name = inspect.currentframe().f_code.co_name
		self.add_assessment_item(title, crc16merge, function_name, assessment_item_data)

	#==============
	def MATCH(self, question_text: str, answers_list: list, matching_list: list):
		title = None
		validator.validate_MATCH(question_text, answers_list, matching_list)
		crc16question = string_functions.get_crc16_from_string(question_text)
		answers_str = '|'.join(answers_list)
		crc16answers = string_functions.get_crc16_from_string(answers_str)
		crc16merge = f"{crc16question}_{crc16answers}"
		assessment_item_data = self.add_item.MATCH(question_text, answers_list, matching_list)
		function_name = inspect.currentframe().f_code.co_name
		self.add_assessment_item(title, crc16merge, function_name, assessment_item_data)

	#==============
	def show_available_question_types(self):
		# Get all callable functions from the add_item module
		if self.add_item:
			functions = []
			for name in dir(self.add_item):
				if callable(getattr(self.add_item, name)) and not name.startswith("__"):
					functions.append(name)
			print(f"Available question types: {', '.join(functions)}")
		else:
			print(f"No add_item module assigned for engine {self.engine_name}.")
