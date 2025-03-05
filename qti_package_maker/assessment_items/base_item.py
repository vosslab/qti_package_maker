#!/usr/bin/env python

# Standard Library
import time

# Pip3 Library

# QTI Package Maker


class BaseItem:
"""Base class for all assessment items."""
	def __init__(self, question_text):
		self.timestamp = time.time()
		self.question_text = question_text
		self.question_crc = ""

class MC(BaseItem):
	def __init__(self, question_text, choices, answer):
		super().__init__(question_text)
		self.choices = choices
		self.answer = answer

class MA(BaseItem):
	def __init__(self, question_text, choices, answers):
		super().__init__(question_text)
		self.choices = choices
		self.answers = answers

class MATCH(BaseItem):
	def __init__(self, question_text, prompts, choices):
		super().__init__(question_text)
		self.prompts = prompts
		self.choices = choices

class FIB(BaseItem):
	def __init__(self, question_text, answers):
		super().__init__(question_text)
		self.answers = answers

class MULTI_FIB(BaseItem):
	def __init__(self, question_text, answer_map):
		super().__init__(question_text)
		self.answer_map = answer_map

class NUM(BaseItem):
	def __init__(self, question_text, answer_float, tolerance_float, tolerance_message=True):
		super().__init__(question_text)
		self.answer_float = answer_float
		self.tolerance_float = tolerance_float
		self.tolerance_message = tolerance_message

class ORDER(BaseItem):
	def __init__(self, question_text, ordered_answers):
		super().__init__(question_text)
		self.ordered_answers = ordered_answers
