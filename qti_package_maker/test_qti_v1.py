#!/usr/bin/env python3

import sys
import os

# Set sys.path to the directory containing the 'qti_package_maker' folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

#print(sys.path)
print("\n")

# Now you can import your modules
from qti_package_maker.engine_qti_v1_2.engine_class import QTIv1Engine

def main():
    engine = QTIv1Engine("example_package")
    engine.show_available_question_types()

if __name__ == '__main__':
    main()
