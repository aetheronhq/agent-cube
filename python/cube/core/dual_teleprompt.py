"""Dual teleprompt for Writer A and Writer B in fixed layout."""

import sys
from collections import deque
from threading import Lock

class DualTeleprompt:
    """Fixed layout: Writer A box on top, Writer B box below, output underneath."""
    
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
        
        self.lines_per_box = 3
        self.width = 100
        self.buffer_a = deque(maxlen=self.lines_per_box)
        self.buffer_b = deque(maxlen=self.lines_per_box)
        self.current_a = ""
        self.current_b = ""
        self.started = False
        self.initialized = True
        self.update_count = 0
    
    def add_token(self, writer: str, text: str) -> None:
        """Add thinking token from Writer A or B."""
        with self._lock:
            if not self.started:
                self._init_boxes()
            
            if writer == "A":
                self.current_a += text
                if text.endswith(('.', '!', '?', '\n')):
                    if self.current_a.strip():
                        self.buffer_a.append(self.current_a.strip()[:self.width - 4])
                        self._update_boxes()
                    self.current_a = ""
            else:
                self.current_b += text
                if text.endswith(('.', '!', '?', '\n')):
                    if self.current_b.strip():
                        self.buffer_b.append(self.current_b.strip()[:self.width - 4])
                        self._update_boxes()
                    self.current_b = ""
    
    def _init_boxes(self) -> None:
        """Initialize both boxes in fixed positions."""
        print()
        
        print(f"\033[2m╭─ 💭 Writer A {'─' * (self.width - 14)}╮\033[0m")
        for _ in range(self.lines_per_box):
            print(f"\033[2m│{' ' * (self.width - 2)}│\033[0m")
        print(f"\033[2m╰{'─' * self.width}╯\033[0m")
        
        print(f"\033[2m╭─ 💭 Writer B {'─' * (self.width - 14)}╮\033[0m")
        for _ in range(self.lines_per_box):
            print(f"\033[2m│{' ' * (self.width - 2)}│\033[0m")
        print(f"\033[2m╰{'─' * self.width}╯\033[0m")
        print()
        
        self.started = True
    
    def _update_boxes(self) -> None:
        """Update box contents only - never redraw borders."""
        self.update_count += 1
        
        if self.update_count % 5 != 0:
            return
        
        total_lines = (self.lines_per_box + 2) * 2 + 1
        
        sys.stdout.write(f"\033[{total_lines}A")
        sys.stdout.write("\033[1B")
        
        visible_a = list(self.buffer_a)[-self.lines_per_box:]
        for i in range(self.lines_per_box):
            line = visible_a[i] if i < len(visible_a) else ""
            sys.stdout.write(f"\r\033[2m│ {line:<{self.width - 4}} │\033[0m\033[K\n")
        
        sys.stdout.write("\033[2B")
        
        visible_b = list(self.buffer_b)[-self.lines_per_box:]
        for i in range(self.lines_per_box):
            line = visible_b[i] if i < len(visible_b) else ""
            sys.stdout.write(f"\r\033[2m│ {line:<{self.width - 4}} │\033[0m\033[K\n")
        
        sys.stdout.write(f"\033[{total_lines - (self.lines_per_box * 2 + 5)}B")
        sys.stdout.flush()
    
    def close(self) -> None:
        """Close and clear the boxes."""
        if self.started:
            self.started = False
    
    @classmethod
    def reset(cls):
        """Reset the singleton."""
        cls._instance = None

def get_dual_teleprompt() -> DualTeleprompt:
    """Get the global dual teleprompt instance."""
    return DualTeleprompt()

