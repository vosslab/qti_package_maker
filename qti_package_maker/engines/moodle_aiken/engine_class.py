
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.moodle_aiken import write_item

class EngineClass(base_engine.BaseEngine):
	"""
	Moodle Aiken writer for multiple-choice text exports.
	"""
	def __init__(self, package_name: str, verbose: bool=False):
		# Call the base engine constructor
		super().__init__(package_name, verbose)
		# set the write_item module (required)
		self.write_item = write_item
		# Verify that the correct write_item module is imported
		self.validate_write_item_module()

	#==============
	def read_package(self, infile: str):
		"""
		Read is not supported for this engine.
		"""
		raise NotImplementedError

	#==============
	def save_package(self, item_bank, outfile: str = None):
		outfile = self.get_outfile_name('aiken', 'txt', outfile)
		assessment_items_tree = self.process_item_bank(item_bank)
		if len(assessment_items_tree) == 0:
			return None
		# Write assessment items to the file
		with open(outfile, "w") as f:
			count = 0
			for item_num, assessment_text in enumerate(assessment_items_tree, start=1):
				f.write(assessment_text)
				count += 1
		if self.verbose is True:
			print(f"Saved {count} assessment items to {outfile}")
		return outfile
