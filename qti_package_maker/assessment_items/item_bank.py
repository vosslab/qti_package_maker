
import inspect
from qti_package_maker.assessment_items import base_item

class ItemBank:
	"""
	A centralized storage system for assessment items.
	"""
	def __init__(self, allow_mixed: bool=False):
		"""Initialize an empty item bank."""
		self.items_tree = []
		self.item_classes = self._discover_item_classes()
		self.allow_mixed = allow_mixed
		# Track the first added item type
		self.item_type = None

	#============================================
	def _discover_item_classes(self):
		"""
		Dynamically find all assessment item classes in base_item.py.
		Returns:
			dict: Mapping of item type names to their corresponding classes.
		"""
		classes = {}
		for name, obj in inspect.getmembers(base_item, inspect.isclass):
			if issubclass(obj, base_item.BaseItem) and obj is not base_item.BaseItem:
				classes[name.upper()] = obj
		return classes

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

		# Ensure consistency if allow_mixed is False
		if not self.allow_mixed:
			if self.item_type is None:
				self.item_type = item_type  # Set the first item type
			elif self.item_type != item_type:
				raise ValueError("Error: Mixing item types is not allowed. "
					+ f"First type was '{self.item_type}', attempted to add '{item_type}'")

		# Instantiate the assessment item and add it to the item bank
		item_instance = self.item_classes[item_type](*item_tuple)
		self.items.append(item_instance)

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
	def __or__(self, other):
		"""
		Merges two ItemBank objects, removing duplicates based on question text.
		Args:
			other (ItemBank): Another ItemBank to merge with.
		Returns:
			ItemBank: A new ItemBank containing the union of assessment items.
		"""
		if not isinstance(other, ItemBank):
			raise TypeError("Can only merge with another ItemBank instance")

		# Ensure mixed types are not allowed if allow_mixed is False
		if not self.allow_mixed and other.items:
			first_type = self.items[0].__class__.__name__ if self.items else None
			for item in other.items:
				if first_type and item.__class__.__name__ != first_type:
					raise ValueError("Error: Mixing item types is not allowed. "
					  + f"Found '{item.__class__.__name__}' in merged bank.")

		merged_bank = ItemBank(allow_mixed=self.allow_mixed)
		unique_items = {item.question_text: item for item in self.items + other.items}
		merged_bank.items = list(unique_items.values())
		return merged_bank

	#============================================
	def __len__(self):
		"""Returns the number of items in the ItemBank."""
		return len(self.items)
