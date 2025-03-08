#!/bin/bash

# Output file
OUTPUT_FILE="combined_python_scripts.txt"

# Clear the output file if it exists
rm -f "$OUTPUT_FILE"

# Find and merge all Python files
find . -type f -name "*.py" | while read -r file; do
    echo "Processing $file"
    echo -e "\n### FILE: $file ###\n" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n### END OF $file ###\n" >> "$OUTPUT_FILE"
done

echo "Merged all Python files into $OUTPUT_FILE"

split -l 700 --numeric-suffixes=1 combined_python_scripts.txt file.
