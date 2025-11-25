import sys
import json
sys.path.insert(0, "python")
from cube.core.parsers.cursor_parser import CursorParser
from cube.automation.stream import format_stream_message

parser = CursorParser()

# First 10 thinking lines from actual log
with open("/Users/jacob/.cube/logs/judge_1-rand-panel-1763928587.json") as f:
    lines = f.readlines()

count = 0
for line in lines[:50]:
    try:
        data = json.loads(line)
        if data.get("type") == "thinking":
            msg = parser.parse(line.strip())
            if msg:
                formatted = format_stream_message(msg, "Judge Sonnet", "green")
                print(f"Content: {repr(msg.content[:30] if msg.content else None)}")
                print(f"Formatted starts with [thinking]: {formatted and formatted.startswith('[thinking]')}")
                count += 1
                if count >= 5:
                    break
    except:
        pass



