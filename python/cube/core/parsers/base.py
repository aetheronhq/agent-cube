"""Parser adapter interface for CLI-specific JSON parsing."""

from abc import ABC, abstractmethod
from typing import Optional
import json
from ...models.types import StreamMessage

class ParserAdapter(ABC):
    """Interface for parsing CLI-specific JSON output."""
    
    @abstractmethod
    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse a JSON line and return a StreamMessage."""
        pass
    
    @abstractmethod
    def supports_resume(self) -> bool:
        """Check if this CLI supports session resume."""
        pass

