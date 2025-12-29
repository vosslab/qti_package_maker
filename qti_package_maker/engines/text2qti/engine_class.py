
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.text2qti import write_item
from qti_package_maker.engines.text2qti import read_package

class EngineClass(base_engine.BaseEngine):
	"""
	Text2qti engine for the plain-text format used by the text2qti reader and writer.
	Supports reading and writing text2qti files.
	"""
	def __init__(self, package_name: str, verbose: bool = False):
		"""
		Initializes the text2qti engine with the package name.
		Args:
			package_name (str): Name of the package being processed.
			verbose (bool): Whether to print debug information.
		"""
		# Call the base engine constructor
		super().__init__(package_name, verbose)
		# set the write_item module (required)
		self.write_item = write_item
		# Verify that the correct write_item module is imported
		self.validate_write_item_module()

	#============================================
	def read_items_from_file(self, infile: str, allow_mixed: bool = False):
		"""
		Read text2qti questions from a text file and return an ItemBank.
		"""
		new_item_bank = read_package.read_items_from_file(infile, allow_mixed=allow_mixed)
		return new_item_bank

	#============================================
	def save_package(self, item_bank, outfile: str = None):
		"""
		Write the item bank to a text2qti-formatted text file.
		"""
		outfile = self.get_outfile_name('text2qti', 'txt', outfile)
		assessment_items_tree = self.process_item_bank(item_bank)
		# Write assessment items to the file
		with open(outfile, "w") as f:
			count = 0
			for item_text in assessment_items_tree:
				f.write(item_text)
				count += 1
		if self.verbose is True:
			print(f"Saved {count} assessment items to {outfile}")
		return outfile
