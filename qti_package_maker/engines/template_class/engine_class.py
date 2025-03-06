
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import base_package_maker
from qti_package_maker.engines.human_readable import write_item

# Standard Library
import os

# QTI Package Maker
from qti_package_maker.engines import base_engine

class EngineClass(base_engine.BaseEngine):
	"""
	Template engine class for developers to use as a reference.
	This is not an actual engine but provides a structured example.
	"""
	ENGINE_NAME = "template_engine"

	def __init__(self, package_name: str, verbose: bool = False):
		"""
		Initializes the template engine with the package name.
		Args:
			package_name (str): Name of the package being processed.
			verbose (bool): Whether to print debug information.
		"""
		# Call the base engine constructor
		super().__init__(package_name, verbose)

	#============================================
	def read_package(self, infile: str):
		"""
		Placeholder method for reading a package.
		Raises NotImplementedError since this is a template.
		"""
		raise NotImplementedError("read_package() must be implemented in a real engine class.")

	#==============
	def save_package(self, item_bank, outfile: str = None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		raise NotImplementedError("save_package() must be implemented in a real engine class.")
		outfile = self.get_outfile_name('human', 'txt', outfile)
		assessment_items_tree = self.process_item_bank(item_bank)
		# Write assessment items to the file
		with open(outfile, "w") as f:
			count = 0
			for item_number, assessment_item_dict in enumerate(assessment_items_tree, start=1):
				item_type = assessment_item_dict['item_type']
				assessment_text = assessment_item_dict['assessment_item_data']
				if item_type.lower() == 'match':
					f.write(f"match {item_number}. {assessment_text}")
				else:
					f.write(f"{item_number}. {assessment_text}")
				count += 1
		if self.verbose is True:
			print(f"Saved {count} assessment items to {outfile}")
