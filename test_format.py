import sys
sys.path.insert(0, "python")
from cube.core.parsers.cursor_parser import CursorParser
from cube.automation.stream import format_stream_message

parser = CursorParser()
line = '{"type":"thinking","subtype":"delta","text":"back error","session_id":"abc","timestamp_ms":1763928680016}'
msg = parser.parse(line)

print(f"Parsed: {msg is not None}")
if msg:
    print(f"  type: {msg.type}")
    print(f"  content: {repr(msg.content)}")
    formatted = format_stream_message(msg, "Judge Sonnet", "green")
    print(f"Formatted: {repr(formatted)}")
    if formatted:
        print(f"Starts with [thinking]: {formatted.startswith('[thinking]')}")




