#!/usr/bin/env python3

import os
import sys

# Set sys.path to the directory containing the 'qti_package_maker' folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

#print(sys.path)
print("\n")

# Now you can import your modules
from qti_package_maker.package_maker import MasterQTIPackage

def main():
	qti_packer = MasterQTIPackage('dummy_canvas_qti_v1', 'QTI_v1')
	#qti_packer = MasterQTIPackage('pool_human_readable', 'HumanRead')
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
	prompts_list = ['orange', 'banana', 'lettuce',]
	choices_list = ['orange', 'yellow', 'green', 'distractor']
	qti_packer.add_MATCH(question_text, prompts_list, choices_list)

	qti_packer.save_package()

if __name__ == '__main__':
    main()
