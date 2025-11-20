ENGINE_NAME = "okla_chrst_bqgen"

from qti_package_maker.common import string_functions

#==============================================================
def _format_choices(choices_list, correct_set):
	lines = []
	for idx, choice in enumerate(choices_list, start=1):
		prefix = string_functions.number_to_lowercase(idx)  # a, b, c...
		marker = "*" if choice in correct_set else ""
		lines.append(f"{marker}{prefix}) {choice}")
	return "\n".join(lines) + "\n\n"

#==============================================================
def MC(item_cls):
	"""Multiple Choice (single answer)."""
	header = f"{item_cls.item_number}. {item_cls.question_text}\n"
	correct_set = {item_cls.answer_text}
	return header + _format_choices(item_cls.choices_list, correct_set)

#==============================================================
def MA(item_cls):
	"""Multiple Answer (checkbox style)."""
	header = f"{item_cls.item_number}. {item_cls.question_text}\n"
	correct_set = set(item_cls.answers_list)
	return header + _format_choices(item_cls.choices_list, correct_set)

#==============================================================
def MATCH(item_cls):
	"""Matching prompt/answer pairs separated by '/'."""
	header = f"match {item_cls.item_number}. {item_cls.question_text}\n"
	lines = []
	for idx, (prompt, choice) in enumerate(zip(item_cls.prompts_list, item_cls.choices_list), start=1):
		prefix = string_functions.number_to_lowercase(idx)
		lines.append(f"{prefix}) {prompt}/{choice}")
	return header + "\n".join(lines) + "\n\n"

#==============================================================
def NUM(item_cls):
	"""Not supported for this engine."""
	return None

#==============================================================
def FIB(item_cls):
	"""Single blank: show acceptable answers."""
	header = f"blank {item_cls.item_number}. {item_cls.question_text}\n"
	lines = []
	for idx, ans in enumerate(item_cls.answers_list, start=1):
		prefix = string_functions.number_to_lowercase(idx)
		lines.append(f"*{prefix}. {ans}")
	return header + "\n".join(lines) + "\n\n"

#==============================================================
def MULTI_FIB(item_cls):
	"""Not supported for this engine."""
	return None

#==============================================================
def ORDER(item_cls):
	"""Not supported for this engine."""
	return None
