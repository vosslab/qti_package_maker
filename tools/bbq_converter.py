#!/usr/bin/env python3

import os
import sys
import argparse

from qti_package_maker.package_maker import MasterQTIPackage

#=====================================================
def read_MC(parts):
	question_text = parts[1].strip()
	choices_list = parts[2::2]
	correct_status = lower_parts[3::2]
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
	correct_status = lower_parts[3::2]
	answers_indices = indices(correct_status, 'correct')
	answers_list = choices_list[answers_indices]
	return question_text, choices_list, answer_text

#=====================================================
def read_MATCH(parts):
	question_text = parts[1].strip()
	#MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text
	#BBQ: When uploading a matching question, you must have a one-to-one relationship between questions and answers. If not, correct answers may be marked incorrect if more than one answer has the same value.
	prompts_list = parts[2::2]
	choices_list = parts[3::2]
	return question_text, prompts_list, choices_list

#=====================================================
def parse_args() -> argparse.Namespace:
	"""
	Parses command-line arguments.

	Returns:
		argparse.Namespace: Parsed command-line arguments.
	"""
	parser = argparse.ArgumentParser(description="Convert BBQ file to other formats.")
	parser.add_argument("-i", "--input", "--input_file", required=True,
			dest="input_file", help="Path to the input unformatted XML file.")
	# Boolean flag for allowing mixed question types
	parser.add_argument("--allow-mixed", dest="allow_mixed", help="Allow mixed question types",
			action="store_true", default=False)

	#============== Output Formats ==============

	# Shortcuts for common formats (used for both -f and individual options)
	format_shortcuts = [
		('-1', '--qtiv1', 'canvas_qti_v1_2',     "Set output format to Canvas QTI v1.2"),
		('-2', '--qtiv2', 'blackboard_qti_v2_1', "Set output format to Blackboard QTI v2.1"),
		('-r', '--human', 'human_readable',      "Set output format to human-readable text"),
		('-b', '--bbq',   'bbq_text_upload',     "Set output format to (B)lack(B)oard (Q)uestions"),
		('-h', '--html',  'html_selftest',       "Set output format to HTML self-test"),
	]

	# Generate the list of all formats from format_shortcuts
	# Extracts only format names
	all_formats = [fmt[2] for fmt in format_shortcuts]

	# Allow multiple formats using --format with an explicit list
	parser.add_argument("-f", "--format", dest="output_format", type=str, action="append",
			choices=all_formats, help="Set output format (multiple allowed)")

	# Shortcut for selecting ALL formats
	parser.add_argument("-a", "--all", dest="all_formats", help="Enable all output formats",
			action="store_true")

	# Register format shortcut options
	for short_opt, long_opt, value_text, desc_text in format_shortcuts:
		parser.add_argument(short_opt, long_opt, dest="output_format", action="append",
				const=value_text, help=desc_text)

	args = parser.parse_args()

	# If --all is set, override other selections and set all formats
	if args.all_formats:
		args.output_format = all_formats
	elif args.output_format:
		# Remove duplicates
		args.output_format = list(set(args.output_format))
	else:
		parser.error("At least one output format must be specified. Use -f, -a, or a shortcut.")

	return args

#=====================================================
def process_questions(input_file: str, engine_list: list, allow_mixed: bool):
	print(f"Reading Blackboard questions (BBQ) from file: {input_file}")

	first_question_type = None  # Stores the first detected question type

	# Mapping BBQ question types to standardized names
	question_mapping = {
		"MC": "MC",
		"MA": "MA",
		"MAT": "MATCH",
		"FIB": "FIB",
		"FIB_PLUS": "MULTI_FIB",
		"NUM": "NUM",
		"ORD": "ORDER",
	}

	with open(input_file, 'r') as f:
		for line in f:
			sline = line.strip()
			if not sline:
				# handle blank lines
				continue

			parts = sline.split('\t')
			# Lookup the standardized question type
			bbq_question_type = parts[0].strip()
			question_type = question_mapping.get(bbq_question_type)
			# Handle unknown question types
			if question_type is None:
				print(f"Warning: Unknown question type '{bbq_question_type}', skipping.")
				continue

			# Enforce consistent question type (fail fast)
			if first_question_type is None:
				first_question_type = question_type
			elif question_type != first_question_type and not allow_mixed:
				print(f"Error: Mixed question types found! First: {first_question_type}, Found: {question_type}")
				print("Use --allow-mixed to permit different question types.")
				sys.exit(1)

			# Dynamically get the function name
			function_name = f"read_{question_type}"
			question_parser = globals().get(function_name)

			if question_parser is None:
				print(f"Error: No parser function '{function_name}' found.")
				sys.exit(1)

			# Read the question using the dynamically retrieved function
			question_tuple = question_parser(parts)

			# Pass the question data to each engine
			for engine in engine_list:
				engine.add_question(question_type, question_tuple)

#=====================================================
#=====================================================
def main():
	"""
	Main function to handle the script execution logic.
	"""
	args = parse_args()
	# documentation website:
	# https://help.blackboard.com/Learn/Instructor/Original/Tests_Pools_Surveys/Orig_Reuse_Questions/Upload_Questions

	# general format of input_file = "bbq-(content_name)-questions.txt"
	content_name = ""

	package_name = 'dummy'
	engine_list = []
	for output_format in args.output_format:
		qti_packer = MasterQTIPackage(content_name, output_format)
		engine_list.append(qti_packer)

	input_file = args.input_file
	process_questions(args.input_file, engine_list, args.allow_mixed)


#==============

if __name__ == "__main__":
	main()
