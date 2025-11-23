import subprocess
import sys
import os
import pytest
from pathlib import Path

def run_cube_cmd(args, cwd=None, expect_fail=False):
    """Run a cube command via python module."""
    env = os.environ.copy()
    # Ensure we can find the cube package if running from source root
    root_python = str(Path(__file__).parent.parent.parent / "python")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{root_python}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = root_python

    cmd = [sys.executable, "-m", "cube.cli"] + args
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True
    )
    
    if expect_fail:
        assert result.returncode != 0, f"Command succeeded unexpectedly: {' '.join(cmd)}"
    else:
        assert result.returncode == 0, f"Command failed: {' '.join(cmd)}\nStdout: {result.stdout}\nStderr: {result.stderr}"
    
    return result

def test_version():
    result = run_cube_cmd(["--version"])
    assert "AgentCube" in result.stdout or "version" in result.stdout.lower()

def test_help():
    run_cube_cmd(["--help"])

def test_sessions_command():
    # This command lists sessions, should work even with empty list
    result = run_cube_cmd(["sessions"])
    assert "Sessions" in result.stdout or "No sessions" in result.stdout

def test_status_command_fake_task():
    # Status on non-existent task usually just shows info or fails gracefully depending on impl
    # The original script said it should not fail (return code 0)
    run_cube_cmd(["status", "test-task-123"])

def test_writers_help():
    run_cube_cmd(["writers", "--help"])

def test_panel_help():
    run_cube_cmd(["panel", "--help"])

def test_feedback_help():
    run_cube_cmd(["feedback", "--help"])

def test_resume_help():
    run_cube_cmd(["resume", "--help"])

def test_peer_review_help():
    run_cube_cmd(["peer-review", "--help"])

def test_orchestrate_help():
    run_cube_cmd(["orchestrate", "--help"])

def test_install_help():
    run_cube_cmd(["install", "--help"])

def test_validation_missing_files(tmp_path):
    # Create a dummy task ID but missing file
    # writers command
    run_cube_cmd(["writers", "test-task", "missing.md"], cwd=tmp_path, expect_fail=True)
    
    # panel command
    run_cube_cmd(["panel", "test-task", "missing.md"], cwd=tmp_path, expect_fail=True)
    
    # feedback command
    run_cube_cmd(["feedback", "sonnet", "test-task", "missing.md"], cwd=tmp_path, expect_fail=True)

def test_orchestrate_generation(tmp_path):
    # Create a dummy task file
    task_file = tmp_path / "test-task.md"
    task_file.write_text("# Test Task\nSimple test task for validation")
    
    # Run orchestrate prompt generation
    # Note: This might fail if it requires CUBE_CONFIG or valid setup. 
    # Based on original script, it just runs.
    
    # We need to be careful about where it runs. 
    # The original script runs: python3 -m cube.cli orchestrate prompt /tmp/test-task.md
    
    result = run_cube_cmd(["orchestrate", "prompt", str(task_file)], cwd=tmp_path)
    assert len(result.stdout) > 0 or len(result.stderr) > 0

def test_invalid_args():
    run_cube_cmd(["writers"], expect_fail=True)
    run_cube_cmd(["panel"], expect_fail=True)
    run_cube_cmd(["feedback"], expect_fail=True)
    run_cube_cmd(["resume"], expect_fail=True)
    
def test_feedback_invalid_writer(tmp_path):
    task_file = tmp_path / "test.md"
    task_file.write_text("# Test")
    run_cube_cmd(["feedback", "invalid-writer", "test-task", str(task_file)], cwd=tmp_path, expect_fail=True)

def test_resume_without_session(tmp_path):
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("prompt")
    run_cube_cmd(["writers", "test-nonexistent", str(prompt_file), "--resume"], cwd=tmp_path, expect_fail=True)

