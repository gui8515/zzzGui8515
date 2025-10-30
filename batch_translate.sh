#!/bin/bash

# Batch translate KSP contract .cfg files
# Usage: ./batch_translate.sh <directory>

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <directory>"
    echo "Example: $0 ContractPacks/Spacetux"
    exit 1
fi

DIRECTORY="$1"

if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory '$DIRECTORY' does not exist."
    exit 1
fi

# Count total files
total_files=$(find "$DIRECTORY" -name "*.cfg" -type f | wc -l)

if [ "$total_files" -eq 0 ]; then
    echo "No .cfg files found in '$DIRECTORY'"
    exit 0
fi

echo "Found $total_files .cfg files in '$DIRECTORY'"
echo "Starting translation..."
echo

count=0
errors=0

# Find all .cfg files and translate them
while IFS= read -r -d '' file; do
    count=$((count + 1))
    echo "[$count/$total_files] Translating: $file"
    
    if python3 translate_contracts.py "$file" --in-place; then
        echo "  ✓ Success"
    else
        echo "  ✗ Failed"
        errors=$((errors + 1))
    fi
done < <(find "$DIRECTORY" -name "*.cfg" -type f -print0)

echo
echo "================================"
echo "Translation complete!"
echo "Total files: $total_files"
echo "Successful: $((total_files - errors))"
echo "Errors: $errors"
echo "================================"

if [ "$errors" -gt 0 ]; then
    exit 1
fi

exit 0
