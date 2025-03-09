
# Standard Library
import os
import time
import shutil
import zipfile

# Pip3 Library
import lxml.etree

# QTI Package Maker
from qti_package_maker.common import qti_manifest
from qti_package_maker.engines import base_engine
from qti_package_maker.engines.blackboard_qti_v2_1 import write_item
from qti_package_maker.engines.blackboard_qti_v2_1 import assessment_meta
#from qti_package_maker.engines.blackboard_qti_v2_1 import item_xml_helpers

#==============

class EngineClass(base_engine.BaseEngine):
	def __init__(self, package_name: str, verbose: bool=False):
		# Call the base engine constructor
		super().__init__(package_name, verbose)
		# set the write_item module (required)
		self.write_item = write_item
		# Verify that the correct write_item module is imported
		self.validate_write_item_module()
		# Setup Directories
		self._setup_directories()

	#==============
	def _setup_directories(self):
		current_time = time.strftime("%H%M")
		self.output_dir = os.path.join(os.getcwd(), f"QTI21-{self.package_name}_package_{current_time}")
		#print(f"OUTPUT directory: {self.output_dir}")
		#self.assessment_base_name = "blackboard_qti21_items"
		self.assessment_base_name = "qti21_items"
		self.assessment_dir = os.path.join(self.output_dir, self.assessment_base_name)
		self.assessment_meta_file_path = os.path.join(self.assessment_dir, 'assessment_meta.xml')
		self.manifest_file_path = os.path.join(self.output_dir, "imsmanifest.xml")

	#==============
	def read_package(self, infile: str):
		raise NotImplementedError

	#==============
	def write_assessment_items(self, item_bank):
		"""
		Write all assessment items into structured Blackboard QTI 2.1 XML files.

		QTI 2.1 requires each assessment item to be stored in a separate XML file,
		unlike QTI 1.2, which allowed multiple items in one file.

		Returns:
			list: A list of relative paths to the saved assessment item XML files.
		"""
		if len(item_bank) == 0:
			print("No items to write out skipping")
			return

		# Stores the list of assessment item file paths
		assessment_file_name_list = []

		self.save_count = 0
		assessment_items_tree = self.process_item_bank(item_bank)
		# Iterate through all assessment items and assign a unique filename
		for item_number, assessment_item_etree in enumerate(assessment_items_tree, start=1):
			# Generate a unique filename for each assessment item XML
			item_file_name = f"item_{item_number:05d}.xml"

			# Generate file paths: relative path (for internal use) and global path (full path)
			item_relative_path = os.path.join(self.assessment_base_name, item_file_name)
			item_global_path = os.path.join(self.assessment_dir, item_file_name)

			# Store the relative path of the item file for reference
			assessment_file_name_list.append(item_relative_path)

			if assessment_item_etree is None:
				print("No data to write out skipping")
				continue

			# The QTI 2.1 <assessmentItem> consists of four key parts:
			# - responseDeclaration: Defines expected answers
			# - outcomeDeclaration: Specifies scoring and outcome rules
			# - itemBody: Contains the actual question and options
			# - responseProcessing: Defines how the responses are evaluated

			# Step 3: Convert the modified assessment item to an XML string
			assessment_item_xml_string = lxml.etree.tostring(
				assessment_item_etree,
				pretty_print=True,
				xml_declaration=True,
				encoding="UTF-8"
			)

			# Step 4: Write the XML string to a file
			# Open the file in write mode and save the XML data
			with open(item_global_path, "w", encoding="utf-8") as f:
				f.write(assessment_item_xml_string.decode("utf-8"))
				self.save_count += 1


		# Step 5: Log the number of saved items and return the file list
		if self.verbose is True:
			print(f"Wrote {self.save_count} assessment items for {self.package_name}")
		return assessment_file_name_list

	#==============
	def write_assessment_meta(self, assessment_file_name_list):
		# Generate imsmanifest.xml
		assessment_meta_etree = assessment_meta.generate_assessment_meta(self.package_name, assessment_file_name_list)
		assessment_meta_xml_string = lxml.etree.tostring(assessment_meta_etree,
			pretty_print=True, xml_declaration=True, encoding="UTF-8")
		with open(self.assessment_meta_file_path, "w", encoding="utf-8") as f:
			f.write(assessment_meta_xml_string.decode("utf-8"))
		return

	#==============
	def write_manifest(self, assessment_file_name_list):
		# Generate imsmanifest.xml
		manifest_etree = qti_manifest.generate_manifest(self.package_name,
				assessment_file_name_list, version="2.1")
		manifest_xml_string = lxml.etree.tostring(manifest_etree, pretty_print=True,
			xml_declaration=True, encoding="UTF-8")
		manifest_path = os.path.join(self.output_dir, "imsmanifest.xml")
		with open(manifest_path, "w", encoding="utf-8") as f:
			f.write(manifest_xml_string.decode("utf-8"))
		return

	#==============
	def save_package(self, item_bank, outfile: str=None):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		# Create necessary directories
		os.makedirs(self.output_dir, exist_ok=True)
		os.makedirs(self.assessment_dir, exist_ok=True)
		assessment_file_name_list = self.write_assessment_items(item_bank)
		self.write_assessment_meta(assessment_file_name_list)
		self.write_manifest(assessment_file_name_list)

		# Write the package to a ZIP file
		#zip_path = f"{self.package_name}.zip"
		outfile = self.get_outfile_name('qti21', 'zip', outfile)
		with zipfile.ZipFile(outfile, "w", zipfile.ZIP_DEFLATED) as zipf:
			for root, _, files in os.walk(self.output_dir):
				for file in files:
					full_path = os.path.join(root, file)
					# Path relative to the output directory
					relative_path = os.path.relpath(full_path, self.output_dir)
					# No need to add package_name prefix
					zipf.write(full_path, relative_path)
		self.clean_temp_files()
		if self.verbose is True:
			print(f"Saved {self.save_count} assessment items to {outfile}")
		return outfile

	#==============

	def clean_temp_files(self):
		"""
		Delete temporary files created during package generation.
		"""
		if os.path.exists(self.output_dir):
			shutil.rmtree(self.output_dir)
