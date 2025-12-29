#!/usr/bin/env python3

# Standard Library
import os
import sys

# Pip3 Library
import pytest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)


@pytest.fixture
def sample_items():
	return {
		"MC": ("What is your favorite color?", ["blue", "red", "yellow"], "blue"),
		"MA": (
			"Which are types of fruit?",
			["orange", "banana", "apple", "lettuce", "spinach"],
			["orange", "banana", "apple"],
		),
		"MATCH": ("Match item to color.", ["orange", "banana", "lettuce"], ["orange", "yellow", "green"]),
		"NUM": ("What is 2 + 2?", 4.0, 0.1, True),
		"FIB": ("Complete the sentence: The sky is __.", ["blue"]),
		"MULTI_FIB": ("Fill in the blanks: A [1] is a [2].", {"1": ["dog"], "2": ["mammal"]}),
		"ORDER": ("Arrange the planets by size.", ["Mercury", "Mars", "Venus", "Earth"]),
	}


@pytest.fixture
def sample_bbq_lines():
	return [
		"MC\t2+2?\t3\tincorrect\t4\tcorrect",
		"MA\tPrime numbers?\t2\tcorrect\t3\tcorrect\t4\tincorrect\t5\tcorrect",
		"MAT\tMatch capital to country.\tUSA\tWashington\tFrance\tParis",
		"NUM\tApprox pi?\t3.14\t0.01",
		"FIB\tCapital of France?\tParis",
		"FIB_PLUS\tFill in: [animal] has milk.\tanimal\tcow",
		"ORD\tOrder these.\tOne\tTwo\tThree",
	]


@pytest.fixture
def tmp_cwd(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	return tmp_path
