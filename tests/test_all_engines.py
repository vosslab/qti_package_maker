#!/usr/bin/env python3

import os
import sys

# Set sys.path to the directory containing the 'qti_package_maker' folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from qti_package_maker import package_interface


# List of all question types with sample data
QUESTION_TYPES = {
	"MC": ("What is your favorite color?", ["blue", "red", "yellow"], "blue"),
	"MA": ("Which are types of fruit?", ["orange", "banana", "apple", "lettuce", "spinach"], ["orange", "banana", "apple"]),
	"MATCH": ("Match item to color.", ["orange", "banana", "lettuce"], ["orange", "yellow", "green"]),
	"NUM": ("What is 2 + 2?", 4.0, 0.1, True),
	"FIB": ("Complete the sentence: The sky is __.", ["blue"]),
	"MULTI_FIB": ("Fill in the blanks: A [1] is a [2].", {"1": ["dog"], "2": ["mammal"]}),
	"ORDER": ("Arrange the planets by size.", ["Mercury", "Mars", "Venus", "Earth"]),
}

def main():
	final_results = {}
	qti_packer = package_interface.QTIPackageInterface("dummy", verbose=True)

	# List of all available engines
	qti_packer.show_available_engines()

	for engine_name in qti_packer.get_available_engines():
		print("\n" + "="*60)
		print(f"🚀 Testing Engine: {engine_name}")
		print("="*60)

		package_name = f"dummy_{engine_name}"

		# Show available question types
		available_question_types = qti_packer.get_available_question_types()
		print(f"✅ Available question types: {', '.join(available_question_types)}")

		# Store results for this engine
		engine_results = {}

		for q_type, q_data in QUESTION_TYPES.items():
			try:
				# ✅ Run the function dynamically
				if q_type in available_question_types:
					getattr(qti_packer, f"add_{q_type}")(*q_data)
					engine_results[q_type] = "✅ Passed"
				else:
					engine_results[q_type] = "❌ Not Implemented"

			except NotImplementedError:
				engine_results[q_type] = "❌ Not Implemented"
			except Exception as e:
				engine_results[q_type] = f"❌ Error: {str(e).split('\n')[0]}"

		# Save package test
		try:
			output_file = package_name + ".dummy"
			qti_packer.save_package(output_file)
			os.remove(output_file)
			engine_results["SAVE"] = "✅ Passed"
		except Exception as e:
			engine_results["SAVE"] = f"❌ Error: {str(e)}"

		# Store engine results
		final_results[engine_name] = engine_results

		# Print per-engine summary
		print("\n📊 **Results for**", engine_name)
		for q_type, status in engine_results.items():
			print(f" - {q_type.ljust(12)} {status}")

		# Cleanup
		del qti_packer

	# ✅ Print final summary
	print("\n" + "="*60)
	print("📌 FINAL SUMMARY")
	print("="*60)
	for engine, results in final_results.items():
		print(f"\n🚀 Engine: {engine}")
		for q_type, status in results.items():
			print(f" - {q_type.ljust(12)} {status}")

if __name__ == '__main__':
	main()
