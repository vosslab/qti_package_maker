# qti_package_maker

**`qti_package_maker`** is a Python library for **creating IMS Question and Test Interoperability (QTI) packages**, supporting the **QTI 2.1** specification. It helps generate standards-compliant ZIP files for uploading to Learning Management Systems (LMS) such as Blackboard and Canvas.

---

## Features

- Create QTI 2.1 ZIP packages quickly and easily.
- Supports the most widely used question types:
  - Multiple Choice (Single/Multiple Answer)
  - Fill-in-the-Blank (Textual and Numeric)
  - Matching and Ordering
- Automatically generates valid QTI XML files.
- Ensures compatibility with popular LMS platforms.
- Designed with extensibility for QTI 3.0 in mind.

---

## Installation

Install the library using `pip` (coming soon to PyPI):

```bash
pip install qti_package_maker
```

Or clone the repository:

```bash
git clone https://github.com/vosslab/qti_package_maker.git
cd qti_package_maker
```

---

## Example Usage

```python
from qti_package_maker import QTIManager, add_QTI_MC_Question

# Initialize the QTI package manager
manager = QTIManager(output_dir="./output")

# Add a Multiple Choice question
add_QTI_MC_Question(
    manager,
    question_id=1,
    question="What is 2 + 2?",
    choices=["2", "3", "4", "5"],
    answer="4"
)

# Save the QTI package as a ZIP file
manager.save_package()
```

---

## How It Works

1. **Create a QTIManager**: Initialize a manager instance for your package.
2. **Add Questions**: Use built-in functions like `add_QTI_MC_Question` to add questions to the package.
3. **Generate ZIP File**: Save the package, and the library will handle XML generation and ZIP creation.

---

## License

This project is licensed under the **GPL v3.0**. See the [LICENSE](LICENSE) file for details.

For proprietary/commercial use, please contact **[your email address]**.

---

## Contributing

Contributions are welcome! Please submit a pull request or file an issue for any bugs, features, or improvements.

---

## Acknowledgments

This library adheres to the IMS Global QTI specification. Learn more at [IMS Global](https://www.imsglobal.org/question/).
```
