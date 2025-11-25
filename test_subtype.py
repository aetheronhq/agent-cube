import sys
import json
sys.path.insert(0, "python")
from cube.core.parsers.cursor_parser import CursorParser

parser = CursorParser()

# Test with assistant delta from log
line = '{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":" message specif"}]},"session_id":"abc","timestamp_ms":123}'
msg = parser.parse(line)

print(f"Parsed: {msg is not None}")
if msg:
    print(f"  type: {msg.type}")
    print(f"  subtype: {repr(msg.subtype)}")
    print(f"  content: {repr(msg.content[:30] if msg.content else None)}")



