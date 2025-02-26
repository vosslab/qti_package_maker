
# Standard Library
import os

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import base_package_maker
from qti_package_maker.engines.bbq_text_upload import add_item

class BBQTextEngine(base_package_maker.BaseEngine):
	def __init__(self, package_name: str):
		super().__init__(package_name)
		# Verify that the correct add_item module is imported
		if not hasattr(add_item, "ENGINE_NAME") or add_item.ENGINE_NAME != "bbq_text_upload":
			raise ImportError("Incorrect add_item module imported for HumanReadable engine")
		self.add_item = add_item

	#==============
	def save_package(self, outfile: str=None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		if not outfile:
			outfile = f"bbq-{self.package_name}-questions.txt"
		if os.path.exists(outfile):
			outfile = f"new_{outfile}"
		with open(outfile, "w") as f:
			count = 0
			for assessment_item_dict in self.assessment_items_tree:
				formatted_bbq_text = assessment_item_dict['assessment_item_data']
				f.write(formatted_bbq_text)
				count += 1
		print(f"Saved {count} assessment items to {outfile}")
