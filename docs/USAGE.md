# Usage

## Primary supported input format
The **Blackboard Question Upload (BBQ) text format** is the primary supported
input format for `qti_package_maker`. This format lets you write questions in a
plain text file and upload them into tests, surveys, and question pools on
Blackboard.

## BBQ file format guidelines
- Files must be **tab-delimited TXT**.
- Do **not** include a header row.
- Do **not** include blank lines.
- Newline characters cannot exist inside a question.
- Each row must contain **one question**.
- The **first field** in each row defines the question type.
- Fields are **separated by a TAB**.

## Supported BBQ question formats

| Question type | Format |
|--------------|--------|
| **Multiple Choice (MC)** | `MC TAB question text TAB answer text TAB correct|incorrect TAB answer two text TAB correct|incorrect` |
| **Multiple Answer (MA)** | `MA TAB question text TAB answer text TAB correct|incorrect TAB answer two text TAB correct|incorrect` |
| **Ordering (ORD)** | `ORD TAB question text TAB answer text TAB answer two text` |
| **Matching (MAT)** | `MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text` |
| **Fill in the Blank (FIB)** | `FIB TAB question text TAB answer text TAB answer two text` |
| **Fill in Multiple Blanks (FIB_PLUS)** | `FIB_PLUS TAB question text TAB variable1 TAB answer1 TAB answer2 TAB TAB variable2 TAB answer3` |
| **Numeric Response (NUM)** | `NUM TAB question text TAB answer TAB [optional]tolerance` |

## BBQ converter

Convert BBQ text files into output formats.

Example usage:
```sh
python3 tools/bbq_converter.py -i bbq-my_questions.txt -f canvas_qti_v1_2
```

Convert into all formats:
```sh
python3 tools/bbq_converter.py -i bbq-my_questions.txt --all
```

For full options:
```sh
python3 tools/bbq_converter.py -h
```

### Complete BBQ converter options
```text
usage: bbq_converter.py [-h] -i INPUT_FILE [-n QUESTION_LIMIT] [--allow-mixed]
                        [-f {canvas_qti_v1_2,blackboard_qti_v2_1,human_readable,bbq_text_upload,html_selftest}] [-a]
                        [-1 [OUTPUT_FORMAT]] [-2 [OUTPUT_FORMAT]] [-r [OUTPUT_FORMAT]] [-b [OUTPUT_FORMAT]] [-s [OUTPUT_FORMAT]]

Convert BBQ file to other formats.

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input INPUT_FILE, --input_file INPUT_FILE
                        Path to the input BBQ text file.
  -n QUESTION_LIMIT, --limit QUESTION_LIMIT, --question_limit QUESTION_LIMIT
                        Limit the number of input items.
  --allow-mixed         Allow mixed question types.
  -f {canvas_qti_v1_2,blackboard_qti_v2_1,human_readable,bbq_text_upload,html_selftest}, --format {canvas_qti_v1_2,blackboard_qti_v2_1,human_readable,bbq_text_upload,html_selftest}
                        Set output format (multiple allowed).
  -a, --all             Enable all output formats.
  -1 [OUTPUT_FORMAT], --qti12 [OUTPUT_FORMAT]
                        Set output format to Canvas QTI v1.2.
  -2 [OUTPUT_FORMAT], --qti21 [OUTPUT_FORMAT]
                        Set output format to Blackboard QTI v2.1.
  -r [OUTPUT_FORMAT], --human [OUTPUT_FORMAT]
                        Set output format to human-readable text.
  -b [OUTPUT_FORMAT], --bbq [OUTPUT_FORMAT]
                        Set output format to Blackboard Question Upload format.
  -s [OUTPUT_FORMAT], --html [OUTPUT_FORMAT]
                        Set output format to HTML self-test.
```

## Python API usage

### Creating an assessment package
```python
from qti_package_maker.package_interface import QTIPackageInterface

# Initialize the package with a name
qti_packer = QTIPackageInterface("example_assessment", verbose=True)

# Add a multiple-choice question
qti_packer.add_item("MC", (
	"What is your favorite color?",
	["blue", "red", "yellow"],
	"blue",
))

# Add a multiple-answer question
qti_packer.add_item("MA", (
	"Which of these are fruits?",
	["apple", "carrot", "banana", "broccoli"],
	["apple", "banana"],
))
```

### Saving the package
```python
# Save as Canvas QTI v1.2
qti_packer.save_package("canvas_qti_v1_2")

# Save as Blackboard QTI v2.1
qti_packer.save_package("blackboard_qti_v2_1")
```
