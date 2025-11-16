"""CodeRabbit CLI output parser."""

import json
import logging
from typing import Optional
from ..parser_adapter import ParserAdapter
from ...models.types import StreamMessage

logger = logging.getLogger(__name__)


class CodeRabbitParser(ParserAdapter):
    """Parser for CodeRabbit CLI JSON format."""
    
    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse CodeRabbit JSON line into StreamMessage.
        
        Args:
            line: JSON string from CodeRabbit CLI output
            
        Returns:
            StreamMessage if parseable, None otherwise
        """
        if not line or not line.strip():
            return None
        
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            logger.debug(f"Failed to parse JSON: {line[:100]}")
            return None
        
        msg_type = data.get("type")
        if not msg_type:
            return None
        
        if msg_type == "review_comment":
            return self._parse_review_comment(data)
        elif msg_type == "summary":
            return self._parse_summary(data)
        elif msg_type == "fix_suggestion":
            return self._parse_fix_suggestion(data)
        elif msg_type == "error":
            return self._parse_error(data)
        else:
            logger.debug(f"Unknown CodeRabbit message type: {msg_type}")
            return None
    
    def _parse_review_comment(self, data: dict) -> StreamMessage:
        """Parse review comment into tool_call message."""
        file = data.get("file", "unknown")
        line = data.get("line", 0)
        severity = data.get("severity", "info").upper()
        message = data.get("message", "")
        
        content = f"[{severity}] {file}:{line} - {message}"
        
        if "suggestion" in data:
            content += f"\n  Suggestion: {data['suggestion']}"
        
        return StreamMessage(
            type="tool_call",
            content=content,
            session_id=data.get("review_id")
        )
    
    def _parse_summary(self, data: dict) -> StreamMessage:
        """Parse summary into output message."""
        total = data.get("total_issues", 0)
        blockers = data.get("blockers", 0)
        warnings = data.get("warnings", 0)
        
        content = f"Review complete: {total} issues found ({blockers} errors, {warnings} warnings)"
        
        return StreamMessage(
            type="output",
            content=content
        )
    
    def _parse_fix_suggestion(self, data: dict) -> StreamMessage:
        """Parse fix suggestion into tool_call message."""
        file = data.get("file", "unknown")
        line = data.get("line", 0)
        fix = data.get("fix", "")
        
        content = f"Fix suggestion for {file}:{line}\n{fix}"
        
        return StreamMessage(
            type="tool_call",
            content=content
        )
    
    def _parse_error(self, data: dict) -> StreamMessage:
        """Parse error into error message."""
        message = data.get("message", "Unknown error")
        
        return StreamMessage(
            type="error",
            content=f"CodeRabbit error: {message}"
        )
    
    def supports_resume(self) -> bool:
        """CodeRabbit CLI does not support resume."""
        return False
