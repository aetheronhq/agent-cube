"""CodeRabbit CLI output parser."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from ..parser_adapter import ParserAdapter
from ...models.types import StreamMessage

logger = logging.getLogger(__name__)


class CodeRabbitParser(ParserAdapter):
    """Parser for CodeRabbit CLI JSON format."""

    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse CodeRabbit JSON line into StreamMessage."""
        if not line or not line.strip():
            return None

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            logger.debug("Failed to parse CodeRabbit JSON: %s", line[:100])
            return None

        msg_type = data.get("type")
        if not msg_type:
            logger.debug("CodeRabbit message missing type: %s", line[:100])
            return None

        if msg_type == "review_comment":
            return self._parse_review_comment(data)
        if msg_type == "summary":
            return self._parse_summary(data)
        if msg_type == "fix_suggestion":
            return self._parse_fix_suggestion(data)
        if msg_type == "error":
            return self._parse_error(data)

        logger.debug("Unknown CodeRabbit message type: %s", msg_type)
        return None

    def supports_resume(self) -> bool:
        """CodeRabbit CLI does not support resume."""
        return False

    def _parse_review_comment(self, data: dict[str, Any]) -> StreamMessage:
        file_path = self._safe_str(data.get("file"), default="unknown")
        line_number = self._safe_int(data.get("line"))
        severity = self._format_severity(data.get("severity"))
        message = self._safe_str(data.get("message"), default="No description provided")

        content = f"[{severity}] {file_path}:{line_number} - {message}"

        suggestion = self._safe_str(data.get("suggestion"))
        if suggestion:
            content += f"\n  Suggestion: {suggestion}"

        return StreamMessage(
            type="tool_call",
            content=content,
            session_id=self._safe_str(data.get("review_id"))
            or self._safe_str(data.get("session_id")),
        )

    def _parse_summary(self, data: dict[str, Any]) -> StreamMessage:
        total = self._safe_int(data.get("total_issues"))
        blockers = self._safe_int(data.get("blockers"))
        warnings = self._safe_int(data.get("warnings"))

        content = f"Review complete: {total} issues found"
        if blockers or warnings:
            content += f" ({blockers} errors, {warnings} warnings)"

        return StreamMessage(type="output", content=content)

    def _parse_fix_suggestion(self, data: dict[str, Any]) -> StreamMessage:
        file_path = self._safe_str(data.get("file"), default="unknown")
        line_number = self._safe_int(data.get("line"))
        fix = self._safe_str(data.get("fix"), default="")

        content = f"Fix suggestion for {file_path}:{line_number}"
        if fix:
            content += f"\n{fix}"

        return StreamMessage(type="tool_call", content=content)

    def _parse_error(self, data: dict[str, Any]) -> StreamMessage:
        message = self._safe_str(data.get("message"), default="Unknown error")
        return StreamMessage(type="error", content=f"CodeRabbit error: {message}")

    @staticmethod
    def _safe_str(value: Any, *, default: str | None = None) -> Optional[str]:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
        return default

    @staticmethod
    def _safe_int(value: Any, *, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _format_severity(value: Any) -> str:
        if isinstance(value, str) and value.strip():
            return value.strip().upper()
        return "INFO"
