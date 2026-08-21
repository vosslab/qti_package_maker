"""
Read a Blackboard Original pool-export package back into an ItemBank.

This module is the inverse of the write path (the per-type `<item>` builder
modules `MC.py`/`MA.py`/`MATCH.py`/`FIB.py`/`NUM.py`/`MULTI_FIB.py` plus their
shared `common_xml.py`, wrapped by `assessment_meta.py`). It accepts either a
Blackboard pool-export ZIP
(`Pool_ExportFile_*.zip`) or an already-unzipped pool directory, locates the
`assessment/x-bb-qti-pool` resource through `imsmanifest.xml`, and parses each
`<item>` in the pool `.dat` into an internal `item_types.*` instance.

The pool dialect is the QTI-1.2-derived envelope with Blackboard extensions
that the per-type builder modules write (and that the real sample pools under
`BB_Export_ZIP/` carry). The reader keys each item on its `<bbmd_questiontype>`
ELEMENT value (not an attribute), recovers question/choice HTML by reading the
`mat_formattedtext` element text (lxml un-escapes it once, reversing the
single-escape the write path applies), and recovers correct answers from the
`resprocessing` `varequal` conditions.

Type dispatch (from the forgeability audit and the real samples):

- `Multiple Choice` -> MC when the choice `response_lid` is `rcardinality="Single"`,
  MA when it is `rcardinality="Multiple"`.
- `Multiple Answer` -> MA.
- `Fill in the Blank` -> FIB (one `response_str` + per-answer `varequal`).
- `Numeric` -> NUM (answer from `varequal`, tolerance from the vargte/varlte window).
- `Fill in the Blank Plus` -> MULTI_FIB (per-blank `respident` keys, `<and>` of `<or>`).
- `Matching` -> MATCH (prompt->choice pairing recovered via each prompt
  `response_lid` ident's `varequal` answer ident, mapped back to its position
  and the `RIGHT_MATCH_BLOCK` text).
- `True/False` -> MC (the internal model has no T/F type).

Edge cases are surfaced, never silently swallowed: a missing or empty manifest
pool entry raises; multiple pool resources are read into one combined ItemBank;
an unparseable item is skipped with a warning naming its source; an unknown
`bbmd_questiontype` is skipped with a warning naming the type and source item;
duplicate `item_crc16` collisions are handled by `ItemBank` dedup (logged there).

Image capture: a pool carries images through two independent
mechanisms, both resolved before any item is parsed so extraction does not
depend on which item types the dispatch table supports. The csfiles
mechanism embeds `<img src="@X@EmbeddedFile.requestUrlStub@X@bbcswebdav/
xid-<n>_1">` tokens directly in item HTML; each token is cross-checked
against a `res00005.dat`-shaped CSResourceLinks resource, resolved to the
binary at `csfiles/home_dir/__xid-<n>_1.<ext>`, and named from the LOM
sidecar `csfiles/home_dir/__xid-<n>_1.<ext>.xml`. The hotspot mechanism wires
a `<matapplication uri="<hash>/<file>">` element (manifest-tracked) to a file
under the pool resource's own directory (its manifest `xml:base`). Every
resolved binary is copied into one fresh, persistent extraction directory
under its recovered plain filename (collision-safe); `ItemBank.media_base_dir`
is pointed at that directory (via `set_media_base_dir(media_dir, owned=True)`,
so the bank owns and will remove it) and each parsed item's HTML is rewritten
from the `@X@...` token to the plain recovered filename, so an imported
package takes on the same shape as file-authored input and flows through the
identical derived resolver in `ItemBank.collect_assets()`.

When a pool carries images, the returned bank owns its extraction directory;
call `bank.cleanup()` once done with an image-bearing imported bank to remove
that directory. Pools with no images (the common case) return a bank with no
directory to clean up, so calling `cleanup()` unconditionally is always safe.
"""

# Standard Library
import os
import tempfile
import zipfile

