
# Standard Library
import re
import inspect
from collections import defaultdict

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import string_functions
from qti_package_maker.assessment_items import item_types

class ItemBank:
	"""
	A centralized storage system for assessment items using a dictionary keyed by CRC codes.
	"""
	def __init__(self, allow_mixed: bool = False):
		"""Initialize an empty item bank."""
		# Boolean if mixed item types are allow in the same item bank
		self.allow_mixed = allow_mixed
		# Dictionary to store items keyed by item_crc
		self.items_dict = {}
		# item_types and their class definitions
		self.item_classes = self._discover_item_classes()
		# Track the first added item type
		self.first_item_type = None
		self.used_item_types_set = set()
		self.crc16_pattern = re.compile(r"\b([0-9a-f]{4})(?:_[0-9a-f]{4})*\b")
		self.item_type_pattern = re.compile(r"^[A-Z_]+$")

	#============================================
	def _discover_item_classes(self):
		"""
		Dynamically find all assessment item classes in item_types.py.
		Returns:
			dict: Mapping of item type names to their corresponding classes.
		"""
		classes = {}
		for name, obj in inspect.getmembers(item_types, inspect.isclass):
			if issubclass(obj, item_types.BaseItem) and obj is not item_types.BaseItem:
				classes[name.upper()] = obj
		return classes

	#============================================
	def get_available_item_types(self):
		"""Returns a list of available assessment item types."""
		return list(self.item_classes.keys())

	#============================================
	def show_available_item_types(self):
		"""Prints the available assessment item types."""
		print("Available Assessment Item Types:")
		for item_type in self.get_available_item_types():
			print(f"- {item_type}")

	#============================================
	def summarize_item_bank(self):
		"""Summarizes the count of each item type in items_dict."""
		item_type_counts = defaultdict(int)
		# Count item types
		for item_cls in self.items_dict.value():
			item_type_counts[item_cls.item_type] += 1
		# Sort the dictionary by item_type
		sorted_items = sorted(item_type_counts.items(), key=lambda x: x[0], reverse=True)
		# Print results
		print("count\titem_type")
		for item_type, count in sorted_items:
			print(f"{count}\t{item_type}")

	#============================================
	def print_histogram_item_bank(self):
		"""
		Summarizes the count of each item type in items_dict and prints histograms for supported types.
		"""
		if len(self.items_dict) == 0:
			return
		# Check if 'MC' type items exist and print their histogram
		if 'MC' in self.used_item_types_set:
			self.print_histogram_MC_items()
		# Check if 'MA' type items exist and print their histogram
		if 'MA' in self.used_item_types_set:
			self.print_histogram_MA_items()

	#============================================
	def print_histogram_MC_items(self):
		"""
		Prints a histogram summarizing the distribution of answers for Multiple Choice (MC) items.
		"""
		answer_counts = defaultdict(int)
		# Iterate through MC items and count occurrences of each answer index
		for item_cls in self.items_dict.values():
			if item_cls.item_type != "MC":
				continue
			answer_counts[item_cls.answer_index] += 1
		# Determine the highest answer index found
		max_index = max(answer_counts.keys())
		# Compute the total number of answers for percentage calculation
		total_answers = sum(answer_counts.values())
		# Print histogram summary
		print("Multiple Choice (MC) Histogram")
		for index in range(max_index + 1):
			letter = string_functions.number_to_letter(index + 1)
			count = answer_counts[index]
			percent = 100 * count / float(total_answers)
			print(f"{letter}: {count} ({percent:.1f}%)")

	#============================================
	def print_histogram_MA_items(self):
		"""
		Prints a histogram summarizing the distribution of answers for Multiple Answer (MA) items.
		"""
		answer_counts = defaultdict(int)
		# Iterate through MA items and count occurrences of each answer index
		for item_cls in self.items_dict.values():
			if item_cls.item_type != "MA":
				continue
			for index in item_cls.answer_index_list:
				answer_counts[index] += 1
		# Determine the highest answer index found
		max_index = max(answer_counts.keys())
		# Compute the total number of answers for percentage calculation
		total_answers = sum(answer_counts.values())
		# Print histogram summary
		print("Multiple Answer (MA) Histogram")
		for index in range(max_index + 1):
			letter = string_functions.number_to_letter(index + 1)
			count = answer_counts[index]
			percent = 100 * count / float(total_answers)
			print(f"{letter}: {count} ({percent:.1f}%)")

	#============================================
	def _validate_item_type(self, item_type):
		"""
		Ensures consistency of item types if allow_mixed is False.
		"""
		if self.allow_mixed:
			return
		if self.first_item_type is None:
			# Set the first item type
			self.first_item_type = item_type
			return
		if self.first_item_type == item_type:
			return
		raise ValueError("Error: Mixing item types is not allowed. "
			+ f"First type was '{self.first_item_type}', attempted to add '{item_type}'")

	#============================================
	def add_item(self, item_type: str, item_tuple: tuple):
		"""
		General method to add an assessment item to the bank.
		Args:
			item_type (str): The type of assessment item.
			item_tuple (tuple): The parameters needed to create the item.
		"""
		item_type = item_type.upper()
		# Validate item_type format pattern of (ALL CAPS + UNDERSCORES ONLY)
		if not self.item_type_pattern.fullmatch(item_type):
			self.show_available_item_types()
			raise ValueError(f"Invalid item_type format: '{item_type}'.")
		if item_type not in self.item_classes:
			self.show_available_item_types()
			raise NotImplementedError(f"Error: Unsupported assessment item type '{item_type}'")
		self._validate_item_type(item_type)
		# Instantiate the assessment item
		item_instance = self.item_classes[item_type](*item_tuple)
		# Validate CRC16 format pattern of (4-character hex pairs separated by underscores)
		item_crc = item_instance.item_crc
		if not self.crc16_pattern.fullmatch(item_crc):
			raise ValueError(f"Invalid CRC16 format: '{item_crc}'")
		# Store in dictionary using item_crc as key to prevent duplicates
		self.items_dict[item_crc] = item_instance
		self.used_item_types_set.add(item_type)

	#============================================
	def get_item_list(self):
		"""
		Returns a list of all assessment item objects in the bank.
		"""
		return list(self.items_dict.values())

	#============================================
	def merge(self, other):
		"""
		Merges two ItemBank objects, ensuring no duplicate items.
		Args:
			other (ItemBank): Another ItemBank to merge with.
		Returns:
			ItemBank: A new ItemBank containing the union of assessment items.
		"""
		# Ensure that the object being merged is an instance of ItemBank
		if not isinstance(other, ItemBank):
			raise TypeError("Can only merge with another ItemBank instance")
		# Determine the new allow_mixed value after merging
		# If either ItemBank allows mixed types, the merged ItemBank will too
		merged_allow_mixed = self.allow_mixed or other.allow_mixed
		# Ensure mixed types are not allowed if allow_mixed is False
		# If allow_mixed is False and item types do not match, raise an error
		if not merged_allow_mixed and self.first_item_type != other.first_item_type:
			raise ValueError("Error: Mixing item types is not allowed. "
				+ f"First type was '{self.first_item_type}', attempted to add '{other.first_item_type}'")
		# Create a new merged ItemBank with the determined allow_mixed setting
		merged_bank = ItemBank(allow_mixed=merged_allow_mixed)
		# Merge dictionaries, ensuring no duplicate items by keying with item_crc
		merged_bank.items_dict = self.items_dict | other.items_dict
		# Merge sets to track all used item types from both banks
		merged_bank.used_item_types_set = self.used_item_types_set | other.used_item_types_set
		# Return the new merged ItemBank
		return merged_bank

	#============================================
	def union(self, other):
		"""Alias for merging two ItemBank"""
		return self.merge(other)

	#============================================
	def __or__(self, other):
		"""Alias for merging two ItemBank objects using the `|` operator."""
		return self.merge(other)

	#============================================
	def __add__(self, other):
		"""Alias for merging two ItemBank objects using the `+` operator."""
		return self.merge(other)

	#============================================
	def __len__(self):
		"""Returns the number of items in the ItemBank."""
		return len(self.items_dict)
