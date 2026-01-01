"""Parser for CLI Review Adapter output."""

import json
import logging
from typing import Optional
from .base import ParserAdapter
from ...models.types import StreamMessage
from .cursor import CursorParser

logger = logging.getLogger(__name__)

class CLIReviewParser(ParserAdapter):
    """Parser for CLI Review Adapter output.
    
    Handles two formats:
    1. Simple format from adapter: {"type": "thinking", "content": "..."}
    2. Complex format from orchestrator: standard cursor-agent JSON
    """
    
    def __init__(self):
        self.cursor_parser = CursorParser()
    
    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse CLI review output."""
        if not line or not line.strip():
            return None
        
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        
        # Simple format: {"type": "X", "content": "Y"}
        if "content" in data and "message" not in data:
            msg = StreamMessage(
                type=data.get("type"),
                subtype=data.get("subtype"),
                content=data.get("content"),
                session_id=data.get("session_id")
            )
            return msg
        
        # Complex format: delegate to CursorParser
        return self.cursor_parser.parse(line)
    
    def supports_resume(self) -> bool:
        """CLI review doesn't support resume."""
        return False



