#!/bin/bash
# Mock CodeRabbit CLI output

echo "Starting CodeRabbit review..."
echo "Reviewing branch: $PWD"

# Simulate findings
echo "## Summary"
echo "Found 2 issues."

echo "## Issues"
echo "[ERROR] src/main.py:42 - SQL Injection vulnerability detected."
echo "  Suggestion: Use parameterized queries."
echo ""
echo "[WARNING] src/utils.py:10 - Function complexity is high."
echo "  Suggestion: Refactor into smaller functions."

echo "Review complete."
