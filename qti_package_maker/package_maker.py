#!/usr/bin/env python3

# Standard Library
import os
import zipfile

# PIP3 modules
import lxml

# local repo modules
import add_item
import manifest
import question_bank
import item_helpers

#==============

class QTIPackage:
	"""
	Class to manage the lifecycle of a QTI package, including adding questions and generating ZIP files.
	"""
	def __init__(self, package_name: str):
		"""
		Initialize a new QTI package.

		Args:
			package_name (str): The name of the QTI package.
		"""
		print("Initializing QTIPackage...")  # Debug message

		self.package_name = package_name
		self.assessment_items = []
		self.available_item_methods = []  # Initialize available methods list
		self._register_item_functions()

		self.output_dir = os.path.join(os.getcwd(), f"{package_name}_package")

		# Create necessary directories
		os.makedirs(self.output_dir, exist_ok=True)
		os.makedirs(os.path.join(self.output_dir, "qti21"), exist_ok=True)
		os.makedirs(os.path.join(self.output_dir, "csfiles/home_dir"), exist_ok=True)

	#==============
	def _register_item_functions(self):
		"""Register all functions from add_item as wrapped methods of this class with 'add_' prefix."""
		print("Registering item functions...")  # Debug message
		for attr in dir(add_item):
			func = getattr(add_item, attr)
			if callable(func) and not attr.startswith("_"):
				#print(f"Registering function: {attr}")  # Debug message

				# Wrap each function to automatically add the generated item
				wrapped_func = self._create_wrapped_item_func(func)

				# Register the wrapped function with 'add_' prefix
				method_name = f"add_{attr}"
				setattr(self, method_name, wrapped_func)

				# Add the method name to available_item_methods
				self.available_item_methods.append(method_name)

		print(f"Completed registering item functions.\nAvailable methods: {self.available_item_methods}")

	#==============
	def show_available_question_types(self):
		"""Print or return the available item functions for adding questions."""
		print("Showing available question types...")  # Debug message
		return f"Available question types: {', '.join(self.available_item_methods)}"

	#==============
	def _create_wrapped_item_func(self, item_func):
		item_type = item_func.__name__.split('_')[-1]

		def wrapped(*args, **kwargs):
			question_text = args[0] if args else ""
			crc16 = item_helpers.get_crc16_from_string(question_text)
			item_etree = item_func(*args, **kwargs)
			title = f"Question_{crc16}"
			self.add_assessment_item(item_etree, title=title, item_type=item_type)

		return wrapped

	#==============

	def add_assessment_item(self, item_etree, title="", item_type=""):
		"""
		Add a generated assessment item to the package.

		Args:
			item_etree (etree.Element): The XML element representing the assessment item.
			title (str): The title of the assessment item.
			item_type (str): The type of assessment item (e.g., "MC", "TF", "Essay").

		Returns:
			None
		"""
		item_number = len(self.assessment_items) + 1
		print(f"added assessment item number {item_number} of type {item_type}")
		self.assessment_items.append(item_etree)

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
		print(f"Saved {len(assessment_file_name_list)} assessment items to {self.output_dir}/qti21/")
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

		print(f"Package saved to {zip_path}")

	#==============

	def clean_temp_files(self):
		"""
		Delete temporary files created during package generation.
		"""
		import shutil
		if os.path.exists(self.output_dir):
			shutil.rmtree(self.output_dir)
