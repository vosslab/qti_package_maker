# Engines

## Output engines

### QTI v1.2 engine (Canvas QTI v1.2)
- **Engine name:** `canvas_qti_v1_2`
- **Format type:** QTI v1.2 (IMS XML format)
- **Compatible LMS:** Canvas, LibreTexts ADAPT
- **File output:** ZIP file containing QTI v1.2 XML files

### QTI v2.1 engine (Blackboard QTI v2.1)
- **Engine name:** `blackboard_qti_v2_1`
- **Format type:** QTI v2.1 (IMS XML format)
- **Compatible LMS:** Blackboard
- **File output:** ZIP file containing QTI v2.1 XML files

### Human-readable engine
- **Engine name:** `human_readable`
- **Format type:** Simple text file
- **Compatible LMS:** Any system that supports plain-text import
- **File output:** A structured text file listing the questions and answers
- **Use case:** Review questions before conversion to QTI

### Blackboard question upload engine
- **Engine name:** `bbq_text_upload`
- **Format type:** Blackboard-specific TXT upload format
- **Compatible LMS:** Blackboard (Original Course View)
- **File output:** A `.txt` file that Blackboard can upload

### HTML self-test engine
- **Engine name:** `html_selftest`
- **Format type:** HTML-based self-assessment
- **Compatible LMS:** Any web-based environment
- **File output:** A self-contained HTML file
- **Use case:** Self-assessment quizzes without LMS integration

## Engine capabilities

### Read and write

| Engine name         | Can read   | Can write   |
|---------------------|------------|-------------|
| bbq_text_upload     | ✅         | ✅          |
| blackboard_qti_v2_1 | ❌         | ✅          |
| canvas_qti_v1_2     | ❌         | ✅          |
| html_selftest       | ❌         | ✅          |
| human_readable      | ❌         | ✅          |
| text2qti            | ✅         | ✅          |

### Assessment item types

| Item type   | bbq text upload   | blackboard qti v2.1   | canvas qti v1.2   | html selftest   | human readable   | text2qti   |
|-------------|-------------------|-----------------------|-------------------|-----------------|------------------|------------|
| FIB         | ✅                | ✅                    | ❌                | ✅             | ✅               | ✅         |
| MA          | ✅                | ✅                    | ✅                | ✅             | ✅               | ✅         |
| MATCH       | ✅                | ✅                    | ✅                | ✅             | ✅               | ❌         |
| MC          | ✅                | ✅                    | ✅                | ✅             | ✅               | ✅         |
| MULTI_FIB   | ✅                | ✅                    | ✅                | ✅             | ✅               | ❌         |
| NUM         | ✅                | ✅                    | ✅                | ✅             | ✅               | ✅         |
| ORDER       | ✅                | ✅                    | ❌                | ✅             | ✅               | ❌         |
