#!/usr/bin/env python3

import os
import re
import sys
import random
import argparse

# Set sys.path to the directory containing the 'qti_package_maker' folder
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
sys.path.insert(0, project_root)

from qti_package_maker.package_maker import MasterQTIPackage

#=====================================================
def read_MC(parts):
	question_text = parts[1].strip()
	choices_list = parts[2::2]
	correct_status = [element.lower() for element in parts[3::2]]
	answer_index = correct_status.index('correct')
	answer_text = choices_list[answer_index]
	return question_text, choices_list, answer_text

#=====================================================
def indices(lst, element):
	result = []
	offset = -1
	while True:
		try:
			offset = lst.index(element, offset+1)
		except ValueError:
			return result
		result.append(offset)

#=====================================================
def read_MA(parts):
	question_text = parts[1].strip()
	choices_list = parts[2::2]
	correct_status = [element.lower() for element in parts[3::2]]
	answers_indices = indices(correct_status, 'correct')
	answers_list = [choices_list[i] for i in answers_indices]
	return question_text, choices_list, answers_list

#=====================================================
def read_MATCH(parts):
	question_text = parts[1].strip()
	#MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text
	#BBQ: When uploading a matching question, you must have a one-to-one relationship between questions and answers. If not, correct answers may be marked incorrect if more than one answer has the same value.
	prompts_list = parts[2::2]
	choices_list = parts[3::2]
	return question_text, prompts_list, choices_list

#=====================================================
#=====================================================
def process_file(input_file: str, allow_mixed: bool) -> list:
	"""
	Read and process Blackboard questions (BBQ) from the input file.
	"""
	print(f"Reading Blackboard questions (BBQ) from file: {input_file}")

	first_question_type = None  # Stores the first detected question type for consistency checks

	# Mapping BBQ question types to standardized names
	question_mapping = {
		"MC": "MC",        # Multiple Choice
		"MA": "MA",        # Multiple Answer
		"MAT": "MATCH",    # Matching
		"FIB": "FIB",      # Fill in the Blank
		"FIB_PLUS": "MULTI_FIB",  # Multi-part Fill in the Blank
		"NUM": "NUM",      # Numeric Response
		"ORD": "ORDER",    # Ordered List Question
	}

	question_items = []  # Stores processed question data

	# Step 1: Read and process questions from the input file
	with open(input_file, 'r') as f:
		for line in f:
			sline = line.strip()  # Remove leading/trailing whitespace

			if not sline:
				# Skip blank lines to avoid processing empty lines
				continue

			# Split the line into parts using tab delimiters
			parts = sline.split('\t')

			# Extract the question type from the first column
			bbq_question_type = parts[0].strip()

			# Lookup the standardized question type
			question_type = question_mapping.get(bbq_question_type)

			# Handle unknown or unsupported question types
			if question_type is None:
				print(f"Warning: Unknown question type '{bbq_question_type}', skipping.")
				continue

			# Step 2: Enforce consistent question type unless allow_mixed is True
			if first_question_type is None:
				# Store the first encountered question type
				first_question_type = question_type
			elif question_type != first_question_type and not allow_mixed:
				# Stop execution if mixed question types are found but not allowed
				print(f"Error: Mixed question types found! First: {first_question_type}, Found: {question_type}")
				print("Use --allow-mixed to permit different question types.")
				sys.exit(1)

			# Store the processed question type and its associated parts
			question_items.append((question_type, parts))

	return question_items

#=====================================================
def limit_questions(question_items: list, question_limit: int) -> list:
	"""
	Limit the number of questions processed, if a limit is set.
	"""

	# Step 3: Apply question limit if specified
	if question_limit and len(question_items) > question_limit:
		# Randomly shuffle questions to ensure variety in selection
		random.shuffle(question_items)

		# Limit the number of questions processed
		question_items = question_items[:question_limit]

	return question_items

#=====================================================
def process_questions(question_items: list, engine_list: list):
	"""
	Process each question by dynamically retrieving the appropriate parser function
	and passing the parsed question data to the provided engines.
	"""

	# Step 4: Process each question using the appropriate parser function
	for question_type, parts in question_items:
		# Dynamically construct the function name to parse the question
		function_name = f"read_{question_type}"

		# Retrieve the corresponding function from the global namespace
		question_parser = globals().get(function_name)

		# Ensure the function exists before calling it
		if question_parser is None:
			print(f"Error: No parser function '{function_name}' found.")
			sys.exit(1)

		# Step 5: Parse the question using the retrieved function
		question_tuple = question_parser(parts)

		# Step 6: Distribute the parsed question data to all engines
		for engine in engine_list:
			engine.add_question(question_type, question_tuple)

	return

