
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.text2qti import write_item
from qti_package_maker.engines.text2qti import read_package

class EngineClass(base_engine.BaseEngine):
	"""
	Template engine class for developers to use as a reference.
	This is not an actual engine but provides a structured example.
	"""
	def __init__(self, package_name: str, verbose: bool = False):
		"""
		Initializes the template engine with the package name.
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
	def read_items_from_file(self, infile: str):
		"""
		Placeholder method for reading a package.
		Raises NotImplementedError since this is a template.
		"""
		new_item_bank = read_package.read_items_from_file(infile)
		return new_item_bank

	#============================================
	def save_package(self, item_bank, outfile: str = None):
		"""
		Placeholder method for reading a package.
		Raises NotImplementedError since this is a template.
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
