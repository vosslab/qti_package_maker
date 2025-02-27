
# Standard Library
import os

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import base_package_maker
from qti_package_maker.engines.bbq_text_upload import add_item

class BBQTextEngine(base_package_maker.BaseEngine):
	def __init__(self, package_name: str):
		super().__init__(package_name)
		# Verify that the correct add_item module is imported
		if not hasattr(add_item, "ENGINE_NAME") or add_item.ENGINE_NAME != "bbq_text_upload":
			raise ImportError("Incorrect add_item module imported for BBQTextEngine engine")
		self.add_item = add_item

	#==============
	def get_outfile_name(self, outfile: str = None):
		# Use package_name if outfile is None
		if not outfile:
			outfile = self.package_name
		# Ensure outfile starts with 'bbq-' unless it's already 'new_bbq-'
		if not outfile.startswith('bbq-') and not outfile.startswith('new_bbq-'):
			outfile = f'bbq-{outfile}'  # Removed redundant .lstrip("bbq-")
		# Ensure outfile ends with '-questions.txt'
		outfile_root, ext = os.path.splitext(outfile)
		if not outfile_root.endswith('-questions'):
			outfile = f"{outfile_root}-questions.txt"
		# Ensure the extension is '.txt'
		if not outfile.endswith('.txt'):
			outfile += '.txt'
		# If the file exists and doesn't start with 'new_', prepend 'new_'
		if os.path.exists(outfile) and not outfile.startswith('new_'):
			outfile = f"new_{outfile}"
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
			for assessment_item_dict in self.assessment_items_tree:
					formatted_bbq_text = assessment_item_dict['assessment_item_data']
					# no inner newlines allowed
					formatted_bbq_text = formatted_bbq_text.replace('\n', ' ').strip()
					# Ensure each item is on a new line
					f.write(formatted_bbq_text + "\n")
					count += 1
		print(f"Saved {count} assessment items to {outfile}")
