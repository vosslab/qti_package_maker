
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.okla_chrst_bqgen import write_item
from qti_package_maker.engines.okla_chrst_bqgen import read_package


class EngineClass(base_engine.BaseEngine):
	"""
	Okla CHRST BQGEN text engine with read and write support.
	"""
	def __init__(self, package_name: str, verbose: bool = False):
		super().__init__(package_name, verbose)
		self.write_item = write_item
		self.validate_write_item_module()

	#============================================
	def read_items_from_file(self, infile: str, allow_mixed: bool = False):
		"""
		Read okla_chrst_bqgen text files into an ItemBank.
		"""
		return read_package.read_items_from_file(infile, allow_mixed=allow_mixed)

	#==============
	def save_package(self, item_bank, outfile: str = None):
		"""
		Write the item bank to an okla_chrst_bqgen formatted text file.
		"""
		outfile = self.get_outfile_name('okla', 'txt', outfile)
		assessment_items_tree = self.process_item_bank(item_bank)
		if len(assessment_items_tree) == 0:
			return None
		with open(outfile, "w") as f:
			count = 0
			for item_number, assessment_text in enumerate(assessment_items_tree, start=1):
				f.write(assessment_text)
				if not assessment_text.endswith("\n"):
					f.write("\n")
				count += 1
		if self.verbose:
			print(f"Saved {count} assessment items to {outfile}")
		return outfile
