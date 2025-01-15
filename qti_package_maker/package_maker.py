#!/usr/bin/env python3

# Standard Library
import os
import zipfile
import time
import random

# PIP3 modules
import xml.etree.ElementTree as ET

# local repo modules
import qti_package_maker.items
import qti_package_maker.manifest
import qti_package_maker.utils

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
		self.package_name = package_name
		self.questions = []
		self.output_dir = os.path.join(os.getcwd(), f"{package_name}_package")

		# Create necessary directories
		os.makedirs(self.output_dir, exist_ok=True)
		os.makedirs(os.path.join(self.output_dir, "qti21"), exist_ok=True)
		os.makedirs(os.path.join(self.output_dir, "csfiles/home_dir"), exist_ok=True)

	#==============

	def add_question(self, question_xml: ET.Element):
		"""
		Add a question to the QTI package.

		Args:
			question_xml (ET.Element): The question in QTI-compliant XML format.
		"""
		self.questions.append(question_xml)

	#==============

	def save_package(self):
		"""
		Generate the imsmanifest.xml and save the QTI package as a ZIP file.
		"""
		# Generate imsmanifest.xml
		manifest_xml = qti_package_maker.manifest.generate_manifest(self.questions)
		manifest_path = os.path.join(self.output_dir, "imsmanifest.xml")
		with open(manifest_path, "w", encoding="utf-8") as f:
			f.write(manifest_xml)

		# Write the package to a ZIP file
		zip_path = f"{self.package_name}.zip"
		with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
			for root, _, files in os.walk(self.output_dir):
				for file in files:
					full_path = os.path.join(root, file)
					relative_path = os.path.relpath(full_path, self.output_dir)
					zipf.write(full_path, os.path.join(self.package_name, relative_path))

		print(f"Package saved to {zip_path}")

	#==============

	def clean_temp_files(self):
		"""
		Delete temporary files created during package generation.
		"""
		import shutil
		if os.path.exists(self.output_dir):
			shutil.rmtree(self.output_dir)
