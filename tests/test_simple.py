#!/usr/bin/env python3

import os
import sys

# Set sys.path to the directory containing the 'qti_package_maker' folder
import sys, subprocess
git_root = subprocess.run(
	["git", "rev-parse", "--show-toplevel"], text=True, capture_output=True
).stdout.strip() or ".."
sys.path.insert(0, git_root)

# Now you can import your modules
from qti_package_maker.package_maker import MasterQTIPackage

# List of all available engines
ENGINE_NAMES = [
	'canvas_qti_v1_2',
	'blackboard_qti_v2_1',
	'human_readable',
	'bbq_text_upload',
	'html_selftest',
]

def main():
	for engine_name in ENGINE_NAMES:
		print("="*60)
		print(engine_name)
		print("="*60)
		package_name = f"dummy_{engine_name}"

		# test loading the class
		qti_packer = MasterQTIPackage(package_name, engine_name)

		# test a simple function
		qti_packer.show_available_question_types()

		# test a MC question
		question_text = 'What is your favorite color?'
		answer_text = 'blue'
		choices_list = ['blue', 'red', 'yellow']
		qti_packer.add_MC(question_text, choices_list, answer_text)

		# test a MA question
		question_text = 'Which are types of fruit?'
		answers_list = ['orange', 'banana', 'apple']
		choices_list = ['orange', 'banana', 'apple', 'lettuce', 'spinach']
		qti_packer.add_MA(question_text, choices_list, answers_list)

		# test a MATCH question
		question_text = 'Match item to color.'
		answers_list = ['orange', 'banana', 'lettuce',]
		matching_list = ['orange', 'yellow', 'green',]
		qti_packer.add_MATCH(question_text, answers_list, matching_list)

		# test save question
		output_file = package_name + ".dummy"
		qti_packer.save_package(output_file)
		os.remove(output_file)

		del qti_packer

if __name__ == '__main__':
    main()
