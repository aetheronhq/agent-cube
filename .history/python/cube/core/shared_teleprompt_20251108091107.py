"""Shared teleprompt for multiple agents running in parallel."""

import sys
from collections import deque
from threading import Lock

class SharedTeleprompter:
    """Shared teleprompt showing thinking from multiple agents."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
        
        self.lines = 3
        self.width = 100
        self.buffer = deque(maxlen=self.lines * 3)
        self.current_lines = {}
        self.started = False
        self.initialized = True
    
    def add_token(self, prefix: str, text: str) -> None:
        """Add thinking token from a specific agent."""
        with self._lock:
            if prefix not in self.current_lines:
                self.current_lines[prefix] = ""
            
            self.current_lines[prefix] += text
            
            should_flush = text.endswith(('.', '!', '?', '\n'))
            
            if should_flush and self.current_lines[prefix].strip():
                line = self.current_lines[prefix].strip()
                
                if len(line) > 100:
                    line = line[:97] + "..."
                
                print(f"\033[2m[{prefix}] {line}\033[0m")
                
                self.current_lines[prefix] = ""
    
    def close(self) -> None:
        """Close the shared teleprompt."""
        pass
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        if cls._instance:
            cls._instance.close()
        cls._instance = None

def get_shared_teleprompt() -> SharedTeleprompter:
    """Get the global shared teleprompt instance."""
    return SharedTeleprompter()

