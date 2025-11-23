import re
prompt = """
**Writer A Branch:** `writer-sonnet/test-integration`
**Writer B Branch:** `writer-codex/test-integration`
"""
writer = 'A'
# Improved pattern
pattern = f"Writer {writer}.*?branch:.*?([a-zA-Z0-9/_.-]+)"
print(f"Pattern: {pattern}")
match = re.search(pattern, prompt, re.IGNORECASE)
if match:
    # Clean up the match (remove leading/trailing quotes/backticks if captured)
    branch = match.group(1).strip("`'\" ")
    print(f"Match: {branch}")
else:
    print("No match")
