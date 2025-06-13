#!/bin/bash

echo "Updating requirements.txt..."

# Optional: back up the current requirements file
cp requirements.txt requirements_backup.txt 2>/dev/null

# Freeze only top-level installed packages, sorted
pip freeze | sort > requirements.txt

echo "✅ requirements.txt updated successfully."
