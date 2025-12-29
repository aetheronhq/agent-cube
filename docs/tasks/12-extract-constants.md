# Task 12: Extract Magic Numbers to Constants

## Objective
Replace magic numbers with named constants for maintainability.

## File: `python/cube/ui/routes/tasks.py`

### Current Code (6 instances)
```python
# Lines 190-191, 212-213, 231-232
"content": filepath.read_text()[:10000],
"truncated": filepath.stat().st_size > 10000,
```

### Fix
```python
# Add at top of file or in config.py
MAX_FILE_PREVIEW_SIZE = 10_000  # 10KB preview limit for UI

# Then use:
"content": filepath.read_text()[:MAX_FILE_PREVIEW_SIZE],
"truncated": filepath.stat().st_size > MAX_FILE_PREVIEW_SIZE,
```

## File: `python/cube/ui/server.py`

### Current Code
```python
allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
```

### Fix
```python
# Consider making configurable via env var
import os
ALLOWED_ORIGINS = os.getenv("CUBE_CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175").split(",")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    ...
)
```

## File: `python/cube/commands/ui.py`

### Current Code
```python
frontend_url = "http://localhost:5173"
host="127.0.0.1"
```

### Fix
```python
DEFAULT_FRONTEND_PORT = 5173
DEFAULT_BACKEND_HOST = "127.0.0.1"

frontend_url = f"http://localhost:{DEFAULT_FRONTEND_PORT}"
```

## Verification
- `grep -rEn "[^a-zA-Z_][0-9]{4,}[^0-9]" python/cube` should show fewer arbitrary numbers
- UI still works correctly

