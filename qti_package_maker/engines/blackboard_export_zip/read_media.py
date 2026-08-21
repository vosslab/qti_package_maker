"""Recover Blackboard export images before item XML parsing begins."""

# Standard Library
import collections.abc
import os
import re
import shutil
import tempfile

# PIP3 modules
import lxml.etree

# QTI Package Maker
from qti_package_maker.engines.blackboard_export_zip import common_xml

# Blackboard's content-packaging namespace; the manifest declares it as `bb:`.
BB_NAMESPACE = "http://www.blackboard.com/content-packaging/"
# The W3C XML namespace that carries the `xml:base` attribute on a resource.
XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
# The manifest resource that carries the csfiles xid -> item CSResourceLinks.
CSRESOURCELINKS_RESOURCE_TYPE = "course/x-bb-csresourcelinks"
# Matches a whole csfiles token (the part after common_xml.CSFILES_SRC_PREFIX)
# anywhere in raw pool text, capturing just the "xid-<n>_1" identifier.
CSFILES_TOKEN_PATTERN = re.compile(
	re.escape(common_xml.CSFILES_SRC_PREFIX) + r"(xid-\d+_\d+)")
# csfiles binaries and their LOM sidecars live under this subdirectory of the
# pool package root.
CSFILES_HOME_SUBDIR = os.path.join("csfiles", "home_dir")
# The LOM namespace on the `.jpg.xml` sidecar's <identifier> element.
LOM_NAMESPACE = "http://www.imsglobal.org/xsd/imsmd_rootv1p2p1"

#============================================
def _extract_pool_media(
	pool_dir: str,
	manifest_path: str,
	pool_dat_names: list[str],
) -> tuple[str | None, collections.abc.Callable[[str], str]]:
	"""
	Extract every csfiles and hotspot image referenced by the pool(s).

	Scans the raw pool text for csfiles tokens and the parsed pool tree for
	`<matapplication>` elements, independent of whether the enclosing item's
	`bbmd_questiontype` is dispatchable, so extraction covers the whole
	package. When at least one image is found, every resolved binary is
	copied into one fresh persistent directory under a collision-safe
	recovered filename.

	Args:
		pool_dir: The pool package root (contains imsmanifest.xml).
		manifest_path: Path to imsmanifest.xml.
		pool_dat_names: The pool `.dat` filenames declared by the manifest.

	Returns:
		A tuple of (media_dir, src_map_fn). media_dir is None and src_map_fn
		is the identity function when the pool carries no images at all
		(existing no-image behavior stays untouched).
	"""
	# desired_name_by_key maps a stable identity (csfiles token or
	# matapplication uri) to its recovered/label basename, before collision
	# disambiguation; source_path_by_key maps the same identity to the
	# on-disk file to copy.
	desired_name_by_key: dict[str, str] = {}
	source_path_by_key: dict[str, str] = {}
	csfiles_tokens: set[str] = set()

	for pool_dat_name in pool_dat_names:
		pool_dat_path = os.path.join(pool_dir, pool_dat_name)
		csfiles_tokens.update(_scan_csfiles_tokens(pool_dat_path))
		pool_base_dir = _find_pool_resource_base_dir(manifest_path, pool_dat_name)
		for uri, label in _scan_matapplication_refs(pool_dat_path):
			if uri in source_path_by_key:
				continue
			source_path_by_key[uri] = _resolve_package_relative_path(
				pool_dir, os.path.join(pool_base_dir, uri)
			)
			desired_name_by_key[uri] = label

	if csfiles_tokens:
		# Only require the CSResourceLinks resource to exist when a csfiles
		# token was actually found; packages with no csfiles images (e.g. the
		# minimal test manifests) need not declare or ship res00005.dat.
		resource_id_set = _load_csresourcelinks_ids(manifest_path, pool_dir)
		for token in csfiles_tokens:
			resource_id = token[len("xid-"):]
			if resource_id not in resource_id_set:
				raise ValueError(
					f"csfiles token '{token}' has no matching resourceId in the "
					f"CSResourceLinks manifest resource"
				)
			binary_path, sidecar_path = _find_csfiles_files(pool_dir, token)
			source_path_by_key[token] = binary_path
			desired_name_by_key[token] = _recover_original_filename(sidecar_path)

	if not desired_name_by_key:
		return None, _identity_src_map

	output_name_by_key = _assign_collision_safe_names(desired_name_by_key)
	media_dir = tempfile.mkdtemp(prefix="qti_bbexport_media_")
	for key, source_path in source_path_by_key.items():
		dest_path = os.path.join(media_dir, output_name_by_key[key])
		shutil.copyfile(source_path, dest_path)

	token_to_output_name = {
		token: output_name_by_key[token] for token in csfiles_tokens
	}
	src_map_fn = _make_csfiles_src_mapper(token_to_output_name)
	return media_dir, src_map_fn

