# QTI Package Maker

## Introduction

`qti_package_maker` is a Python package designed for generating and converting question and test packages in various formats, including IMS QTI (Question & Test Interoperability) v1.2 and v2.1, Blackboard Question Upload format, human-readable text, and HTML self-test formats.

This package is developed for educators, instructional designers, and e-learning professionals working with LMS platforms such as LibreTexts' ADAPT, Canvas, and Blackboard. It provides a unified interface to create and manage assessments that can be imported into these learning management systems.

The package allows users to:
- Convert and generate question packages in multiple formats, including QTI v1.2 for Canvas/ADAPT and QTI v2.1 for Blackboard.
- Handle various question types, including multiple-choice, matching, numerical, and ordered questions.
- Clean and structure question text to remove formatting inconsistencies.
- Randomize question choices while ensuring the correct answer remains properly mapped.
- Read and write question packages in QTI, human-readable, and Blackboard formats.

This tool is primarily intended for educators and developers who need to convert, migrate, and generate structured assessments across different learning platforms.

## Table of Contents
<!-- md_toc github README.md -->
- [Introduction](#introduction)
- [Table of Contents](#table-of-contents)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installing from PyPI](#installing-from-pypi)
  - [Installing from Source](#installing-from-source)
- [Question Types](#question-types)
  - [Multiple Choice (MC)](#multiple-choice-mc)
  - [Multiple Answer (MA)](#multiple-answer-ma)
  - [Matching (MATCH)](#matching-match)
  - [Numerical Entry (NUM)](#numerical-entry-num)
  - [Fill-in-the-Blank (FIB)](#fill-in-the-blank-fib)
  - [Multi-Part Fill-in-the-Blank (MULTI_FIB)](#multi-part-fill-in-the-blank-multi_fib)
  - [Ordered List (ORDER)](#ordered-list-order)
- [Output Engines](#output-engines)
  - [QTI v1.2 Engine (Canvas QTI v1.2)](#qti-v12-engine-canvas-qti-v12)
  - [QTI v2.1 Engine (Blackboard QTI v2.1)](#qti-v21-engine-blackboard-qti-v21)
  - [Human-Readable Engine](#human-readable-engine)
  - [Blackboard Question Upload Engine](#blackboard-question-upload-engine)
  - [HTML Self-Test Engine](#html-self-test-engine)
- [Engines Capabilities](#engines-capabilities)
  - [Read and Write](#read-and-write)
  - [Assessment Item Types](#assessment-item-types)
- [Usage](#usage)
  - [Primary Supported Input Format](#primary-supported-input-format)
  - [BBQ File Format Guidelines](#bbq-file-format-guidelines)
  - [Supported BBQ Question Formats](#supported-bbq-question-formats)
- [BBQ Converter Command Options](#bbq-converter-command-options)
  - [Complete BBQ Converter Options](#complete-bbq-converter-options)
- [Python API Usage](#python-api-usage)
  - [Creating an Assessment Package](#creating-an-assessment-package)
    - [Saving the Package](#saving-the-package)
- [Development & Contribution](#development--contribution)
- [Roadmap and Planned Features](#roadmap-and-planned-features)
- [Related Projects](#related-projects)
- [License](#license)
- [Support this project](#support-this-project)
- [Social Media links](#social-media-links)
- [Acknowledgments](#acknowledgments)

## Features
- Supports Multiple QTI Versions – Generates valid QTI v1.2 (Canvas) and QTI v2.1 (Blackboard).
- Multiple Question Types – MC, MA, FIB, NUM, MATCH, ORDER, and MULTI_FIB.
- Modular Engine System – Easily swap between different export formats.
- Command-line and Python API Support – Use it in scripts or from the command line.

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

QTI Package Maker supports seven essential question types commonly used in assessments. These include Multiple Choice (MC), Multiple Answer (MA), Matching (MATCH), Numerical Entry (NUM), Fill-in-the-Blank (FIB), Multi-Part Fill-in-the-Blank (MULTI_FIB), and Ordered Lists (ORDER). Below is an overview of each type and its required inputs.

### Multiple Choice (MC)
**Inputs:**
- `question_text` (str): The question prompt.
- `choices_list` (list): A list of answer choices.
- `answer_text` (str): The correct answer.

### Multiple Answer (MA)
**Inputs:**
- `question_text` (str)
- `choices_list` (list)
- `answers_list` (list): A list of correct answers.

### Matching (MATCH)
**Inputs:**
- `question_text` (str)
- `prompts_list` (list): Items to be matched.
- `choices_list` (list): Possible matching answers.

### Numerical Entry (NUM)
**Inputs:**
- `question_text` (str)
- `answer_float` (float): The correct numerical answer.
- `tolerance_float` (float): Accepted tolerance range.
- `tolerance_message` (bool, default=True): Message for tolerance handling.

### Fill-in-the-Blank (FIB)
**Inputs:**
- `question_text` (str)
- `answers_list` (list): List of acceptable answers.

### Multi-Part Fill-in-the-Blank (MULTI_FIB)
**Inputs:**
- `question_text` (str)
- `answer_map` (dict): A dictionary mapping blank positions to correct answers.

### Ordered List (ORDER)
**Inputs:**
- `question_text` (str)
- `ordered_answers_list` (list): The correct sequence of answers.

## Output Engines

The package supports multiple output formats via engines. Each engine corresponds to a specific QTI version or alternative export format.

### QTI v1.2 Engine (Canvas QTI v1.2)
- **Engine Name:** `canvas_qti_v1_2`
- **Format Type:** QTI v1.2 (IMS XML format)
- **Compatible LMS:** Canvas, LibreTexts ADAPT
- **File Output:** ZIP file containing QTI v1.2 XML files

### QTI v2.1 Engine (Blackboard QTI v2.1)
- **Engine Name:** `blackboard_qti_v2_1`
- **Format Type:** QTI v2.1 (IMS XML format)
- **Compatible LMS:** Blackboard
- **File Output:** ZIP file containing QTI v2.1 XML files

### Human-Readable Engine
- **Engine Name:** `human_readable`
- **Format Type:** Simple text file
- **Compatible LMS:** Any system that supports plain-text import
- **File Output:** A structured text file listing the questions and answers in a human-readable format
- **Use Case:** Used for reviewing questions before conversion to QTI

### Blackboard Question Upload Engine
- **Engine Name:** `bbq_text_upload`
- **Format Type:** Blackboard-specific TXT upload format
- **Compatible LMS:** Blackboard (Original Course View)
- **Documentation:** https://help.blackboard.com/Learn/Instructor/Original/Tests_Pools_Surveys/Orig_Reuse_Questions/Upload_Questions
- **File Output:** A `.txt` file that Blackboard can directly upload

### HTML Self-Test Engine
- **Engine Name:** `html_selftest`
- **Format Type:** HTML-based self-assessment
- **Compatible LMS:** Any web-based environment
- **File Output:** A self-contained HTML file
- **Use Case:** Used for creating self-assessment quizzes without LMS integration

## Engines Capabilities

### Read and Write

| Engine Name         | Can Read   | Can Write   |
|---------------------|------------|-------------|
| bbq_text_upload     | ✅         | ✅          |
| blackboard_qti_v2_1 | ❌         | ✅          |
| canvas_qti_v1_2     | ❌         | ✅          |
| html_selftest       | ❌         | ✅          |
| human_readable      | ❌         | ✅          |
| text2qti            | ✅         | ✅          |

### Assessment Item Types

| Item Type   | bbq text upload   | blackboard qti v2.1   | canvas qti v1.2   | html selftest   | human readable   | text2qti   |
|-------------|-------------------|-----------------------|-------------------|-----------------|------------------|------------|
| FIB         | ✅                | ✅                    | ❌                | ❌             | ✅               | ✅         |
| MA          | ✅                | ✅                    | ✅                | ✅             | ✅               | ✅         |
| MATCH       | ✅                | ❌                    | ✅                | ✅             | ✅               | ❌         |
| MC          | ✅                | ✅                    | ✅                | ✅             | ✅               | ✅         |
| MULTI_FIB   | ✅                | ❌                    | ❌                | ❌             | ✅               | ❌         |
| NUM         | ✅                | ❌                    | ❌                | ❌             | ✅               | ✅         |
| ORDER       | ✅                | ❌                    | ❌                | ❌             | ✅               | ❌         |

## Usage

### Primary Supported Input Format

The **Blackboard Question Upload (BBQ) text format** is currently the only supported input format for `qti_package_maker`. This format allows users to write questions in a plain text file and upload them into tests, surveys, and question pools on Blackboard. Once uploaded, the questions can be edited and used like those created directly within the LMS.

### BBQ File Format Guidelines
- Must be a **tab-delimited TXT file**.
- Should **not include a header row**.
- Should **not contain blank lines**.
- New lines characters cannot exist within the question.
- Each row must contain **one question**.
- The **first field in each row** defines the question type.
- Fields in a row are **separated by a TAB**.

### Supported BBQ Question Formats

| Question Type        | Format |
|----------------------|--------|
| **Multiple Choice (MC)** | ``MC TAB question text TAB answer text TAB correct\|incorrect TAB answer two text TAB correct\|incorrect`` |
| **Multiple Answer (MA)** | ``MA TAB question text TAB answer text TAB correct\|incorrect TAB answer two text TAB correct\|incorrect`` |
| **Ordering (ORD)** | `ORD TAB question text TAB answer text TAB answer two text` |
| **Matching (MAT)** | `MAT TAB question text TAB answer text TAB matching text TAB answer two text TAB matching two text` |
| **Fill in the Blank (FIB)** | `FIB TAB question text TAB answer text TAB answer two text` |
| **Fill in Multiple Blanks (FIB_PLUS)** | `FIB_PLUS TAB question text TAB variable1 TAB answer1 TAB answer2 TAB TAB variable2 TAB answer3` |
| **Numeric Response (NUM)** | `NUM TAB question text TAB answer TAB [optional]tolerance` |

For more details, refer to the official **[Blackboard documentation](https://help.blackboard.com/Learn/Instructor/Original/Tests_Pools_Surveys/Orig_Reuse_Questions/Upload_Questions)**.

## BBQ Converter Command Options

The `bbq_converter.py` tool allows converting BBQ text files into multiple output formats. Example usage:
```sh
python3 tools/bbq_converter.py -i bbq-my_questions.txt -f qti12
```
To convert into all available formats:
```sh
python3 tools/bbq_converter.py -i bbq-my_questions.txt --all
```

For available options, use:
```sh
python3 tools/bbq_converter.py -h
```

### Complete BBQ Converter Options
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

## Python API Usage

### Creating an Assessment Package

```python
from qti_package_maker.package_interface import QTIPackageInterface

# Initialize the package with a name
qti_packer = QTIPackageInterface("example_assessment", verbose=True)

# Add a multiple-choice question
qti_packer.add_item("MC", ("What is your favorite color?", ["blue", "red", "yellow"], "blue"))

# Add a multiple-answer question
qti_packer.add_item("MA", ("Which of these are fruits?", ["apple", "carrot", "banana", "broccoli"], ["apple", "banana"]))
```

#### Saving the Package
```python
# Save as Canvas QTI v1.2
qti_packer.save_package("canvas_qti_v1_2")

# Save as Blackboard QTI v2.1
qti_packer.save_package("blackboard_qti_v2_1")
``````
This will create a Blackboard-compatible QTI v2.1 ZIP file.

## Development & Contribution

Contributions are welcome! Follow these steps to contribute:

1. **Fork** the repository on GitHub.
2. **Clone** your forked repository:
   ```sh
   git clone https://github.com/YOUR_USERNAME/qti_package_maker.git
   cd qti_package_maker
   ```
3. **Create a feature branch** (`feature-my-update`):
   ```sh
   git checkout -b feature-my-update
   ```
4. **Make your changes** and commit them:
   ```sh
   git add .
   git commit -m "Describe your changes here"
   ```
5. **Push** to your fork and open a **Pull Request**:
   ```sh
   git push origin feature-my-update
   ```
   - Navigate to the **Pull Requests** section of the original repository on GitHub.
   - Click **New Pull Request** and select your branch.
   - Provide a clear description of your changes and submit the request.

## Roadmap and Planned Features
- Improve error handling and validation
- Add question randomization and shuffling
- Add unit tests

## Related Projects

- **Moodle Question Format: Canvas**  
  A Moodle plugin that imports questions exported from the Canvas LMS as an XML file into Moodle.  
  GitHub: https://github.com/jmvedrine/moodle-qformat_canvas

- **text2qti**  
  A Python tool that converts Markdown-based plain text files into quizzes in QTI format, compatible with Canvas and other educational software.  
  PyPI: https://pypi.org/project/text2qti/

- **Blackboard Test Question Generator**  
  An online tool that assists in creating test questions for Blackboard by converting plain text into a format suitable for import.  
  Website: https://ed.oc.edu/blackboardquizgenerator/

- **amc2moodle**  
  A Python package that facilitates the conversion of AMC (Auto Multiple Choice) formatted questions into Moodle XML format for easy import.  
  PyPI: https://pypi.org/project/amc2moodle/

- **moodle-questions**  
  A Python library designed for manipulating questions in Moodle XML format, enabling programmatic creation and modification of Moodle quizzes.  
  GitHub: https://github.com/gethvi/moodle-questions

- **pyAssignment**  
  A Python module for authoring and assessing homework assignments, with capabilities to output assignments to LaTeX and Blackboard quiz formats.  
  PyPI: https://pypi.org/project/pyassignment/

## License

Copyright &copy; 2025, Dr. Neil Voss

qti_package_maker is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or any later version.

qti_package_maker is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

See the full license details in the 
[LICENSE file](https://github.com/vosslab/qti_package_maker/blob/main/LICENSE).
If not, see <http://www.gnu.org/licenses/>.

## Support this project

<!-- setup on Feb 28, 2025 -->
- **Bitcoin:** [Donate with Bitcoin](bitcoin:bc1qdexkqwzyet93ret40akqmms2jv99wvsgzdshu8?message=support%20qti_package_maker)
- **Dash:** [Donate with Dash](dash:XdDmwBVecEy9yyXKeD7hScLp7oN8rd4XNV?message=support%20qti_package_maker)
- **Patreon:** [Support on Patreon](https://www.patreon.com/vosslab)
- **Paypal:** [Donate via PayPal](https://paypal.me/vosslab)

## Social Media links

- [YouTube](https://www.youtube.com/neilvosslab)
- [Github](https://github.com/vosslab)
- [Bluesky](https://bsky.app/profile/neilvosslab.bsky.social)
- [Facebook](https://fb.me/neilvosslab)
- [LinkedIn](https://www.linkedin.com/in/vosslab)


## Acknowledgments
- Based on the IMS Global QTI specification
- Inspired by the need for cross-platform assessment portability
- Developed to improve e-learning content interoperability
- Funding for production from Illinois Library OER grant


