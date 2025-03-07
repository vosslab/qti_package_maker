
# Standard Library

# Pip3 Library

# QTI Package Maker
from qti_package_maker.assessment_items import item_bank
from qti_package_maker.assessment_items import item_types

"""
I think the process will be that this module is passed a file
and returns an new item bank from the input.

for QTI the input is a zip file,
but for BBQ text upload the format is a text file
"""

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
def make_item_cls_from_line(text_line: str):
	# Mapping BBQ question types to parsing functions
	question_function_map = {
		"MC": read_MC,
		"MA": read_MA,
		"MAT": read_MATCH,
		#"NUM": read_NUM,
		#"FIB": read_FIB,
		#"FIB_PLUS": read_MULTI_FIB,
		#"ORD": read_ORDER
	}

	# Split the line into parts using tab delimiters
	parts = text_line.split('\t')

	# Extract the question type from the first column
	bbq_question_header = parts[0].strip()

	# Lookup the standardized question type
	question_type = question_mapping.get(bbq_question_header)

	# Handle unknown or unsupported question types
	if question_type is None:
		print(f"Warning: Unknown question type '{bbq_question_header}', skipping.")
		return None

	# Look up the function for the given question type
	read_function = question_function_map.get(question_type)

	if read_function is None:
		print(f"Error: Unsupported question type '{question_type}' encountered.")
		return None

	# Call the function and return the created item
	item_cls = read_function(parts)

	return item_cls


#=====================================================
#=====================================================
# TODO think about maybe a better name for this important main function
def process_file(input_file: str, allow_mixed: bool) -> list:
	"""
	Read and process Blackboard questions (BBQ) from the input file.
	"""
	new_item_bank = item_bank.ItemBank()
	# Step 1: Read and process questions from the input file
	with open(input_file, 'r') as f:
		for line in f:
			# Remove leading/trailing whitespace
			sline = line.strip()
			# Skip blank lines to avoid processing empty lines
			if not sline:
				continue
			item_cls = make_item_cls_from_line(sline)

			# Store the processed question type and its associated parts
			new_item_bank.add(item_cls)

	return new_item_bank
