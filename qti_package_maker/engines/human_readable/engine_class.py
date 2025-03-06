
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import base_package_maker
from qti_package_maker.engines.human_readable import write_item

class EngineClass(base_package_maker.BaseEngine):
	def __init__(self, package_name: str, verbose: bool=False):
		super().__init__(package_name, verbose)
		# Verify that the correct write_item module is imported
		if not hasattr(write_item, "ENGINE_NAME") or write_item.ENGINE_NAME != "human_readable":
			raise ImportError("Incorrect write_item module imported for HumanReadable engine")
		self.write_item = write_item

	#==============
	def save_package(self, item_bank, outfile: str = None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		outfile = self.get_outfile_name('human', 'txt', outfile)
		assessment_items_tree = self.process_item_bank(item_bank)
		# Write assessment items to the file
		with open(outfile, "w") as f:
			count = 0
			for assessment_text in assessment_items_tree:
				f.write(assessment_text)
				count += 1
		if self.verbose is True:
			print(f"Saved {count} assessment items to {outfile}")
