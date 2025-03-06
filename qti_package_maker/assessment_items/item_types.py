
# Standard Library
import time

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import string_functions

class BaseItem:
	"""Base class for all assessment items."""
	def __init__(self, question_text):
		self.timestamp = time.time()
		self.question_text = question_text
		self.question_crc16 = string_functions.get_crc16_from_string(question_text)
		if not hasattr(self, 'options_crc16'):
			raise AttributeError("Assessment Items must override and set their 'options_crc16' value")
		self.item_crc = f"{self.question_crc16}_{self.options_crc16}"

#============================================
class MC(BaseItem):
	def __init__(self, question_text: str, choices_list: list, answer_text: str):
		self.choices_list = choices_list
		self.answer_text = answer_text
		options_string = "|".join(choices_list)
		self.options_crc16 = string_functions.get_crc16_from_string(options_string)
		super().__init__(question_text)

#============================================
class MA(BaseItem):
	def __init__(self, question_text: str, choices_list: list, answers_list: list):
		self.choices_list = choices_list
		self.answers_list = answers_list
		options_string = "|".join(choices_list)
		self.options_crc16 = string_functions.get_crc16_from_string(options_string)
		super().__init__(question_text)

#============================================
class MATCH(BaseItem):
	def __init__(self, question_text: str, prompts_list: list, choices_list: list):
		self.prompts_list = prompts_list
		self.choices_list = choices_list
		options_string = "|".join(prompts_list+choices_list)
		self.options_crc16 = string_functions.get_crc16_from_string(options_string)
		super().__init__(question_text)

#============================================
class NUM(BaseItem):
	def __init__(self, question_text: str, answer_float: float, tolerance_float: float, tolerance_message=True):
		self.answer_float = answer_float
		self.tolerance_float = tolerance_float
		self.tolerance_message = tolerance_message
		options_string = f"{answer_float:.2e}_{tolerance_float:.2e}"
		self.options_crc16 = string_functions.get_crc16_from_string(options_string)
		super().__init__(question_text)

#============================================
class FIB(BaseItem):
	def __init__(self, question_text: str, answers_list: list):
		self.answers_list = answers_list
		options_string = "|".join(answers_list)
		self.options_crc16 = string_functions.get_crc16_from_string(options_string)
		super().__init__(question_text)

#============================================
class MULTI_FIB(BaseItem):
	def __init__(self, question_text: str, answer_map: dict):
		self.answer_map = answer_map
		options_string = "|".join(answer_map.values())
		self.options_crc16 = string_functions.get_crc16_from_string(options_string)
		super().__init__(question_text)

#============================================
class ORDER(BaseItem):
	def __init__(self, question_text: str, ordered_answers_list: list):
		self.ordered_answers_list = ordered_answers_list
		options_string = "|".join(ordered_answers_list)
		self.options_crc16 = string_functions.get_crc16_from_string(options_string)
		super().__init__(question_text)
