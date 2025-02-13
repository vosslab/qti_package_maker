
# Standard Library
import os
import zipfile

# Pip3 Library
import lxml

# QTI Package Maker
from qti_package_maker.engine_human_readable import add_item
from qti_package_maker.common.base_package_maker import BaseEngine

class HumanReadable(BaseEngine):
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
			for item_number, (item_type, assessment_text) in enumerate(self.assessment_items, start=1):
				if item_type.lower() == 'match':
					f.write(f"match {item_number}. {assessment_text}")
				else:
					f.write(f"{item_number}. {assessment_text}")
				count += 1
		print(f"Saved {count} assessment items to {outfile}")
