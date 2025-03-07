ENGINE_NAME = "html_selftest"

#from qti_package_maker.common import string_functions
from qti_package_maker.engines.html_selftest import add_MC
from qti_package_maker.engines.html_selftest import add_MA
from qti_package_maker.engines.html_selftest import add_MATCH
#from qti_package_maker.engines.html_selftest import add_NUM
#from qti_package_maker.engines.html_selftest import add_FIB
#from qti_package_maker.engines.html_selftest import add_MULTI_FIB
#from qti_package_maker.engines.html_selftest import add_ORDER

#==============================================================
def MC(item_cls):
	#item_number: int, item_crc16: str, question_text: str, choices_list: list, answer_text: str):
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	return add_MC.generate_html(item_cls.item_number, item_cls.item_crc16, item_cls.question_text, item_cls.choices_list, item_cls.answer_text)

#==============================================================
def MA(item_cls):
	#item_number: int, item_crc16: str, question_text: str, choices_list: list, answers_list: list):
	"""Create a Multiple Answer (Checkboxes) question."""
	return add_MA.generate_html(item_cls.item_number, item_cls.item_crc16, item_cls.question_text, item_cls.choices_list, item_cls.answers_list)

#==============================================================
def MATCH(item_cls):
	#item_number: int, item_crc16: str, question_text: str, prompts_list: list, choices_list: list):
	"""Create a Matching question where users match items from two lists."""
	return add_MATCH.generate_html(item_cls.item_number, item_cls.item_crc16, item_cls.question_text, item_cls.prompts_list, item_cls.choices_list)

#==============================================================
def NUM(item_cls):
	#item_number: int, item_crc16: str,
	#question_text: str, answer_float: float, tolerance_float: float, tolerance_message=True):
	"""Create a Numerical question with an accepted tolerance range."""
	#return add_NUM.generate_html(item_number, item_crc16, question_text, answer_float, tolerance_float, tolerance_message)
	raise NotImplementedError

#==============================================================
def FIB(item_cls):
	#item_number: int, item_crc16: str, question_text: str, answers_list: list):
	"""Create a Fill-in-the-Blank (Single Blank) question."""
	#return add_FIB.generate_html(item_number, item_crc16, question_text, answers_list)
	raise NotImplementedError

#==============================================================
# Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping.
def MULTI_FIB(item_cls):
	#item_number: int, item_crc16: str, question_text: str, answer_map: dict) -> str:
	"""Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping."""
	#return add_MULTI_FIB.generate_html(item_number, item_crc16, question_text, answer_map)
	raise NotImplementedError

#==============================================================
def ORDER(item_cls):
	#item_number: int, item_crc16: str, question_text: str, ordered_answers_list: list):
	"""Create an Ordered List question where users arrange items in a correct sequence."""
	#return add_ORDER.generate_html(item_number, item_crc16, question_text, ordered_answers_list)
	raise NotImplementedError

