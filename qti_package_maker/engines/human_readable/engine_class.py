
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import base_package_maker
from qti_package_maker.engines.human_readable import write_item

class HumanReadable(base_package_maker.BaseEngine):
	def __init__(self, package_name: str, verbose: bool=False):
		super().__init__(package_name, verbose)
		# Verify that the correct write_item module is imported
		if not hasattr(write_item, "ENGINE_NAME") or write_item.ENGINE_NAME != "human_readable":
			raise ImportError("Incorrect write_item module imported for HumanReadable engine")
		self.write_item = write_item

	#==============
	def save_package(self, outfile: str = None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		outfile = self.get_outfile_name('human', 'txt', outfile)
		# Write assessment items to the file
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
		if self.verbose is True:
			print(f"Saved {count} assessment items to {outfile}")
