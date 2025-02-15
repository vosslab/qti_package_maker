# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import string_functions

#==============================================================
def MC(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	pass

#==============================================================
def MA(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_list: list):
	"""Create a Multiple Answer (Checkboxes) question."""
	pass

#==============================================================
def MATCH(item_number: int, crc16_text: str, question_text: str, answers_list: list, matching_list: list):
	"""Create a Matching question where users match items from two lists."""
	pass

#==============================================================
def NUM(item_number: int, crc16_text: str, question_text: str, answer: float, tolerance: float, tol_message=True):
	"""Create a Numerical question with an accepted tolerance range."""
	pass

#==============================================================
def FIB(item_number: int, crc16_text: str, question_text: str, answers_list: list):
	"""Create a Fill-in-the-Blank (Single Blank) question."""
	pass

#==============================================================
def MULTI_FIB(item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping."""
	pass

#==============================================================
def ORDER(item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	"""Create an Ordered List question where users arrange items in a correct sequence."""
	pass
