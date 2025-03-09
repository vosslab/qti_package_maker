
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
from qti_package_maker.engines.canvas_qti_v1_2 import write_item
from qti_package_maker.engines.canvas_qti_v1_2 import assessment_meta
from qti_package_maker.engines.canvas_qti_v1_2 import item_xml_helpers

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
		self.output_dir = os.path.join(os.getcwd(), f"QTI12-{self.package_name}_package_{current_time}")
		#print(f"OUTPUT directory: {self.output_dir}")
		# Create necessary directories
		self.assessment_base_name = "canvas_qti12_questions"
		self.assessment_dir = os.path.join(self.output_dir, self.assessment_base_name)
		self.assessment_items_file_name = self.assessment_base_name + ".xml"
		self.assessment_items_base_path = os.path.join(self.assessment_base_name, self.assessment_items_file_name)
		self.assessment_items_file_path = os.path.join(self.output_dir, self.assessment_items_base_path)
		self.assessment_meta_file_path = os.path.join(self.assessment_dir, 'assessment_meta.xml')
		self.manifest_file_path = os.path.join(self.output_dir, "imsmanifest.xml")

	#==============
	def read_package(self, infile: str):
		raise NotImplementedError

	#==============
	def write_assessment_items(self, item_bank):
		if len(item_bank) == 0:
			print("No items to write out skipping")
			return

		""" Write all assessment items into a structured Canvas QTI 1.2 XML file."""
		# Step 1: Create <section> to hold assessment items
		section_level_etree = lxml.etree.Element("section", ident="root_section")

		# Step 2: Append each <item> (assessment item) to <section>
		self.save_count = 0
		assessment_items_tree = self.process_item_bank(item_bank)
		for assessment_item_etree in assessment_items_tree:
			self.save_count += 1
			section_level_etree.append(assessment_item_etree)

		# Step 3: Create <assessment> and append <section>
		assessment_level_etree = lxml.etree.Element("assessment", ident="root_assessment", title=self.package_name)
		assessment_level_etree.append(section_level_etree)

		# Step 4: Create XML root <questestinterop> and append <assessment>
		assessment_items_file_xml_root = item_xml_helpers.create_assessment_items_file_xml_header()
		assessment_items_file_xml_root.append(assessment_level_etree)

		# Step 5: Save final XML to file
		assessment_items_xml_string = lxml.etree.tostring(
			assessment_items_file_xml_root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
		)

		with open(self.assessment_items_file_path, "w", encoding="utf-8") as f:
			f.write(assessment_items_xml_string.decode("utf-8"))

		# Step 6: Log & return filename
		if self.verbose is True:
			print(f"Wrote {self.save_count} assessment items to {self.assessment_items_base_path}")
		return

	#==============
	def write_assessment_meta(self):
		# Generate imsmanifest.xml
		assessment_meta_etree = assessment_meta.generate_assessment_meta(self.package_name)
		assessment_meta_xml_string = lxml.etree.tostring(assessment_meta_etree,
			pretty_print=True, xml_declaration=True, encoding="UTF-8")
		with open(self.assessment_meta_file_path, "w", encoding="utf-8") as f:
			f.write(assessment_meta_xml_string.decode("utf-8"))
		return

	#==============
	def write_manifest(self):
		# Generate imsmanifest.xml
		file_list = [self.assessment_items_base_path, ]
		manifest_etree = qti_manifest.generate_manifest(self.package_name, file_list, version="1.2")
		manifest_xml_string = lxml.etree.tostring(manifest_etree, pretty_print=True,
			xml_declaration=True, encoding="UTF-8")
		with open(self.manifest_file_path, "w", encoding="utf-8") as f:
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
		self.write_manifest()
		self.write_assessment_meta()
		self.write_assessment_items(item_bank)

		# Write the package to a ZIP file
		#zip_path = f"{self.package_name}-qti_v1_2.zip"
		#zip_path = f"{self.package_name}.zip"
		outfile = self.get_outfile_name('qti12', 'zip', outfile)
		with zipfile.ZipFile(outfile, "w", zipfile.ZIP_DEFLATED) as zipf:
			for root, _, files in os.walk(self.output_dir):
				for file in files:
					full_path = os.path.join(root, file)
					# Path relative to the output directory
					relative_path = os.path.relpath(full_path, self.output_dir)
					zipf.write(full_path, relative_path)  # No need to add package_name prefix
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