# PIP3 modules
import lxml.etree

# QTI Package Maker
from qti_package_maker.assessment_items import item_bank
from qti_package_maker.engines.blackboard_export_zip import read_items
from qti_package_maker.engines.blackboard_export_zip import read_media

#============================================
# Manifest / namespace constants
#============================================
# Blackboard's content-packaging namespace; the manifest declares it as `bb:`.
BB_NAMESPACE = "http://www.blackboard.com/content-packaging/"
# The manifest resource that carries the question pool.
POOL_RESOURCE_TYPE = "assessment/x-bb-qti-pool"
# The manifest filename inside every pool package.
MANIFEST_FILENAME = "imsmanifest.xml"

#============================================
# Public entry point
#============================================
#============================================
def read_items_from_file(infile: str, allow_mixed: bool = False) -> item_bank.ItemBank:
	"""
	Read a Blackboard pool-export package (ZIP or directory) into an ItemBank.

	Args:
		infile: Path to a Blackboard pool-export ZIP or an unzipped pool directory.
		allow_mixed: When True, the returned ItemBank accepts mixed item types
			(pool exports are frequently mixed, e.g. MC + MATCH in one pool).

	Returns:
		An ItemBank holding every parsed item from every pool resource in the
		package. When the pool carries images, the bank owns its media
		extraction directory (see the module docstring); call
		`item_bank.cleanup()` once done with the returned bank.
	"""
	# A ZIP needs extracting first; a directory is read in place.
	if zipfile.is_zipfile(infile):
		new_item_bank = _read_from_zip(infile, allow_mixed)
	elif os.path.isdir(infile):
		new_item_bank = _read_from_directory(infile, allow_mixed)
	else:
		raise ValueError(
			f"Input is neither a ZIP file nor a directory: '{infile}'"
		)
	return new_item_bank

#============================================
def _read_from_zip(zip_path: str, allow_mixed: bool) -> item_bank.ItemBank:
	"""
	Extract a pool-export ZIP to a temp directory and read it.

	Args:
		zip_path: Path to the pool-export ZIP.
		allow_mixed: Passed through to the ItemBank.

	Returns:
		The parsed ItemBank.
	"""
	# Extract into a self-cleaning temp directory, then read it as a directory.
	# Any recovered media is copied out to its own persistent directory before
	# this temp directory is cleaned up (see _extract_pool_media).
	with tempfile.TemporaryDirectory() as temp_dir:
		with zipfile.ZipFile(zip_path, "r") as zip_file:
			_safe_extract_zip(zip_file, temp_dir)
		# Some exports nest the package one folder deep inside the ZIP; resolve
		# to whichever directory actually holds the manifest.
		pool_root = _find_manifest_root(temp_dir)
		new_item_bank = _read_from_directory(pool_root, allow_mixed)
	return new_item_bank

#============================================
def _safe_extract_zip(zip_file: zipfile.ZipFile, dest_dir: str) -> None:
	"""
	Extract every entry of zip_file into dest_dir, rejecting path traversal.

	Every member's resolved destination path is validated to stay within
	dest_dir BEFORE anything is written, so a malicious "../" entry name
	(zip-slip) raises instead of writing outside the extraction directory.

	Args:
		zip_file: An open ZipFile to extract.
		dest_dir: The directory every entry must resolve inside of.

	Raises:
		ValueError: a member's path would escape dest_dir.
	"""
	dest_abs = os.path.abspath(dest_dir)
	for member in zip_file.infolist():
		member_path = os.path.normpath(os.path.join(dest_abs, member.filename))
		if member_path != dest_abs and not member_path.startswith(dest_abs + os.sep):
			raise ValueError(
				f"zip entry '{member.filename}' escapes the extraction directory"
			)
	zip_file.extractall(dest_abs)

