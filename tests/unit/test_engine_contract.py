#!/usr/bin/env python3

# Standard Library

# QTI Package Maker
from qti_package_maker.engines import engine_registration


def test_engine_classes_import_and_validate(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	engine_registration.register_engines()
	for engine_info in engine_registration.ENGINE_REGISTRY.values():
		engine_cls = engine_info["engine_class"]
		engine = engine_cls("dummy", verbose=False)
		assert engine.name
		assert engine.write_item is not None
