"""Parser registry."""

from typing import Dict, Type
from ..parser_adapter import ParserAdapter
from .cursor_parser import CursorParser
from .gemini_parser import GeminiParser
from .cli_review_parser import CLIReviewParser

_PARSERS: Dict[str, Type[ParserAdapter]] = {
    "cursor-agent": CursorParser,
    "gemini": CursorParser,  # Gemini CLI now uses Cursor-style JSON format
    "cli-review": CLIReviewParser,
}

def get_parser(cli_name: str) -> ParserAdapter:
    """Get parser for CLI tool."""
    parser_class = _PARSERS.get(cli_name, CursorParser)
    return parser_class()