#============================================
def _find_manifest_root(start_dir: str) -> str:
	"""
	Find the directory that holds `imsmanifest.xml` within an extracted tree.

	Args:
		start_dir: The directory to search from.

	Returns:
		The directory path containing the manifest.
	"""
	# Fast path: the manifest sits directly in start_dir.
	if os.path.isfile(os.path.join(start_dir, MANIFEST_FILENAME)):
		return start_dir
	# Otherwise walk until the manifest is found (handles single-folder nesting).
	for current_dir, _subdirs, filenames in os.walk(start_dir):
		if MANIFEST_FILENAME in filenames:
			return current_dir
	raise ValueError(
		f"No {MANIFEST_FILENAME} found in extracted package under '{start_dir}'"
	)

#============================================
def _read_from_directory(pool_dir: str, allow_mixed: bool) -> item_bank.ItemBank:
	"""
	Read an unzipped pool directory into an ItemBank.

	Args:
		pool_dir: A directory containing `imsmanifest.xml` and the pool `.dat`.
		allow_mixed: Passed through to the ItemBank.

	Returns:
		The parsed ItemBank.
	"""
	manifest_path = os.path.join(pool_dir, MANIFEST_FILENAME)
	if not os.path.isfile(manifest_path):
		raise ValueError(
			f"Missing {MANIFEST_FILENAME} in pool directory '{pool_dir}'"
		)
	# Resolve every pool resource the manifest declares (usually one).
	pool_dat_names = _find_pool_dat_filenames(manifest_path)
	if not pool_dat_names:
		raise ValueError(
			f"Manifest '{manifest_path}' declares no '{POOL_RESOURCE_TYPE}' resource"
		)
	new_item_bank = item_bank.ItemBank(allow_mixed)
	# Extract every referenced image into a fresh persistent directory BEFORE
	# parsing items, so extraction covers the whole pool regardless of which
	# item types the dispatch table supports (see module docstring).
	media_dir, src_map_fn = read_media._extract_pool_media(
		pool_dir, manifest_path, pool_dat_names
	)
	if media_dir is not None:
		# This bank created media_dir (see _extract_pool_media); mark it owned
		# so cleanup() removes it once the caller is done with the bank,
		# instead of leaking one tempfile.mkdtemp() directory per read.
		new_item_bank.set_media_base_dir(media_dir, owned=True)
	# Read every pool resource into one combined bank.
	for pool_dat_name in pool_dat_names:
		pool_dat_path = os.path.join(pool_dir, pool_dat_name)
		if not os.path.isfile(pool_dat_path):
			raise ValueError(
				f"Manifest points to missing pool file '{pool_dat_name}' in '{pool_dir}'"
			)
		read_items._parse_pool_into_bank(pool_dat_path, new_item_bank, src_map_fn)
	return new_item_bank

#============================================
def _find_pool_dat_filenames(manifest_path: str) -> list[str]:
	"""
	Read the manifest and return every pool resource's `.dat` filename.

	The pool resource is identified by `type="assessment/x-bb-qti-pool"`; its
	`.dat` filename is the namespaced `bb:file` attribute, not the resource id.

	Args:
		manifest_path: Path to `imsmanifest.xml`.

	Returns:
		The pool `.dat` filenames, in manifest order.
	"""
	tree = lxml.etree.parse(manifest_path)
	root = tree.getroot()
	bb_file_attr = f"{{{BB_NAMESPACE}}}file"
	pool_dat_names = []
	# Scan every <resource>; keep those typed as the BB pool.
	for resource in root.iter("resource"):
		if resource.get("type") != POOL_RESOURCE_TYPE:
			continue
		dat_filename = resource.get(bb_file_attr)
		# A pool resource with no bb:file is malformed; surface it rather than
		# silently dropping the only pool the package carries.
		if not dat_filename:
			raise ValueError(
				f"Pool resource in '{manifest_path}' has no bb:file attribute"
			)
		pool_dat_names.append(dat_filename)
	return pool_dat_names

#============================================
# Image capture
#============================================
#============================================
