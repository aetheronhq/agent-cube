"""Parser registry."""

from typing import Dict, Type
from .base import ParserAdapter
from .cursor import CursorParser
from .gemini import GeminiParser
from .cli_review import CLIReviewParser

_PARSERS: Dict[str, Type[ParserAdapter]] = {
    "cursor-agent": CursorParser,
    "gemini": GeminiParser,
    "cli-review": CLIReviewParser,
}

def get_parser(cli_name: str) -> ParserAdapter:
    """Get parser for CLI tool."""
    parser_class = _PARSERS.get(cli_name, CursorParser)
    return parser_class()
