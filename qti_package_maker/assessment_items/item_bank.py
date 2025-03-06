
# Standard Library
import inspect

# Pip3 Library

# QTI Package Maker
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
		if item_type not in self.item_classes:
			self.show_available_item_types()
			raise NotImplementedError(f"Error: Unsupported assessment item type '{item_type}'")
		self._validate_item_type(item_type)
		# Instantiate the assessment item
		item_instance = self.item_classes[item_type](*item_tuple)
		# Store in dictionary using item_crc as key to prevent duplicates
		self.items_dict[item_instance.item_crc] = item_instance

	#============================================
	def merge(self, other):
		"""
		Merges two ItemBank objects, ensuring no duplicate items.
		Args:
			other (ItemBank): Another ItemBank to merge with.
		Returns:
			ItemBank: A new ItemBank containing the union of assessment items.
		"""
		if not isinstance(other, ItemBank):
			raise TypeError("Can only merge with another ItemBank instance")
		# Ensure mixed types are not allowed if allow_mixed is False
		self._validate_item_type(other.first_item_type)
		merged_bank = ItemBank(allow_mixed=self.allow_mixed)
		# Merge dictionaries
		merged_bank.items_dict = {**self.items_dict, **other.items_dict}
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
