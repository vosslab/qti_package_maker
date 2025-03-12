#!/usr/bin/env python3

# Standard Library
import os

# Pip3 Library
import tabulate

# QTI Package Maker
from qti_package_maker import package_interface

# List of all question types with sample data
ITEM_TYPE_EXAMPLES = {
	"MC": ("What is your favorite color?", ["blue", "red", "yellow"], "blue"),
	"MA": ("Which are types of fruit?", ["orange", "banana", "apple", "lettuce", "spinach"], ["orange", "banana", "apple"]),
	"MATCH": ("Match item to color.", ["orange", "banana", "lettuce"], ["orange", "yellow", "green"]),
	"NUM": ("What is 2 + 2?", 4.0, 0.1, True),
	"FIB": ("Complete the sentence: The sky is __.", ["blue"]),
	"MULTI_FIB": ("Fill in the blanks: A [1] is a [2].", {"1": ["dog"], "2": ["mammal"]}),
	"ORDER": ("Arrange the planets by size.", ["Mercury", "Mars", "Venus", "Earth"]),
}

# Define ANSI color codes
GREEN = "\033[92m"   # Green for pass
RED = "\033[91m"     # Red for fail
YELLOW = "\033[93m"  # Yellow for unknown
RESET = "\033[0m"    # Reset color

#tablefmt = "rounded_outline"
tablefmt = "github"
tablefmt = "fancy_outline"
success = "✅"
success = f"{GREEN}+{RESET}"
fail = "❌"
fail = f"{RED}X{RESET}"
caution = "⚠️"
caution = f"{YELLOW}?{RESET}"

def main():
	# Create an instance of the QTI packager
	qti_packer = package_interface.QTIPackageInterface("dummy", verbose=False)
	# Get available engines
	engine_name_list = [item.replace('_', ' ') for item in qti_packer.get_available_engines()]
	# Get available item types
	available_item_types = qti_packer.get_available_item_types()
	print(f"Available question types: {', '.join(available_item_types)}")
	# Create results list directly in final table format
	table_data = []
	# Test each question type and store results directly in table_data
	for item_type in available_item_types:
		print(f"Adding {item_type}...")
		row = [item_type]  # First column: question type
		# Add item to the packager
		item_tuple = ITEM_TYPE_EXAMPLES[item_type]
		qti_packer.add_item(item_type, item_tuple)
		for engine_name in engine_name_list:
			print(f"- Writing file using {engine_name}...")
			# Attempt to save the package
			try:
				output_file = qti_packer.save_package(engine_name)
				# Validate file creation and update row results
				if os.path.exists(output_file):
					row.append(success)  # Success
					os.remove(output_file)  # Cleanup
				else:
					row.append(caution)  # Unknown issue
			except NotImplementedError:
				row.append(fail)  # Not implemented
		# Append completed row to table data
		table_data.append(row)
		# Reset the item bank for the next test
		qti_packer.reset_item_bank()
	# Print test results with swapped columns and rows
	qti_packer.show_available_engines(tablefmt)
	print("\nWrite Test Results:")
	headers = ["Item Type"] + engine_name_list  # First row: headers
	print(tabulate.tabulate(table_data, headers=headers, tablefmt=tablefmt))

if __name__ == '__main__':
	main()
