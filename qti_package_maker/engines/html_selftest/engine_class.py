
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.html_selftest import write_item

class EngineClass(base_engine.BaseEngine):
	def __init__(self, package_name: str, verbose: bool=False):
		super().__init__(package_name, verbose)
		# Verify that the correct write_item module is imported
		if not hasattr(write_item, "ENGINE_NAME") or write_item.ENGINE_NAME != "html_selftest":
			raise ImportError(f"Incorrect write_item module imported for {self.name} engine")
		self.write_item = write_item

	#==============
	def read_package(self, infile: str):
		raise NotImplementedError

	#==============
	def save_package(self, item_bank, outfile: str = None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		if len(item_bank) == 0:
			print("No items to write out skipping")
			return
		outfile = self.get_outfile_name('selftest', 'html', outfile)
		# Write assessment items to the file
		formatted_html_text = self.process_one_item_from_item_bank(item_bank)
		with open(outfile, "w") as f:
			# only one problem per file, only write one
			f.write(formatted_html_text)
		if self.verbose is True:
			print(f"Saved one assessment item to {outfile}")
