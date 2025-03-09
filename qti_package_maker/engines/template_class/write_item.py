ENGINE_NAME = "template_class"

#from qti_package_maker.common import string_functions

#==============================================================
def MC(item_cls):
	#item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	raise NotImplementedError("this is a template class, each engine must write their own function")

#==============================================================
def MA(item_cls):
	#item_number: int, crc16_text: str, question_text: str, choices_list: list, answers_list: list):
	"""Create a Multiple Answer (Checkboxes) question."""
	raise NotImplementedError("this is a template class, each engine must write their own function")

#==============================================================
def MATCH(item_cls):
	#item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	"""Create a Matching question where users match items from two lists."""
	#MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text
	raise NotImplementedError("this is a template class, each engine must write their own function")

#==============================================================
def NUM(item_cls):
	#item_number: int, crc16_text: str,
	#question_text: str, answer_float: float, tolerance_float: float, tolerance_message=True):
	"""Create a Numerical question with an accepted tolerance range."""
	raise NotImplementedError("this is a template class, each engine must write their own function")

#==============================================================
def FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answers_list: list):
	"""Create a Fill-in-the-Blank (Single Blank) question."""
	raise NotImplementedError("this is a template class, each engine must write their own function")

#==============================================================
# Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping.
def MULTI_FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping."""
	raise NotImplementedError("this is a template class, each engine must write their own function")

#==============================================================
def ORDER(item_cls):
	#item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	"""Create an Ordered List question where users arrange items in a correct sequence."""
	raise NotImplementedError("this is a template class, each engine must write their own function")
