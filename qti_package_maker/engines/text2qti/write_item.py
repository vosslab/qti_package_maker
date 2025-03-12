
from qti_package_maker.common import string_functions

#==============================================================
def MC(item_cls):
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	question_text = item_cls.question_text
	choices_list = item_cls.choices_list
	answer_text = item_cls.answer_text
	output = [f"{item_cls.item_number}. {item_cls.question_text}"]
	for i, choice_text in enumerate(item_cls.choices_list, start=1):
		prefix = "*" if choice_text == item_cls.answer_text else ""
		letter = string_functions.number_to_letter(i)
		output.append(f"{prefix}{letter}) {choice_text}")
	return "\n".join(output) + "\n"

#==============================================================
def MA(item_cls):
	"""Create a Multiple Answer (Checkboxes) question."""
	output = [f"{item_cls.item_number}. {item_cls.question_text}"]
	for choice_text in item_cls.choices_list:
		prefix = "[*]" if choice_text in item_cls.answers_list else "[ ]"
		output.append(f"{prefix} {choice_text}")
	return "\n".join(output) + "\n"

#==============================================================
def NUM(item_cls):
	"""Create a Numerical question with an accepted tolerance range."""
	output = [f"{item_cls.item_number}. {item_cls.question_text}"]
	if item_cls.tolerance_float > 0:
		output.append(f"= {item_cls.answer_float} +- {item_cls.tolerance_float}")
	else:
		output.append(f"= {item_cls.answer_float}")
	return "\n".join(output) + "\n"

#==============================================================
def FIB(item_cls):
	"""Create a Fill-in-the-Blank (Single Blank) question."""
	output = [f"{item_cls.item_number}. {item_cls.question_text}"]
	for answer_text in item_cls.answers_list:
		output.append(f"* {answer_text}")
	return "\n".join(output) + "\n"

#==============================================================
def MATCH(item_cls):
	#item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	"""Create a Matching question where users match items from two lists."""
	raise NotImplementedError("text2qti does not have documentations on MATCH assessment items")

#==============================================================
# Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping.
def MULTI_FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping."""
	raise NotImplementedError("text2qti does not have documentations on MULTI_FIB assessment items")

#==============================================================
def ORDER(item_cls):
	#item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	"""Create an Ordered List question where users arrange items in a correct sequence."""
	raise NotImplementedError("text2qti does not have documentations on ORDER assessment items")
