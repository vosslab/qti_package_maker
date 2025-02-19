
# Standard Library
import os
import zipfile

# Pip3 Library
import lxml

# QTI Package Maker
from qti_package_maker.common import base_package_maker
from qti_package_maker.engine_blackboard_qti_v2_1 import add_item

class QTIv2Engine(base_package_maker.BaseEngine):
	def __init__(self, package_name: str):
		super().__init__(package_name)
		self.add_item = add_item

		self.output_dir = os.path.join(os.getcwd(), f"{package_name}_package")
		# Create necessary directories
		os.makedirs(self.output_dir, exist_ok=True)
		os.makedirs(os.path.join(self.output_dir, "qti12"), exist_ok=True)

	#==============
	def add_assessment_item(self, title: str, item_type: str, item_etree):
		self.number_of_assessment_items = len(self.assessment_items)
		self.assessment_items.append(item_etree)
		return

	#==============

	def write_assessment_items(self):
		assessment_file_name_list = []
		for item_number, assessment_item_etree in enumerate(self.assessment_items, start=1):
			file_name = f"assessmentItem{item_number:05d}.xml"
			file_path = f"{self.output_dir}/qti21/{file_name}"
			with open(file_path, "w") as f:
				assessment_file_name_list.append(file_name)
				assessment_xml_string = lxml.etree.tostring(assessment_item_etree,
					pretty_print=True, xml_declaration=True, encoding="UTF-8")
				f.write(assessment_xml_string.decode("utf-8"))
		print(f"Saved {len(assessment_file_name_list)} assessment items to {self.package_name}/qti21/")
		return assessment_file_name_list

	#==============

	def write_question_bank(self, assessment_file_name_list):
		# Generate imsmanifest.xml
		question_bank_etree = question_bank.generate_question_bank(self.package_name, assessment_file_name_list)
		question_bank_xml_string = lxml.etree.tostring(question_bank_etree,
			pretty_print=True, xml_declaration=True, encoding="UTF-8")
		question_bank_path = os.path.join(self.output_dir, "qti21/question_bank00001.xml")
		with open(question_bank_path, "w", encoding="utf-8") as f:
			f.write(question_bank_xml_string.decode("utf-8"))
		return

	#==============

	def write_manifest(self, assessment_file_name_list):
		# Generate imsmanifest.xml
		manifest_etree = manifest.generate_manifest(assessment_file_name_list)
		manifest_xml_string = lxml.etree.tostring(manifest_etree, pretty_print=True,
			xml_declaration=True, encoding="UTF-8")
		manifest_path = os.path.join(self.output_dir, "imsmanifest.xml")
		with open(manifest_path, "w", encoding="utf-8") as f:
			f.write(manifest_xml_string.decode("utf-8"))
		return

	#==============

	def save_package(self):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		assessment_file_name_list = self.write_assessment_items()
		self.write_question_bank(assessment_file_name_list)
		self.write_manifest(assessment_file_name_list)

		# Write the package to a ZIP file
		zip_path = f"{self.package_name}.zip"
		with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
			for root, _, files in os.walk(self.output_dir):
				for file in files:
					full_path = os.path.join(root, file)
					relative_path = os.path.relpath(full_path, self.output_dir)  # Path relative to the output directory
					zipf.write(full_path, relative_path)  # No need to add package_name prefix
		self.clean_temp_files()

		print(f"Package saved to {zip_path}")

	#==============

	def clean_temp_files(self):
		"""
		Delete temporary files created during package generation.
		"""
		import shutil
		if os.path.exists(self.output_dir):
			shutil.rmtree(self.output_dir)
