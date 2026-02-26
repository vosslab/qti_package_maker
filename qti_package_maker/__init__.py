try:
	from importlib.metadata import version
	__version__ = version("qti_package_maker")
except Exception:
	import importlib.resources
	__version__ = importlib.resources.files(__package__).joinpath("../VERSION").read_text().strip()
