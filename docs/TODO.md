# TODO

Content migrated from a legacy TODO list.

## Planned
- Track a histogram of answer choices.
- Clean up `choice_text`, `answer_text`, and `question_text`: remove leading/trailing `&nbsp;`,
  remove extra CRC16 sums at the start of `question_text`.
- Add a quiet mode (less verbose output).
- Add a shuffle mechanism.
- Add general read engine capabilities.
- Add BBQ reads for ORDER, NUM, FIB, and MULTI_FIB.
- Hints across formats: see [ROADMAP.md](ROADMAP.md).
- Update README wording where needed.
- Update `html_selftest` styling to respect dark mode.
- Track CRC codes for uniqueness.

## Done
- Full write capability for `human_readable`.
- Full write capability for `bbq_text_upload`.

## Unimplemented item functions
- `blackboard_qti_v2_1/add_item.py`: `MATCH`, `NUM`, `MULTI_FIB`, `ORDER`.
- `canvas_qti_v1_2/add_item.py`: `NUM`, `FIB`, `MULTI_FIB`, `ORDER`.
- `html_selftest/add_item.py`: `NUM`, `FIB`, `MULTI_FIB`, `ORDER`.

## Question function signatures
```python
# Question function Types

def MC(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	...

def MA(item_number: int, crc16_text: str, question_text: str, choices_list: list, answer_list: list):
	...

def MATCH(item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	...

def NUM(
	item_number: int,
	crc16_text: str,
	question_text: str,
	answer_float: float,
	tolerance_float: float,
	tolerance_message=True,
):
	...

def FIB(item_number: int, crc16_text: str, question_text: str, answers_list: list):
	...

def MULTI_FIB(item_number: int, crc16_text: str, question_text: str, answer_map: dict):
	...

def ORDER(item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	...
```

## TODO: implement automatic file type detection (MasterQTIPackage)

### Overview
Enhance `MasterQTIPackage` to automatically detect input file types based on
file extension and contents. This will allow users to call `read()` without
manually specifying the format.

### Steps
1. Detect file type
   - Use file extensions (`.zip`, `.txt`, `.xml`) as an initial hint.
   - Inspect ZIP contents for `imsmanifest.xml` to distinguish between QTI 1.2 and
     QTI 2.1.
   - Check the first line of `.txt` files for BBQ text format.
   - Scan the first 200 characters of `.xml` files for `<questestinterop>` (QTI 1.2) or
     `<assessmentTest>` (QTI 2.1).
2. Read using the correct reader
   - Automatically select the appropriate reader class (`QTIv1Reader`, `QTIv2Reader`,
     `BBQTextReader`, etc.).
   - Store all parsed questions for later conversion.
3. Support multiple reads in one session
   - Allow reading multiple files (`qti12.zip`, `bbq-questions.txt`, etc.).
   - Prevent duplicate reads of the same file.
4. Ensure compatibility with writers
   - Ensure the selected writer can handle all loaded question types.
   - Consider auto-detecting the best writer format based on input.

### Example usage (after implementation)
```python
qpm = MasterQTIPackage(writer="human")
qpm.read("qti12.zip")
qpm.read("qti21.zip")
qpm.read("bbq-questions.txt")
qpm.save("human.txt")
```
