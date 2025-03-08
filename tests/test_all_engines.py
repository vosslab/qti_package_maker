#!/usr/bin/env python3

import os
import sys
from collections import defaultdict

import tabulate

# Set sys.path to the directory containing the 'qti_package_maker' folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

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

def main():
	# Create an instance of the QTI packager
	qti_packer = package_interface.QTIPackageInterface("dummy", verbose=True)

	# Get available engines
	qti_packer.show_available_engines()
	engine_name_list = qti_packer.get_available_engines()

	# Get available item types
	available_item_types = qti_packer.get_available_item_types()
	print(f"✅ Available question types: {', '.join(available_item_types)}")

	# Initialize results dictionary
	#final_results = {engine: {item: "-" for item in available_item_types} for engine in engine_name_list}
	# Initialize results dictionary with "-" as the default value
	final_results = defaultdict(lambda: defaultdict(lambda: "-"))

	# Test each engine with all available item types
	for engine_name in engine_name_list:
		for item_type in available_item_types:
			print(f"Adding {item_type} to engine {engine_name}...")

			# Add item to the packager
			item_tuple = ITEM_TYPE_EXAMPLES[item_type]
			qti_packer.add_item(item_type, item_tuple)

			# Attempt to save the package
			try:
				output_file = qti_packer.save_package(engine_name)
				# Validate file creation and update results
				if os.path.exists(output_file):
					final_results[engine_name][item_type] = "Y"
					os.remove(output_file)  # Cleanup
				else:
					final_results[engine_name][item_type] = "?"
			except NotImplementedError:
				final_results[engine_name][item_type] = "N"
			# Reset the item bank for the next test
			qti_packer.reset_item_bank()

	# Convert dictionary results into a wide table format
	table_data = [[engine] + [final_results[engine][item] for item in available_item_types]
	              for engine in engine_name_list]

	# Print test results as a wide table
	print("\nTest Results:")
	headers = ["Engine"] + list(available_item_types)
	print(tabulate.tabulate(table_data, headers=headers, tablefmt="rounded_outline"))


if __name__ == '__main__':
	main()
