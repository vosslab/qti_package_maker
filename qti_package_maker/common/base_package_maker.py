
# Standard Library
import inspect

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import validator
from qti_package_maker.common import string_functions

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
		#print(f"added assessment_item number {self.number_of_assessment_items} of type {item_type}")

	#==============
	def MC(self, question_text: str, choices_list: list, answer_text: str):
		title = None
		item_number = self.number_of_assessment_items + 1
		validator.validate_MC(question_text, choices_list, answer_text)
		crc16question = string_functions.get_crc16_from_string(question_text)
		choices_str = '|'.join(choices_list)
		crc16choice = string_functions.get_crc16_from_string(choices_str)
		crc16merge = f"{crc16question}_{crc16choice}"
		assessment_item_data = self.add_item.MC(item_number, crc16merge, question_text, choices_list, answer_text)
		function_name = inspect.currentframe().f_code.co_name
		self.add_assessment_item(title, crc16merge, function_name, assessment_item_data)

	#==============
	def MA(self, question_text: str, choices_list: list, answers_list: list):
		title = None
		item_number = self.number_of_assessment_items + 1
		validator.validate_MA(question_text, choices_list, answers_list)
		crc16question = string_functions.get_crc16_from_string(question_text)
		choices_str = '|'.join(choices_list)
		crc16choices = string_functions.get_crc16_from_string(choices_str)
		crc16merge = f"{crc16question}_{crc16choices}"
		assessment_item_data = self.add_item.MA(item_number, crc16merge, question_text, choices_list, answers_list)
		function_name = inspect.currentframe().f_code.co_name
		self.add_assessment_item(title, crc16merge, function_name, assessment_item_data)

	#==============
	def MATCH(self, question_text: str, prompts_list: list, choices_list: list):
		title = None
		item_number = self.number_of_assessment_items + 1
		validator.validate_MATCH(question_text, prompts_list, choices_list)
		crc16question = string_functions.get_crc16_from_string(question_text)
		prompts_str = '|'.join(prompts_list)
		crc16prompts = string_functions.get_crc16_from_string(prompts_str)
		crc16merge = f"{crc16question}_{crc16prompts}"
		assessment_item_data = self.add_item.MATCH(item_number, crc16merge, question_text, prompts_list, choices_list)
		function_name = inspect.currentframe().f_code.co_name
		self.add_assessment_item(title, crc16merge, function_name, assessment_item_data)

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