#=====================================================
def parse_args(format_shortcuts) -> argparse.Namespace:
	"""
	Parses command-line arguments.

	Returns:
		argparse.Namespace: Parsed command-line arguments.
	"""
	parser = argparse.ArgumentParser(description="Convert BBQ file to other formats.")
	parser.add_argument("-i", "--input", "--input_file", required=True,
			dest="input_file", help="Path to the input BBQ text file.")

	parser.add_argument("-o", "--output", "--output_file", required=False,
			dest="output_file", help="Path to the output file, only works with one output engine.")

	parser.add_argument("-n", "--limit", "--question_limit", type=int,
			dest="question_limit", help="Limit the number of input items.")

	# Boolean flag for allowing mixed question types
	parser.add_argument("--allow-mixed", dest="allow_mixed", help="Allow mixed question types",
			action="store_true", default=False)

	#============== Output Formats ==============

	# Generate the list of all formats from format_shortcuts
	# Extracts only format names
	all_formats = list(format_shortcuts.keys())

	# Allow multiple formats using --format with an explicit list
	parser.add_argument("-f", "--format", dest="output_format", type=str, action="append",
			choices=all_formats, help="Set output format (multiple allowed)")

	# Shortcut for selecting ALL formats
	parser.add_argument("-a", "--all", dest="all_formats", help="Enable all output formats",
			action="store_true")

	# Register format shortcut options
	for engine_name, (short_opt, short_name, desc_text) in format_shortcuts.items():
		parser.add_argument(short_opt, f"--{short_name}", f"--{engine_name}", dest="output_format",
				action="append", const=engine_name, nargs='?', help=desc_text)

	args = parser.parse_args()

	# If --all is set, override other selections and set all formats
	if args.all_formats:
		args.output_format = all_formats
	elif args.output_format:
		# Remove duplicates
		args.output_format = list(set(args.output_format))
	else:
		parser.error("At least one output format must be specified. Use -f, -a, or a shortcut.")

	if args.output_file and len(args.output_format) > 1:
		parser.error("Output file, only works with one output engine.")

	return args

def extract_core_name(bbq_file_name):
	# Regular expression to match the core part
	if '/' in bbq_file_name:
		bbq_file_basename = os.path.basename(bbq_file_name)
	else:
		bbq_file_basename = bbq_file_name
	match = re.search(r'^bbq-(.+?)-questions\.txt$', bbq_file_basename)
	if not match:
		raise ValueError
	bbq_core_name = match.group(1)
	return bbq_core_name

#=====================================================
#=====================================================
def main():
	"""
	Main function to handle the script execution logic.
	"""
	# Shortcuts for common formats (used for both -f and individual options)
	format_shortcuts = {
		'canvas_qti_v1_2':     ('-1', 'qti12', "Set output format to Canvas QTI v1.2"),
		'blackboard_qti_v2_1': ('-2', 'qti21', "Set output format to Blackboard QTI v2.1"),
		'human_readable':      ('-r', 'human', "Set output format to human-readable text"),
		'bbq_text_upload':     ('-b', 'bbq',   "Set output format to (B)lack(B)oard (Q)uestions"),
		'html_selftest':       ('-s', 'selftest',  "Set output format to HTML self-test"),
	}

	args = parse_args(format_shortcuts)
	# documentation website:
	# https://help.blackboard.com/Learn/Instructor/Original/Tests_Pools_Surveys/Orig_Reuse_Questions/Upload_Questions

	# general format of input_file = "bbq-(content_name)-questions.txt"
	content_name = extract_core_name(args.input_file)
	if not content_name:
		print("Invalid input filename format")
		raise ValueError
	print(f"Content Name: {content_name}")

	engine_list = []
	for output_format in args.output_format:
		short_name = format_shortcuts[output_format][1]
		#package_name = f"{short_name}-{content_name}"
		package_name = f"{content_name}"
		qti_packer = MasterQTIPackage(package_name, output_format)
		engine_list.append(qti_packer)

	# Step 1: Read questions from the input file
	question_items = process_file(args.input_file, args.allow_mixed)

	# Step 2: Apply question limit if specified
	question_items = limit_questions(question_items, args.question_limit)

	# Step 3: Process and distribute questions to the engines
	process_questions(question_items, engine_list)

	for engine in engine_list:
		engine.save_package(args.output_file)

#==============

if __name__ == "__main__":
	main()
