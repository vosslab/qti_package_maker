
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.bbq_text_upload import write_item
from qti_package_maker.engines.bbq_text_upload import read_package

class EngineClass(base_engine.BaseEngine):
	def __init__(self, package_name: str, verbose: bool=False):
		super().__init__(package_name, verbose)
		# Verify that the correct write_item module is imported
		if not hasattr(write_item, "ENGINE_NAME") or write_item.ENGINE_NAME != "bbq_text_upload":
			raise ImportError(f"Incorrect write_item module imported for {self.name} engine")
		self.write_item = write_item
		self.validate_write_item_module()

	#==============
	def read_package(self, infile: str):
		new_item_bank = read_package.read_items_from_file(infile)
		return new_item_bank

	#==============
	def save_package(self, item_bank, outfile: str = None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
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