#============================================
def _scan_csfiles_tokens(pool_dat_path: str) -> set[str]:
	"""
	Find every distinct csfiles xid token referenced anywhere in a pool `.dat`.

	Scans the raw file text rather than the parsed tree: the token text
	itself carries no characters that need XML unescaping, so a plain regex
	scan finds every reference regardless of which item encloses it (an item
	whose `bbmd_questiontype` is not dispatchable is scanned all the same).

	Args:
		pool_dat_path: Path to a pool `.dat`.

	Returns:
		The distinct "xid-<n>_1" tokens found, e.g. {"xid-23446236_1"}.
	"""
	with open(pool_dat_path, "r", encoding="utf-8") as pool_file:
		pool_text = pool_file.read()
	return set(CSFILES_TOKEN_PATTERN.findall(pool_text))

#============================================
def _scan_matapplication_refs(pool_dat_path: str) -> list[tuple[str, str]]:
	"""
	Find every hotspot `<matapplication uri>` element in a pool `.dat`.

	Args:
		pool_dat_path: Path to a pool `.dat`.

	Returns:
		A list of (uri, label) pairs, in document order. label falls back to
		the uri's basename when the element carries no `label` attribute.
	"""
	tree = lxml.etree.parse(pool_dat_path)
	refs = []
	for matapplication_el in tree.getroot().iter("matapplication"):
		uri = matapplication_el.get("uri")
		if not uri:
			continue
		label = matapplication_el.get("label") or os.path.basename(uri)
		refs.append((uri, label))
	return refs

#============================================
def _find_pool_resource_base_dir(manifest_path: str, pool_dat_name: str) -> str:
	"""
	Return the pool resource's `xml:base` directory (where its files live).

	Real Blackboard exports declare `xml:base="res00002"` on the pool
	resource; hotspot `<matapplication uri>` paths resolve relative to this
	directory, not the package root. Falls back to the `.dat` filename's own
	stem when no `xml:base` is declared (e.g. minimal test manifests).

	Args:
		manifest_path: Path to imsmanifest.xml.
		pool_dat_name: The pool `.dat` filename (its resource is looked up by
			`bb:file`).

	Returns:
		The base directory name the pool resource's own files resolve under.
	"""
	tree = lxml.etree.parse(manifest_path)
	bb_file_attr = f"{{{BB_NAMESPACE}}}file"
	xml_base_attr = f"{{{XML_NAMESPACE}}}base"
	for resource in tree.getroot().iter("resource"):
		if resource.get(bb_file_attr) != pool_dat_name:
			continue
		xml_base = resource.get(xml_base_attr)
		if xml_base:
			return xml_base
		break
	return os.path.splitext(pool_dat_name)[0]

#============================================
def _load_csresourcelinks_ids(manifest_path: str, pool_dir: str) -> set[str]:
	"""
	Read every `resourceId` declared by the manifest's CSResourceLinks resource.

	Args:
		manifest_path: Path to imsmanifest.xml.
		pool_dir: The pool package root the CSResourceLinks `.dat` lives under.

	Returns:
		The set of resourceId strings (e.g. {"23446236_1", ...}); empty when
		the manifest declares no CSResourceLinks resource.

	Raises:
		ValueError: the manifest declares a CSResourceLinks resource whose
			`.dat` file is missing.
	"""
	tree = lxml.etree.parse(manifest_path)
	bb_file_attr = f"{{{BB_NAMESPACE}}}file"
	resource_ids: set[str] = set()
	for resource in tree.getroot().iter("resource"):
		if resource.get("type") != CSRESOURCELINKS_RESOURCE_TYPE:
			continue
		dat_filename = resource.get(bb_file_attr)
		if not dat_filename:
			continue
		dat_path = os.path.join(pool_dir, dat_filename)
		if not os.path.isfile(dat_path):
			raise ValueError(
				f"Manifest points to missing CSResourceLinks file '{dat_filename}' "
				f"in '{pool_dir}'"
			)
		links_tree = lxml.etree.parse(dat_path)
		for link_el in links_tree.getroot().iter("cms_resource_link"):
			resource_id_el = link_el.find("resourceId")
			if resource_id_el is not None and resource_id_el.text:
				resource_ids.add(resource_id_el.text.strip())
	return resource_ids

#============================================
def _find_csfiles_files(pool_dir: str, token: str) -> tuple[str, str]:
	"""
	Locate a csfiles binary and its LOM sidecar for one xid token.

	Args:
		pool_dir: The pool package root.
		token: A "xid-<n>_1" token (as found by _scan_csfiles_tokens).

	Returns:
		A tuple of (binary_path, sidecar_path).

	Raises:
		FileNotFoundError: the csfiles home dir, the binary, or the sidecar
			is missing.
	"""
	home_dir = os.path.join(pool_dir, CSFILES_HOME_SUBDIR)
	if not os.path.isdir(home_dir):
		raise FileNotFoundError(
			f"csfiles token '{token}' referenced but '{home_dir}' does not exist"
		)
	binary_prefix = f"__{token}."
	binary_path = None
	# deterministic scan order so ties (should not occur) resolve predictably
	for filename in sorted(os.listdir(home_dir)):
		if filename.startswith(binary_prefix) and not filename.endswith(".xml"):
			binary_path = os.path.join(home_dir, filename)
			break
	if binary_path is None:
		raise FileNotFoundError(
			f"csfiles binary not found for token '{token}' under '{home_dir}'"
		)
	sidecar_path = binary_path + ".xml"
	if not os.path.isfile(sidecar_path):
		raise FileNotFoundError(
			f"LOM sidecar not found for token '{token}': '{sidecar_path}'"
		)
	return binary_path, sidecar_path

