"""Claude Code CLI JSON parser."""

import json
from typing import Optional
from .base import ParserAdapter
from ...models.types import StreamMessage

class ClaudeCodeParser(ParserAdapter):
    """Parser for Claude Code CLI JSON format."""

    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse Claude Code CLI JSON line."""
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                return None

            msg_type = data.get("type")

            # Based on Anthropic's streaming API
            if msg_type == "message_start":
                return StreamMessage(
                    type="system",
                    subtype="init",
                    model=data.get("message", {}).get("model")
                )
            
            if msg_type == "content_block_delta":
                delta = data.get("delta", {})
                if delta.get("type") == "text_delta":
                    return StreamMessage(
                        type="assistant",
                        content=delta.get("text", "")
                    )

            if msg_type == "message_delta":
                return StreamMessage(
                    type="result",
                    content="Thinking complete."
                )

            if msg_type == "message_stop":
                return StreamMessage(
                    type="result",
                    content="Done."
                )

            # Fallback for other thinking/tool messages
            if msg_type == "thinking" or data.get("thinking"):
                return StreamMessage(
                    type="thinking",
                    content=data.get("reasoning", "...")
                )
            
            if data.get("tool_name"):
                 return StreamMessage(
                    type="tool_call",
                    subtype="started",
                    tool_name=data.get("tool_name"),
                    tool_args=data.get("parameters", {})
                )

            return None

        except json.JSONDecodeError:
            line = line.strip()
            if line:
                return StreamMessage(
                    type="system",
                    subtype="log",
                    content=f"[claude-code] {line[:200]}"
                )
            return None
        except (KeyError, TypeError, AttributeError):
            return None

    def supports_resume(self) -> bool:
        """Check if Claude Code CLI supports session resume."""
        return True
