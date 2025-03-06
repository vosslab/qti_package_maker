#!/usr/bin/env python

import importlib
import pkgutil
from pathlib import Path

# Dictionary to store engine information dynamically
ENGINE_REGISTRY = {}

# Get the directory where this script is located
ENGINES_DIR = Path(__file__).parent

#============================================
def is_method_implemented(engine_class, method_name: str) -> bool:
	"""
	Checks if the given method exists and does NOT raise NotImplementedError.
	Args:
		engine_class: The engine class to check.
		method_name (str): The name of the method to check.
	Returns:
		bool: True if the method is implemented, False if it raises NotImplementedError.
	"""
	method = getattr(engine_class, method_name, None)
	if not callable(method):
		return False
	try:
		method()  # Test call (may require dummy arguments in some cases)
	except NotImplementedError:
		return False
	except TypeError:
		# Raised if the method requires arguments, meaning it's likely implemented
		return True
	except Exception as e:
		print(f"Warning: Unexpected error when checking {method_name} in {engine_class}: {e}")
		return False
	return True

def process_engine(module_name, ispkg):
	# Import the engine_class module dynamically
	module = importlib.import_module(
		f"qti_package_maker.engines.{module_name}.engine_class"
	)

	# Debugging output
	print(f"Module '{module_name}' contents:", dir(module))

	# Explicitly fetch EngineClass using getattr()
	engine_class = getattr(module, "EngineClass", None)
	print(f"EngineClass for '{module_name}':", engine_class)

	if not engine_class:
		print(f"Warning: {module_name}.engine_class.py does not define EngineClass.")
		return None

	# Determine read/write capabilities dynamically
	can_read = is_method_implemented(engine_class, "read_package")
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
# Run the registration when imported
register_engines()

#============================================
# If this script is run directly, print the available engines
#============================================
def main():
	"""
	If executed as a script, prints out available engines for testing.
	"""
	if ENGINE_REGISTRY:
		print("\nRegistered Engines:")
		for key, engine_info in ENGINE_REGISTRY.items():
			print(
				f"- {engine_info['engine_name']} "
				f"(Read: {engine_info['can_read']}, Write: {engine_info['can_write']})"
			)
	else:
		print("No engines found.")

if __name__ == "__main__":
	main()
