# Install

qti_package_maker installs as a Python package and is used via scripts under
[tools/](../tools/) or as an importable module.

## Requirements
- Python 3.9+ (project metadata); local tooling targets Python 3.12.
- pip
- Git (for source installs).

## Install from source
```sh
git clone https://github.com/vosslab/qti_package_maker.git
cd qti_package_maker
python3 -m venv .venv
source .venv/bin/activate
pip install -r pip_requirements.txt
pip install -e .
```

## Install from PyPI
```sh
pip install qti-package-maker
```

## Verify install
```sh
python3 -c "import qti_package_maker; print(qti_package_maker.__name__)"
```

## Known gaps
- Confirm supported operating systems beyond macOS if needed.
- Confirm whether PyPI wheels track this repo release cadence.
