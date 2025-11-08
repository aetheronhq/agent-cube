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
            if not self.started:
                self._init_display()
            
            if prefix not in self.current_lines:
                self.current_lines[prefix] = ""
            
            self.current_lines[prefix] += text
            
            should_flush = text.endswith(('.', '!', '?', '\n'))
            
            if should_flush and self.current_lines[prefix].strip():
                line = f"[{prefix}] {self.current_lines[prefix].strip()}"
                
                if len(line) > self.width - 4:
                    line = line[:self.width - 7] + "..."
                
                self.buffer.append(line)
                self._render()
                
                self.current_lines[prefix] = ""
    
    def _init_display(self) -> None:
        """Initialize the teleprompt box."""
        print(f"\n\033[2m╭─ 💭 Thinking {'─' * (self.width - 13)}╮\033[0m")
        for _ in range(self.lines):
            print(f"\033[2m│{' ' * (self.width - 2)}│\033[0m")
        print(f"\033[2m╰{'─' * self.width}╯\033[0m")
        self.started = True
    
    def _render(self) -> None:
        """Render the scrolling window in place."""
        visible_lines = list(self.buffer)[-self.lines:]
        
        sys.stdout.write(f"\033[{self.lines + 1}A")
        
        for i in range(self.lines):
            if i < len(visible_lines):
                line = visible_lines[i]
            else:
                line = ""
            
            sys.stdout.write(f"\r\033[2m│ {line:<{self.width - 4}} │\033[0m\033[K\n")
        
        sys.stdout.write(f"\r\033[2m╰{'─' * self.width}╯\033[0m")
        sys.stdout.flush()
    
    def close(self) -> None:
        """Close the shared teleprompt."""
        with self._lock:
            if self.started:
                sys.stdout.write("\n\n")
                self.started = False
                self.current_lines.clear()
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        if cls._instance:
            cls._instance.close()
        cls._instance = None

def get_shared_teleprompt() -> SharedTeleprompter:
    """Get the global shared teleprompt instance."""
    return SharedTeleprompter()

