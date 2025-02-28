# QTI Package Maker

## Introduction

`qti_package_maker` is a Python package designed for generating and converting question and test packages in various formats, including IMS QTI (Question & Test Interoperability) v1.2 and v2.1, Blackboard Question Upload format, human-readable text, and HTML self-test formats.

This package is developed for educators, instructional designers, and e-learning professionals who work with LMS platforms like Canvas, Blackboard, and Moodle.

This package provides a unified interface to create and manage assessments that can be imported into learning management systems (LMS) such as Canvas, Blackboard, and LibreTexts' ADAPT.

The package allows users to:
- Convert and generate question packages in multiple formats, including QTI v1.2 for Canvas/ADAPT and QTI v2.1 for Blackboard.
- Handle various question types, including multiple-choice, matching, numerical, and ordered questions.
- Clean and structure question text to remove formatting inconsistencies.
- Randomize question choices while ensuring the correct answer remains properly mapped.
- Read and write question packages in QTI, human-readable, and Blackboard formats.

This tool is primarily intended for educators, LMS administrators, and developers who need to convert, migrate, and generate structured assessments across different learning platforms.

## Features
- Supports Multiple QTI Versions – Generates valid QTI v1.2 (Canvas) and QTI v2.1 (Blackboard).
- Multiple Question Types – MC, MA, FIB, NUM, MATCH, ORDER, and MULTI_FIB.
- Modular Engine System – Easily swap between different export formats.
- Cleans Question Text – Removes extra metadata, leading/trailing spaces, and non-printable characters.
- Randomization and Shuffling – Allows question randomization while keeping the correct answers linked.
- Command-line and Python API Support – Use it in scripts or from the command line.
- Histogram Tracking – Keeps track of the frequency of answer choices.

## Installation

### Prerequisites
- Python 3.9 or later
- `pip` installed

### Installing from PyPI
```sh
pip install qti-package-maker
```

### Installing from Source
```sh
git clone https://github.com/vosslab/qti_package_maker.git
cd qti_package_maker
pip install -r requirements.txt
```

## Question Types

### 1. Multiple Choice (MC)
**Inputs:**
- `question_text` (str): The question prompt.
- `choices_list` (list): A list of answer choices.
- `answer_text` (str): The correct answer.

### 2. Multiple Answer (MA)
**Inputs:**
- `question_text` (str)
- `choices_list` (list)
- `answers_list` (list): A list of correct answers.

### 3. Matching (MATCH)
**Inputs:**
- `question_text` (str)
- `prompts_list` (list): Items to be matched.
- `choices_list` (list): Possible matching answers.

### 4. Numerical (NUM)
**Inputs:**
- `question_text` (str)
- `answer_float` (float): The correct numerical answer.
- `tolerance_float` (float): Accepted tolerance range.
- `tolerance_message` (bool, default=True): Message for tolerance handling.

### 5. Fill-in-the-Blank (FIB)
**Inputs:**
- `question_text` (str)
- `answers_list` (list): List of acceptable answers.

### 6. Multi-Part Fill-in-the-Blank (MULTI_FIB)
**Inputs:**
- `question_text` (str)
- `answer_map` (dict): A dictionary mapping blank positions to correct answers.

### 7. Ordered List (ORDER)
**Inputs:**
- `question_text` (str)
- `ordered_answers_list` (list): The correct sequence of answers.

## Output Engines

The package supports multiple output formats via engines. Each engine corresponds to a specific QTI version or alternative export format.

### 1. QTI v1.2 Engine (Canvas QTI v1.2)
- **Engine Name:** `canvas_qti_v1_2`
- **Format Type:** QTI v1.2 (IMS XML format)
- **Compatible LMS:** Canvas, LibreTexts ADAPT
- **File Output:** ZIP file containing QTI v1.2 XML files

### 2. QTI v2.1 Engine (Blackboard QTI v2.1)
- **Engine Name:** `blackboard_qti_v2_1`
- **Format Type:** QTI v2.1 (IMS XML format)
- **Compatible LMS:** Blackboard
- **File Output:** ZIP file containing QTI v2.1 XML files

### 3. Human-Readable Engine
- **Engine Name:** `human_readable`
- **Format Type:** Simple text file
- **Compatible LMS:** Any system that supports plain-text import
- **File Output:** A structured text file listing the questions and answers in a human-readable format
- **Use Case:** Used for reviewing questions before conversion to QTI

