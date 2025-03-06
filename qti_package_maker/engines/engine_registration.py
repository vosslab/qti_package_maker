import importlib
import pkgutil
from pathlib import Path

# Dictionary to store engine information dynamically
ENGINE_REGISTRY = {}

# Get the directory where this script is located
ENGINES_DIR = Path(__file__).parent

def register_engines():
	"""
	Dynamically scans the 'engines' directory for engine_class.py files
	and registers available engines by importing their classes.
	"""
	global ENGINE_REGISTRY

	for _, module_name, ispkg in pkgutil.iter_modules([str(ENGINES_DIR)]):
		engine_path = ENGINES_DIR / module_name / "engine_class.py"

		if not ispkg or not engine_path.exists():
			continue  # Skip non-packages or missing engine_class.py

		try:
			# Import the engine_class module dynamically
			module = importlib.import_module(
				f"qti_package_maker.engines.{module_name}.engine_class"
			)

			# Verify ENGINE_NAME and EngineClass exist
			if hasattr(module, "ENGINE_NAME") and hasattr(module, "EngineClass"):
				engine_class = module.EngineClass
				# Determine read/write capabilities dynamically
				can_read = hasattr(engine_class, "read_package") and \
					callable(getattr(engine_class, "read_package"))
				can_write = hasattr(engine_class, "save_package") and \
					callable(getattr(engine_class, "save_package"))

				# Register engine
				ENGINE_REGISTRY[module_name] = {
					"engine_name": module.ENGINE_NAME,
					"can_read": can_read,
					"can_write": can_write,
					"engine_class": engine_class
				}
			else:
				print(f"Warning: {module_name}.engine_class.py is missing required attributes.")

		except Exception as e:
			print(f"Error loading engine '{module_name}': {e}")

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
