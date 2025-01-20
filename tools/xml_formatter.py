#!/usr/bin/env python3

from bs4 import BeautifulSoup
import argparse
import os
import sys

#==============

def format_xml_with_bs(input_file: str) -> str:
	"""
	Formats an XML file using BeautifulSoup's prettify() method.

	Args:
		input_file (str): Path to the XML file to be formatted.

	Returns:
		str: The formatted XML as a string.
	"""
	try:
		# Read the XML file
		with open(input_file, "r") as file:
			xml_content = file.read()

		# Parse and prettify the XML
		bs = BeautifulSoup(xml_content, "xml")
		return bs.prettify()
	except Exception as e:
		print(f"Error formatting XML file: {e}")
		sys.exit(1)

#==============

def save_formatted_xml(formatted_xml: str, output_file: str) -> None:
	"""
	Saves the formatted XML to the specified output file.

	Args:
		formatted_xml (str): The formatted XML content.
		output_file (str): Path to save the formatted XML file.

	Returns:
		None
	"""
	try:
		with open(output_file, "w") as file:
			file.write(formatted_xml)
		print(f"Formatted XML written to {output_file}")
	except Exception as e:
		print(f"Error writing to file: {e}")
		sys.exit(1)

#==============

def parse_args() -> argparse.Namespace:
	"""
	Parses command-line arguments.

	Returns:
		argparse.Namespace: Parsed command-line arguments.
	"""
	parser = argparse.ArgumentParser(description="Format an XML file with BeautifulSoup prettify().")
	parser.add_argument("-i", "--input", required=True, help="Path to the input unformatted XML file.")
	parser.add_argument("--inplace", action="store_true", help="Edit the input file in place.")
	parser.add_argument("-o", "--output", help="Path to save the formatted XML file (if not using --inplace).")
	return parser.parse_args()

#==============

def main():
	"""
	Main function to handle the script execution logic.
	"""
	args = parse_args()

	# Format the input XML file
	formatted_xml = format_xml_with_bs(args.input)

	# Handle inplace editing
	if args.inplace:
		backup_file = args.input + ".bak"
		try:
			# Create a backup file before overwriting
			os.rename(args.input, backup_file)
			save_formatted_xml(formatted_xml, args.input)
			print(f"In-place formatting completed. Backup saved as {backup_file}")
		except Exception as e:
			print(f"Failed to perform in-place formatting: {e}")
			sys.exit(1)
	else:
		# Save to output file
		if not args.output:
			print("Error: --output is required if --inplace is not used.")
			sys.exit(1)
		save_formatted_xml(formatted_xml, args.output)

#==============

if __name__ == "__main__":
	main()
