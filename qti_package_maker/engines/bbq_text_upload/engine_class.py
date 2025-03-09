
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.bbq_text_upload import write_item
from qti_package_maker.engines.bbq_text_upload import read_package

class EngineClass(base_engine.BaseEngine):
	def __init__(self, package_name: str, verbose: bool=False):
		# Call the base engine constructor
		super().__init__(package_name, verbose)
		# set the write_item module (required)
		self.write_item = write_item
		# Verify that the correct write_item module is imported
		self.validate_write_item_module()

	#==============
	def read_items_from_file(self, infile: str):
		new_item_bank = read_package.read_items_from_file(infile)
		return new_item_bank

	#==============
	def save_package(self, item_bank, outfile: str = None):
		outfile = self.get_outfile_name('bbq', 'txt', outfile)
		assessment_items_tree = self.process_item_bank(item_bank)
		# Write assessment items to the file
		with open(outfile, "w") as f:
			count = 0
			for formatted_bbq_text in assessment_items_tree:
				# no inner newlines allowed
				formatted_bbq_text = formatted_bbq_text.replace('\n', ' ').strip()
				# Ensure each item is on a new line
				f.write(formatted_bbq_text + "\n")
				count += 1
		if self.verbose is True:
			print(f"Saved {count} assessment items to {outfile}")
		return outfile
