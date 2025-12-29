
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.human_readable import write_item

class EngineClass(base_engine.BaseEngine):
	"""
	Human-readable HTML writer that renders items into a preformatted page.
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

	#============================
	def write_html_header(self) -> str:
		"""
		Return the HTML header for the human-readable output.
		"""
		return (
			'<!DOCTYPE html>\n'
			'<html>\n<head>\n'
			'<meta charset="UTF-8">\n'
			'<style>\n'
			'  body {\n'
			'    background: white;\n'
			'    color: black;\n'
			'  }\n'
			'  @media (prefers-color-scheme: dark) {\n'
			'    body {\n'
			'      background: #121212;\n'
			'      color: #e0e0e0;\n'
			'    }\n'
			'  }\n'
			'</style>\n'
			'</head>\n<body>\n'
			'<pre>\n'
		)

	#============================
	def write_html_footer(self) -> str:
		"""
		Return the closing HTML tags for the human-readable output.
		"""
		return '</pre>\n</body>\n</html>\n'

	#==============
	def save_package(self, item_bank, outfile: str = None):
		outfile = self.get_outfile_name('human', 'html', outfile)
		assessment_items_tree = self.process_item_bank(item_bank)
		if len(assessment_items_tree) == 0:
			return None
		# Write assessment items to the file
		with open(outfile, "w") as f:
			f.write(self.write_html_header())
			count = 0
			for item_num, assessment_text in enumerate(assessment_items_tree, start=1):
				f.write(f"{item_num}. ")
				f.write(assessment_text)
				count += 1
			f.write(self.write_html_footer())
		if self.verbose is True:
			print(f"Saved {count} assessment items to {outfile}")
		return outfile
