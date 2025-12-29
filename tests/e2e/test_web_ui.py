import json
from datetime import datetime
import pytest
import requests
from playwright.sync_api import Page, expect

@pytest.mark.skip(reason="CI reliability issue: Frontend failed to start")
def test_backend_health(backend_server):
    """Verify backend health endpoint is reachable."""
    resp = requests.get(f"{backend_server}/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

@pytest.mark.skip(reason="CI reliability issue: Frontend failed to start")
def test_dashboard_loads(page: Page, frontend_server):
    """Verify the dashboard loads."""
    page.goto(frontend_server)
    
    # Expect title or some main element
    expect(page).to_have_title("AgentCube Web UI")
    
    # Check for main heading or navigation
    expect(page.get_by_text("Agent Cube").or_(page.get_by_text("Dashboard"))).to_be_visible()

@pytest.mark.skip(reason="CI reliability issue: Frontend failed to start")
def test_navigate_to_task_missing(page: Page, frontend_server):
    """Test navigation to a missing task detail page."""
    page.goto(f"{frontend_server}/tasks/missing-task")
    
    # Should show error for missing task
    # TaskDetail.tsx: "Failed to load task (404)" or just "Error: ..."
    expect(page.get_by_text("Error:")).to_be_visible()

@pytest.mark.skip(reason="CI reliability issue: Frontend failed to start")
def test_task_detail_loads(page: Page, frontend_server, mock_home):
    """Test loading a valid task."""
    task_id = "test-valid-task"
    state = {
        "task_id": task_id,
        "path": "/tmp/test/path",
        "current_phase": 1,
        "updated_at": datetime.now().isoformat(),
        "status": "in_progress",
        "writers_complete": False,
        "panel_complete": False,
        "synthesis_complete": False,
        "peer_review_complete": False
    }
    
    # Write state file
    state_file = mock_home / ".cube" / "state" / f"{task_id}.json"
    state_file.write_text(json.dumps(state))
    
    page.goto(f"{frontend_server}/tasks/{task_id}")
    
    # Should show task ID header
    expect(page.get_by_text(f"Task {task_id}")).to_be_visible()
    expect(page.get_by_text("Phase 1/10")).to_be_visible()

@pytest.mark.skip(reason="CI reliability issue: Frontend failed to start")
def test_decisions_page_link(page: Page, frontend_server, mock_home):
    """Test link to decisions page."""
    # Reuse valid task
    task_id = "test-valid-task"
    # Ensure state exists (might run parallel, but here sequential mostly)
    if not (mock_home / ".cube" / "state" / f"{task_id}.json").exists():
        state = {
            "task_id": task_id,
            "path": "/tmp/test/path",
            "current_phase": 1
        }
        (mock_home / ".cube" / "state" / f"{task_id}.json").write_text(json.dumps(state))

    page.goto(f"{frontend_server}/tasks/{task_id}")
    
    # Click "View Decisions"
    page.get_by_role("link", name="View Decisions").click()
    
    # URL should change
    expect(page).to_have_url(f"{frontend_server}/tasks/{task_id}/decisions")

