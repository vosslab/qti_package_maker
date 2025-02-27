
# Standard Library
import os
import random

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import base_package_maker
from qti_package_maker.engines.html_selftest import add_item

class HTMLSelfTest(base_package_maker.BaseEngine):
	def __init__(self, package_name: str):
		super().__init__(package_name)
		# Verify that the correct add_item module is imported
		if not hasattr(add_item, "ENGINE_NAME") or add_item.ENGINE_NAME != "html_selftest":
			raise ImportError("Incorrect add_item module imported for HTMLSelfTest engine")
		self.add_item = add_item

	#==============
	def get_outfile_name(self, outfile: str = None):
		# Use package_name if outfile is None
		if not outfile:
			outfile = self.package_name
		if not outfile.startswith('selftest-'):
			outfile = f'selftest-{outfile}'
		# Remove outfile ends with '-questions.txt'
		outfile_root, ext = os.path.splitext(outfile)
		if outfile_root.endswith('-questions'):
			outfile = outfile_root.rstrip('-questions')
		# Ensure the extension is '.txt'
		if not outfile.endswith('.html'):
			outfile += '.html'
		return outfile

	#==============
	def save_package(self, outfile: str = None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		outfile = self.get_outfile_name(outfile)
		# Write assessment items to the file
		with open(outfile, "w") as f:
			count = 0
			# only one problem per file, only write one
			assessment_item_dict = random.choice(self.assessment_items_tree)
			formatted_html_text = assessment_item_dict['assessment_item_data']
			f.write(formatted_html_text)
			count += 1
		print(f"Saved {count} assessment items to {outfile}")