### 4. Blackboard Question Upload Engine
- **Engine Name:** `bbq_text_upload`
- **Format Type:** Blackboard-specific TXT upload format
- **Compatible LMS:** Blackboard (Original Course View)
- **Documentation:** https://help.blackboard.com/Learn/Instructor/Original/Tests_Pools_Surveys/Orig_Reuse_Questions/Upload_Questions
- **File Output:** A `.txt` file that Blackboard can directly upload

### 5. HTML Self-Test Engine
- **Engine Name:** `html_selftest`
- **Format Type:** HTML-based self-assessment
- **Compatible LMS:** Any web-based environment
- **File Output:** A self-contained HTML file
- **Use Case:** Used for creating self-assessment quizzes without LMS integration

## Usage

### Python API Usage
```python
from qti_package_maker.package_maker import MasterQTIPackage

# Initialize the package with the desired format engine
qti_packer = MasterQTIPackage("example_pool", engine="qti_v2")

# Add a multiple-choice question
qti_packer.add_MC("What is your favorite color?", ["blue", "red", "yellow"], "blue")

# Save the package
qti_packer.save_package()
```
This will create a Blackboard-compatible QTI v2.1 ZIP file.

### How to Specify an Engine
When using the package, select the desired engine name as a parameter:
```python
qti_packer = MasterQTIPackage("example_test", engine="canvas_qti_v1_2")
```
Or via CLI:
```sh
python3 tools/bbq_converter.py -i bbq-my_questions.txt -f qti12
python3 tools/bbq_converter.py -i bbq-my_questions.txt -f html_selftest
```

### Primary Supported Input Format: BBQ Text Format

The **Blackboard Question Upload (BBQ) text format** is currently the only supported input format for `qti_package_maker`. This format allows users to write questions in a plain text file and upload them into tests, surveys, and question pools on Blackboard. Once uploaded, the questions can be edited and used like those created directly within the LMS.

### **BBQ File Format Guidelines**
- Must be a **tab-delimited TXT file**.
- Should **not include a header row**.
- Should **not contain blank lines**.
- Each row must contain **one question**.
- The **first field in each row** defines the question type.
- Fields in a row are **separated by a TAB**.

### **Supported BBQ Question Formats**

| Question Type        | Format |
|----------------------|--------|
| **Multiple Choice (MC)** | `MC TAB question text TAB answer text TAB correct|incorrect TAB answer two text TAB correct|incorrect` |
| **Multiple Answer (MA)** | `MA TAB question text TAB answer text TAB correct|incorrect TAB answer two text TAB correct|incorrect` |
| **Ordering (ORD)** | `ORD TAB question text TAB answer text TAB answer two text` |
| **Matching (MAT)** | `MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text` |
| **Fill in the Blank (FIB)** | `FIB TAB question text TAB answer text TAB answer two text` |
| **Fill in Multiple Blanks (FIB_PLUS)** | `FIB_PLUS TAB question text TAB variable1 TAB answer1 TAB answer2 TAB TAB variable2 TAB answer3` |
| **Numeric Response (NUM)** | `NUM TAB question text TAB answer TAB [optional]tolerance` |

For more details, refer to the official **[Blackboard documentation](https://help.blackboard.com/Learn/Instructor/Original/Tests_Pools_Surveys/Orig_Reuse_Questions/Upload_Questions)**.

### Command-Line Usage
Convert a Blackboard Question Upload file (BBQ) to any other or all other packages using the `bbq_converter.py` tool:
```sh
python3 tools/bbq_converter.py -i bbq-my_questions.txt --all
```
This generates a Canvas-compatible QTI v1.2 ZIP package.

### BBQ Converter Options
The `bbq_converter.py` tool supports multiple output formats and options for processing question files:
```sh
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

## Development & Contribution

### Contribution Guidelines
1. Fork the repository
2. Clone the Repository
3. Create a feature branch (`feature-my-update`)
4. Commit changes and push to GitHub
5. Open a Pull Request

### Clone the Repository
```sh
git clone https://github.com/YOUR_USERNAME/qti_package_maker.git
cd qti_package_maker
```

## Roadmap and Planned Features
- Improve error handling and validation
- Add question randomization and shuffling
- Add unit tests

## License
This project is licensed under the GPL v3.0 License.
See [LICENSE](LICENSE) for details.

## Acknowledgments
- Based on the IMS Global QTI specification
- Inspired by the need for cross-platform assessment portability
- Developed to improve e-learning content interoperability
- Funding for production from Illinois Library OER grant

This package is developed for educators, instructional designers, and e-learning professionals who work with LMS platforms like LibreTexts ADAPT, Canvas, Blackboard, and Moodle.
