#!/usr/bin/env python

import argparse

import package_maker

#===========================================================
#===========================================================
# This function handles the parsing of command-line arguments.
def parse_arguments():
	"""
	Parses command-line arguments for the script.

	Returns:
		argparse.Namespace: Parsed arguments with attributes `duplicates`,
		`num_choices`, and `question_type`.
	"""
	# Create an argument parser with a description of the script's functionality
	parser = argparse.ArgumentParser(description="Generate questions.")

	# Parse the provided command-line arguments and return them
	args = parser.parse_args()
	return args

#===========================================================
#===========================================================
# This function serves as the entry point for generating and saving questions.
def main():
	"""
	Main function that orchestrates question generation and file output.
	"""

	# Parse arguments from the command line
	#args = parse_arguments()

	qti_packer = package_maker.QTIPackage('example_pool_from_test_maker')
	qti_packer.show_available_question_types()
	question_text = 'What is your favorite color?'
	answer_text = 'blue'
	choices_list = ['blue', 'red', 'yellow']
	qti_packer.add_MC(question_text, choices_list, answer_text)

	question_text = 'Which are types of fruit?'
	answers_list = ['orange', 'banana', 'apple']
	choices_list = ['orange', 'banana', 'apple', 'lettuce', 'spinach']
	qti_packer.add_MA(question_text, choices_list, answers_list)

	qti_packer.save_package()

#===========================================================
#===========================================================
# This block ensures the script runs only when executed directly
if __name__ == '__main__':
	# Call the main function to run the program
	main()

## THE END