#============================================
def _recover_original_filename(sidecar_path: str) -> str:
	"""
	Recover the original course-relative filename from a LOM sidecar.

	The sidecar's `<identifier>` element carries
	`"<xid>#/courses/<course>/<original-name>"`; the recovered name is the
	basename of the path portion after the `#`.

	Args:
		sidecar_path: Path to a `.jpg.xml` LOM sidecar.

	Returns:
		The recovered original filename, e.g. "image-1.jpg".

	Raises:
		ValueError: the sidecar has no identifier, or it names no file.
	"""
	tree = lxml.etree.parse(sidecar_path)
	identifier_el = tree.getroot().find(f".//{{{LOM_NAMESPACE}}}identifier")
	if identifier_el is None or not identifier_el.text:
		raise ValueError(f"LOM sidecar '{sidecar_path}' has no identifier element")
	identifier_text = identifier_el.text.strip()
	_, _, path_part = identifier_text.partition("#")
	source_path = path_part if path_part else identifier_text
	original_name = os.path.basename(source_path)
	if not original_name:
		raise ValueError(
			f"LOM sidecar '{sidecar_path}' identifier names no file: '{identifier_text}'"
		)
	return original_name

#============================================
def _resolve_package_relative_path(pool_dir: str, relative_path: str) -> str:
	"""
	Resolve a package-relative path, rejecting traversal outside pool_dir.

	Mirrors the traversal check in `media_assets.resolve_asset` /
	`ItemBank.add_image`: the resolved path must stay within pool_dir.

	Args:
		pool_dir: The pool package root.
		relative_path: A path relative to pool_dir (e.g. a matapplication
			uri under the pool resource's `xml:base` directory).

	Returns:
		The resolved absolute path.

	Raises:
		ValueError: the path escapes pool_dir.
		FileNotFoundError: the resolved file does not exist.
	"""
	base_abs = os.path.abspath(pool_dir)
	resolved_path = os.path.normpath(os.path.join(base_abs, relative_path))
	if resolved_path != base_abs and not resolved_path.startswith(base_abs + os.sep):
		raise ValueError(f"path '{relative_path}' escapes the package root '{pool_dir}'")
	if not os.path.isfile(resolved_path):
		raise FileNotFoundError(f"referenced file not found: {resolved_path}")
	return resolved_path

#============================================
def _assign_collision_safe_names(desired_name_by_key: dict[str, str]) -> dict[str, str]:
	"""
	Assign deterministic, collision-safe output names for a set of keys.

	Same disambiguation pattern as `media_assets.assign_output_names`: keys
	are processed in sorted order, and a colliding basename gets a
	deterministic `name(1).ext`, `name(2).ext`, ... suffix.

	Args:
		desired_name_by_key: mapping of a stable identity key to its desired
			(possibly colliding) basename.

	Returns:
		A mapping of the same keys to disambiguated output names.
	"""
	used_names: set[str] = set()
	output_name_by_key = {}
	for key in sorted(desired_name_by_key):
		base_name = desired_name_by_key[key]
		candidate_name = base_name
		collision_counter = 1
		while candidate_name in used_names:
			root, extension = os.path.splitext(base_name)
			candidate_name = f"{root}({collision_counter}){extension}"
			collision_counter += 1
		used_names.add(candidate_name)
		output_name_by_key[key] = candidate_name
	return output_name_by_key

#============================================
def _make_csfiles_src_mapper(
	token_to_output_name: dict[str, str],
) -> collections.abc.Callable[[str], str]:
	"""
	Build the `<img src>` rewrite function for one pool's csfiles tokens.

	Args:
		token_to_output_name: mapping of "xid-<n>_1" token to its recovered,
			collision-safe filename in the extraction directory.

	Returns:
		A callable mapping an in-content src to its rewritten src; any src
		that is not a recognized csfiles token passes through unchanged.
	"""
	#----------------------------------------------------
	def _map_src(old_src: str) -> str:
		if not old_src.startswith(common_xml.CSFILES_SRC_PREFIX):
			return old_src
		token = old_src[len(common_xml.CSFILES_SRC_PREFIX):]
		return token_to_output_name.get(token, old_src)
	return _map_src

#============================================
def _identity_src_map(src: str) -> str:
	"""Return src unchanged; used when a pool carries no images."""
	return src
