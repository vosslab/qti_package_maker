
# Standard Library
import os

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import base_package_maker
from qti_package_maker.engine_human_readable import add_item

class HumanReadable(base_package_maker.BaseEngine):
	def __init__(self, package_name: str):
		super().__init__(package_name)

		# Verify that the correct add_item module is imported
		if not hasattr(add_item, "ENGINE_NAME") or add_item.ENGINE_NAME != "human_readable":
			raise ImportError("Incorrect add_item module imported for HumanReadable engine")

		self.add_item = add_item

	#==============
	def save_package(self, outfile: str = None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		if not outfile:
			outfile = f"{self.package_name}.txt"

		with open(outfile, "w") as f:
			count = 0
			for item_number, assessment_item_dict in enumerate(self.assessment_items_tree, start=1):
				item_type = assessment_item_dict['item_type']
				assessment_text = assessment_item_dict['assessment_item_data']
				if item_type.lower() == 'match':
					f.write(f"match {item_number}. {assessment_text}")
				else:
					f.write(f"{item_number}. {assessment_text}")
				count += 1
		print(f"Saved {count} assessment items to {outfile}")
