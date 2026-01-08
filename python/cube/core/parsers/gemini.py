"""Gemini CLI JSON parser."""

import json
from typing import Optional

from ...models.types import StreamMessage
from .base import ParserAdapter


class GeminiParser(ParserAdapter):
    """Parser for gemini CLI JSON format."""

    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse gemini CLI JSON line."""
        try:
            data = json.loads(line)

            if not isinstance(data, dict):
                return None

            msg_type = data.get("type")

            if msg_type == "init":
                return StreamMessage(
                    type="system", subtype="init", model=data.get("model"), session_id=data.get("session_id")
                )

            if msg_type == "message" and data.get("role") == "assistant":
                content = data.get("content", "")
                if content:
                    if len(content) > 200:
                        return StreamMessage(type="assistant", content=content)
                    else:
                        return StreamMessage(type="thinking", content=content)

            if msg_type == "tool_use":
                tool_name = data.get("tool_name", "")
                params = data.get("parameters", {}) or {}

                if tool_name == "read_many_files" and "paths" in params:
                    paths = params["paths"]
                    if paths:
                        return StreamMessage(
                            type="tool_call",
                            subtype="started",
                            tool_name="read",
                            tool_args={"path": f"{len(paths)} files"},
                        )

                elif tool_name == "run_shell_command":
                    return StreamMessage(
                        type="tool_call",
                        subtype="started",
                        tool_name="shell",
                        tool_args={"command": params.get("command", "")},
                    )

                elif tool_name == "read_file":
                    return StreamMessage(
                        type="tool_call",
                        subtype="started",
                        tool_name="read",
                        tool_args={"path": params.get("file_path", "")},
                    )

                elif tool_name == "write_file":
                    return StreamMessage(
                        type="tool_call",
                        subtype="started",
                        tool_name="write",
                        tool_args={"path": params.get("file_path", "")},
                    )

                elif tool_name in ("replace", "edit_file"):
                    return StreamMessage(
                        type="tool_call",
                        subtype="started",
                        tool_name="edit",
                        tool_args={"path": params.get("file_path", "")},
                    )

                elif tool_name:
                    return StreamMessage(
                        type="tool_call", subtype="started", tool_name=tool_name.replace("_", " "), tool_args=params
                    )

            if msg_type == "tool_result":
                return StreamMessage(type="tool_call", subtype="completed", tool_name="completed")

            return None

        except json.JSONDecodeError:
            line = line.strip()
            if line and not line.startswith(("{", "[")):
                # Show debug/log output as thinking so there's something in the thinking box
                return StreamMessage(type="thinking", content=line[:200])
            return None
        except (KeyError, TypeError, AttributeError):
            return None

    def supports_resume(self) -> bool:
        """Gemini CLI doesn't support session resume in non-interactive mode."""
        return False
