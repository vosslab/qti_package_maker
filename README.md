# qti_toolkit

**`qti_toolkit`** is a Python library for creating and managing IMS Question and Test Interoperability (QTI) packages, supporting the **QTI 2.1** specification. This toolkit helps generate standards-compliant ZIP files for LMS platforms like Blackboard and Canvas.

---

## Features

- Create QTI 2.1 ZIP packages with ease.
- Support for popular question types:
  - Multiple Choice (Single/Multiple Answer)
  - Fill-in-the-Blank (Textual and Numeric)
  - Matching and Ordering
- Standards-compliant XML generation.
- Designed with future extensibility for QTI 3.0.

---

## Installation

Install the library using `pip` (coming soon to PyPI):

```bash
pip install qti_toolkit
```

Or clone the repository:

```bash
git clone https://github.com/yourusername/qti_toolkit.git
cd qti_toolkit
```

---

## Example Usage

```python
from qti_toolkit import QTIManager, QTIMultipleChoiceItem

# Initialize the QTI package manager
manager = QTIManager(output_dir="./output")

# Add a multiple-choice question
mc_question = QTIMultipleChoiceItem(
    identifier="MCQ1",
    title="Sample MCQ",
    # question="What is 2 + 2?",
    choices=["2", "3", "4", "5"],
    answer="4"
)

manager.add_item(mc_question)

# Save the QTI package as a ZIP file
manager.save_package()
```

---

## License

This project is licensed under the **GPL v3.0**. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please submit a pull request or file an issue for any bugs, features, or improvements.

---

## Acknowledgments

This library adheres to the IMS Global QTI specification. Learn more at [IMS Global](https://www.imsglobal.org/question/).
```
