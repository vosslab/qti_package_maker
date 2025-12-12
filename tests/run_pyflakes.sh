#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PY_ROOT}"

# Run pyflakes on all Python files and capture output
PYFLAKES_OUT="${SCRIPT_DIR}/pyflakes.txt"
find "${PY_ROOT}" \
	-type d \( -name .git -o -name .venv -o -name .pytest_cache -o -name __pycache__ \) -prune -o \
	-type f -name "*.py" -print0 \
	| xargs -0 pyflakes > "${PYFLAKES_OUT}" 2>&1 || true

RESULT=$(wc -l < "${PYFLAKES_OUT}")

# Success if no errors were found
if [ "${RESULT}" -eq 0 ]; then
    echo "No errors found!!!"
    exit 0
fi

	echo "First 5 errors"
	head -n 5 "${PYFLAKES_OUT}"
	echo ""

	echo "Last 5 errors"
	tail -n 5 "${PYFLAKES_OUT}"
	echo ""

echo "Found ${RESULT} pyflakes errors"

# Fail if any errors were found
exit 1
