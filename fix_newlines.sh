#!/bin/bash

# Script to check and fix missing final newlines in Python files
# This follows the "Keep It Simple" design philosophy by using a straightforward approach

echo "Checking for Python files without final newlines..."

# Find all Python files in the src directory
find_output=$(find src -type f -name "*.py")

# Counter for files fixed
files_fixed=0

# Process each file
for file in $find_output; do
    # Check if the file ends with a newline
    if [ -s "$file" ] && [ $(tail -c 1 "$file" | wc -l) -eq 0 ]; then
        echo "Adding newline to $file"
        echo "" >> "$file"
        files_fixed=$((files_fixed + 1))
    fi
done

echo "Fixed $files_fixed files"
echo "Done!"
