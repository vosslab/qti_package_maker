#!/usr/bin/env python3

# Set sys.path to the directory containing the 'qti_package_maker' folder
import sys, subprocess
git_root = subprocess.run(
	["git", "rev-parse", "--show-toplevel"], text=True, capture_output=True
).stdout.strip() or ".."
sys.path.insert(0, git_root)

# Now you can import your modules
from qti_package_maker import package_interface

def main():
	qti_packer = package_interface.QTIPackageInterface('dummy')
	qti_packer.show_available_question_types()
	question_text = 'What is your favorite color?'
	answer_text = 'blue'
	choices_list = ['blue', 'red', 'yellow']
	qti_packer.add_MC(question_text, choices_list, answer_text)

	question_text = 'Which are types of fruit?'
	answers_list = ['orange', 'banana', 'apple']
	choices_list = ['orange', 'banana', 'apple', 'lettuce', 'spinach']
	qti_packer.add_MA(question_text, choices_list, answers_list)

	question_text = 'Match item to color.'
	answers_list = ['orange', 'banana', 'lettuce',]
	matching_list = ['orange', 'yellow', 'green',]
	qti_packer.add_MATCH(question_text, answers_list, matching_list)

	qti_packer.save_package('human')

if __name__ == '__main__':
    main()
