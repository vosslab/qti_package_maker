# QTI Package Maker

`qti_package_maker` is a Python package for generating and converting assessment
packages across LMS formats, including IMS QTI v1.2 and v2.1, Blackboard text
upload, human-readable text, and HTML self-tests.

## Features
- Supports multiple QTI versions (Canvas QTI v1.2 and Blackboard QTI v2.1).
- Handles MC, MA, FIB, NUM, MATCH, ORDER, and MULTI_FIB question types.
- Modular engine system for format-specific readers and writers.
- CLI and Python API workflows.

## Quickstart
Install and usage details live in docs, but the shortest path looks like this:

```sh
pip install qti-package-maker
python3 tools/bbq_converter.py -i bbq-my_questions.txt -f canvas_qti_v1_2
```

For full usage, see [docs/USAGE.md](docs/USAGE.md).

## Standards
- [QTI 2.1 specification (1EdTech)](https://www.1edtech.org/standards/qti/index#QTI21)
- [QTI 1.2 specification (1EdTech)](https://www.1edtech.org/standards/qti/index#QTI%201.2)

## Documentation
- Installation: [docs/INSTALL.md](docs/INSTALL.md)
- Usage and CLI: [docs/USAGE.md](docs/USAGE.md)
- Question types: [docs/QUESTION_TYPES.md](docs/QUESTION_TYPES.md)
- Engines and capabilities: [docs/ENGINES.md](docs/ENGINES.md)
- Formats: [docs/FORMATS.md](docs/FORMATS.md)
- Troubleshooting: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Developer guide: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)
- Backlog: [docs/TODO.md](docs/TODO.md)
- Changelog: [docs/CHANGELOG.md](docs/CHANGELOG.md)
- Related projects: [docs/RELATED_PROJECTS.md](docs/RELATED_PROJECTS.md)
- Community and support: [docs/COMMUNITY.md](docs/COMMUNITY.md)

## Question Types

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

### Moodle Aiken Engine
- **Engine Name:** `moodle_aiken`
- **Format Type:** Moodle's Aiken multiple choice text upload format
- **Compatible LMS:** Moodle
- **File Output:** An Aiken text file
- **Use Case:** Used for uploading non-HTML, multiple-choice-only questions for Moodle

## Engines Capabilities

### Read and Write

| Engine Name         | Can Read   | Can Write   |
|---------------------|------------|-------------|
| bbq_text_upload     | Yes        | Yes         |
| blackboard_qti_v2_1 | No         | Yes         |
| canvas_qti_v1_2     | No         | Yes         |
| html_selftest       | No         | Yes         |
| human_readable      | No         | Yes         |
| moodle_aiken        | No         | Yes         |
| text2qti            | Yes        | Yes         |

### Assessment Item Types

| Item Type   | bbq text upload   | blackboard qti v2.1   | canvas qti v1.2   | html selftest   | human readable   | moodle aiken   | text2qti   |
|-------------|-------------------|-----------------------|-------------------|-----------------|------------------|----------------|------------|
| FIB         | Yes               | Yes                   | No                | No              | Yes              | No            | Yes        |
| MA          | Yes               | Yes                   | Yes               | Yes             | Yes              | No            | Yes        |
| MATCH       | Yes               | No                    | Yes               | Yes             | Yes              | No            | No         |
| MC          | Yes               | Yes                   | Yes               | Yes             | Yes              | Yes           | Yes        |
| MULTI_FIB   | Yes               | No                    | No                | No              | Yes              | No            | No         |
| NUM         | Yes               | No                    | No                | No              | Yes              | No            | Yes        |
| ORDER       | Yes               | No                    | No                | No              | Yes              | No            | No         |

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
  -A [OUTPUT_FORMAT], --aiken [OUTPUT_FORMAT], --moodle_aiken [OUTPUT_FORMAT]
                        Set output format to MOODLE aiken
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
```
This will create a Blackboard-compatible QTI v2.1 ZIP file.

## Development & Contribution

Contributions are welcome! Start with [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
and note changes in [docs/CHANGELOG.md](docs/CHANGELOG.md). Follow these steps
to contribute:

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
See [LICENSE](LICENSE).

## Acknowledgments
- Based on the IMS Global QTI specification.
- Inspired by the need for cross-platform assessment portability.
- Developed to improve e-learning content interoperability.
- Funding for production from Illinois Library OER grant.
