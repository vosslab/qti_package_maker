#!/usr/bin/env python

import inspect
import pathlib
import pkgutil
import tabulate
import importlib

# Dictionary to store engine information dynamically
ENGINE_REGISTRY = {}

# Get the directory where this script is located
ENGINES_DIR = pathlib.Path(__file__).parent

#============================================
def is_method_implemented(engine_class, method_name: str) -> bool:
	"""
	Checks if the given method exists and is actually implemented in the engine.
	"""
	# Get the method from the class
	method = getattr(engine_class, method_name, None)
	# If the method does not exist or is not callable, return False
	if not callable(method):
		return False
	# Get method source code to check if it only raises NotImplementedError
	source = inspect.getsource(method)
	if "raise NotImplementedError" in source:
		# The method is not implemented
		return False
	return True

#============================================
def process_engine(module_name, ispkg):
	# Import the engine_class module dynamically
	module_path = f"qti_package_maker.engines.{module_name}.engine_class"

	# Import the module
	module = importlib.import_module(module_path)
	#importlib.reload(module)

	# Debugging output
	#print(f"Module '{module_name}' contents:", dir(module))

	# Explicitly fetch EngineClass using getattr()
	engine_class = getattr(module, "EngineClass", None)
	#print(f"EngineClass for '{module_name}':", engine_class)

	if not engine_class:
		print(f"Warning: {module_name}.engine_class.py does not define EngineClass.")
		return None

	# Determine read/write capabilities dynamically
	can_read = is_method_implemented(engine_class, "read_items_from_file")
	can_write = is_method_implemented(engine_class, "save_package")

	# Register engine using folder name as engine_name
	ENGINE_REGISTRY[module_name] = {
		"engine_name": module_name,
		"can_read": can_read,
		"can_write": can_write,
		"engine_class": engine_class
	}

#============================================
def register_engines():
	"""
	Dynamically scans the 'engines' directory for engine_class.py files
	and registers available engines by importing their classes.
	"""
	global ENGINE_REGISTRY
	for _, module_name, ispkg in pkgutil.iter_modules([str(ENGINES_DIR)]):
		if module_name.startswith("template"):
			continue
		engine_path = ENGINES_DIR / module_name / "engine_class.py"
		if not ispkg or not engine_path.exists():
			# Skip non-packages or missing engine_class.py
			continue
		engine_dict = process_engine(module_name, ispkg)
		if engine_dict is not None:
			ENGINE_REGISTRY[module_name] = engine_dict

#============================================
def print_engine_table(tablefmt: str="fancy_outline"):
	if ENGINE_REGISTRY:
		engine_data = []
		for info in ENGINE_REGISTRY.values():
			# Convert True/False to colored + or X
			can_read = PLUS if info["can_read"] else CROSS
			can_write = PLUS if info["can_write"] else CROSS
			engine_data.append([info["engine_name"], can_read, can_write])
		print("\nRegistered Engines:")
		headers = ["Engine Name", "Can Read", "Can Write"]
		print(tabulate.tabulate(engine_data, headers, tablefmt=tablefmt))
	else:
		print("No engines found.")

#============================================
# Run the registration when imported
try:
	register_engines()
except ModuleNotFoundError:
	pass

# Define ANSI color codes for green (pass) and red (fail)
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"    # Reset color
PLUS = f"{GREEN}+{RESET}" # Green +
CROSS = f"{RED}X{RESET}" # Red X

#============================================
# If this script is run directly, print the available engines
#============================================
def main():
	register_engines()
	print_engine_table()

if __name__ == "__main__":
	main()
