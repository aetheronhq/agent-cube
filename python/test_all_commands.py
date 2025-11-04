#!/usr/bin/env python3
"""Comprehensive test of all cube-py commands."""

import sys
import subprocess
from pathlib import Path

def run_cmd(cmd, should_fail=False):
    """Run a command and check result."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    success = (result.returncode != 0) if should_fail else (result.returncode == 0)
    
    if success:
        print(f"✅ {cmd}")
        return True
    else:
        print(f"❌ {cmd}")
        print(f"   stdout: {result.stdout[:200]}")
        print(f"   stderr: {result.stderr[:200]}")
        return False

def main():
    """Run all tests."""
    print("🧪 Comprehensive cube-py Command Testing")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    tests = [
        # Version and help
        ("Version display", "python3 -m cube.cli --version", False),
        ("Main help", "python3 -m cube.cli --help", False),
        ("Version command", "python3 -m cube.cli version", False),
        
        # Simple commands
        ("Sessions command", "python3 -m cube.cli sessions", False),
        ("Status with fake task", "python3 -m cube.cli status test-task-123", False),
        
        # Command help texts
        ("Writers help", "python3 -m cube.cli writers --help", False),
        ("Panel help", "python3 -m cube.cli panel --help", False),
        ("Feedback help", "python3 -m cube.cli feedback --help", False),
        ("Resume help", "python3 -m cube.cli resume --help", False),
        ("Peer-review help", "python3 -m cube.cli peer-review --help", False),
        ("Orchestrate help", "python3 -m cube.cli orchestrate --help", False),
        ("Install help", "python3 -m cube.cli install --help", False),
        
        # File validation (should fail gracefully)
        ("Writers with missing file", "python3 -m cube.cli writers test-task missing.md", True),
        ("Panel with missing file", "python3 -m cube.cli panel test-task missing.md", True),
        ("Feedback with missing file", "python3 -m cube.cli feedback sonnet test-task missing.md", True),
        
        # Orchestrate tests
        ("Orchestrate with temp file", "python3 -m cube.cli orchestrate prompt /tmp/test-task.md", False),
        
        # Invalid arguments
        ("Writers with no args", "python3 -m cube.cli writers", True),
        ("Panel with no args", "python3 -m cube.cli panel", True),
        ("Feedback with no args", "python3 -m cube.cli feedback", True),
        ("Resume with no args", "python3 -m cube.cli resume", True),
        
        # Invalid writer names
        ("Feedback with invalid writer", "python3 -m cube.cli feedback invalid-writer test-task /tmp/test.md", True),
        
        # Resume without session (should fail)
        ("Writers resume without session", "python3 -m cube.cli writers test-nonexistent ../test-prompts/test-writer-prompt.md --resume", True),
    ]
    
    print("Running tests...")
    print()
    
    for test_name, cmd, should_fail in tests:
        print(f"Testing: {test_name}")
        if run_cmd(cmd, should_fail):
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()
    
    if failed > 0:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All command tests passed!")
        print()
        print("Next: Test with actual cursor-agent execution:")
        print("  python3 -m cube.cli writers test-hello ../test-prompts/test-writer-prompt.md")
        print()

if __name__ == "__main__":
    # Create temp task file
    Path("/tmp/test-task.md").write_text("# Test Task\nSimple test")
    
    main()

