#!/bin/bash

# Set the maximum number of lines per file
MAX_LINES=815

# Initialize variables
OUTPUT_PREFIX="combined_python."
FILE_COUNTER=1
LINE_COUNT=0
CURRENT_OUTPUT="${OUTPUT_PREFIX}$(printf "%02d" $FILE_COUNTER)"

# Remove old output files
rm -f ${OUTPUT_PREFIX}??

# Find and process all Python files
find . -type f -name "*.py" | sort | while read -r file; do
    echo "Processing $file"

    # Count the number of lines in the current file
    FILE_LINES=$(wc -l < "$file")

    # If adding this file would exceed MAX_LINES, start a new output file
    if (( LINE_COUNT + FILE_LINES > MAX_LINES )); then
        FILE_COUNTER=$((FILE_COUNTER + 1))
        CURRENT_OUTPUT="${OUTPUT_PREFIX}$(printf "%02d" $FILE_COUNTER)"
        LINE_COUNT=0
    fi

    # Write file header
    echo -e "\n### FILE: $file ###\n" >> "$CURRENT_OUTPUT"

    # Append the file content
    cat "$file" >> "$CURRENT_OUTPUT"

    # Write file footer
    echo -e "\n### END OF $file ###\n" >> "$CURRENT_OUTPUT"

    # Update the current line count
    LINE_COUNT=$((LINE_COUNT + FILE_LINES + 3)) # 3 extra lines for headers and footers

done
wc ${OUTPUT_PREFIX}??
echo "Merged all Python files into multiple output files ($OUTPUT_PREFIX.01, $OUTPUT_PREFIX.02, etc.)"
