"""Tests for cube.core.decision_parser module."""

import json

import pytest
from cube.core.decision_parser import (
    JudgeDecision,
    aggregate_decisions,
    get_peer_review_status,
    normalize_winner,
    parse_judge_decision,
    parse_single_decision_file,
)
from cube.core.user_config import clear_config_cache


@pytest.fixture(autouse=True)
def reset_config():
    """Clear config cache before and after each test."""
    clear_config_cache()
    yield
    clear_config_cache()


@pytest.fixture
def mock_config(tmp_path, monkeypatch):
    """Create a minimal cube.yaml for testing."""
    config_content = """
writers:
  writer_a:
    name: "opus"
    model: "opus-4.5"
    label: "Writer Opus"
    color: "green"
  writer_b:
    name: "codex"
    model: "gpt-5.1"
    label: "Writer Codex"
    color: "blue"

judges:
  judge_1:
    model: "opus-4.5"
    label: "Judge Opus"
    color: "green"
  judge_2:
    model: "gpt-5.1"
    label: "Judge Codex"
    color: "yellow"
  judge_3:
    model: "gemini-3-pro"
    label: "Judge Gemini"
    color: "magenta"
"""
    config_path = tmp_path / "cube.yaml"
    config_path.write_text(config_content)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".git").mkdir()
    return tmp_path


@pytest.fixture
def sample_decision():
    """Sample decision JSON data for parsing tests."""
    return {
        "judge": "judge_1",
        "task_id": "test-task",
        "decision": "APPROVED",
        "winner": "writer_a",
        "scores": {
            "writer_a": {"total": 8.5},
            "writer_b": {"total": 7.2},
        },
        "blocker_issues": [],
        "recommendation": "Writer A solution is simpler and cleaner.",
        "timestamp": "2026-01-02T10:00:00",
    }


@pytest.fixture
def decisions_dir(tmp_path):
    """Create decisions directory for tests."""
    decisions = tmp_path / ".prompts" / "decisions"
    decisions.mkdir(parents=True)
    return decisions


class TestNormalizeWinner:
    """Tests for normalize_winner function."""

    def test_writer_a_from_key(self, mock_config):
        """'writer_a' resolves to writer_a."""
        assert normalize_winner("writer_a") == "writer_a"

    def test_writer_a_with_spaces(self, mock_config):
        """'Writer A' resolves to writer_a."""
        assert normalize_winner("Writer A") == "writer_a"

    def test_writer_a_uppercase(self, mock_config):
        """'WRITER_A' resolves to writer_a."""
        assert normalize_winner("WRITER_A") == "writer_a"

    def test_writer_b_from_key(self, mock_config):
        """'writer_b' resolves to writer_b."""
        assert normalize_winner("writer_b") == "writer_b"

    def test_writer_b_with_spaces(self, mock_config):
        """'Writer B' resolves to writer_b."""
        assert normalize_winner("Writer B") == "writer_b"

    def test_empty_returns_tie(self, mock_config):
        """Empty string returns 'TIE'."""
        assert normalize_winner("") == "TIE"

    def test_none_returns_tie(self, mock_config):
        """None returns 'TIE' (after converting to string check)."""
        assert normalize_winner(None) == "TIE"

    def test_invalid_returns_tie(self, mock_config):
        """Invalid winner string returns 'TIE'."""
        assert normalize_winner("unknown_winner") == "TIE"
        assert normalize_winner("neither") == "TIE"


class TestParseSingleDecisionFile:
    """Tests for parse_single_decision_file function."""

    def test_valid_json(self, tmp_path, sample_decision):
        """Parse well-formed JSON decision file."""
        decision_file = tmp_path / "decision.json"
        decision_file.write_text(json.dumps(sample_decision))

        result = parse_single_decision_file(decision_file)

        assert result is not None
        assert result["judge"] == "judge_1"
        assert result["decision"] == "APPROVED"
        assert result["winner"] == "writer_a"

    def test_malformed_json(self, tmp_path):
        """Return None for malformed JSON."""
        decision_file = tmp_path / "bad.json"
        decision_file.write_text("{invalid json content")

        result = parse_single_decision_file(decision_file)

        assert result is None

    def test_nonexistent_file(self, tmp_path):
        """Return None for missing file."""
        result = parse_single_decision_file(tmp_path / "missing.json")

        assert result is None

    def test_empty_file(self, tmp_path):
        """Return None for empty file (invalid JSON)."""
        decision_file = tmp_path / "empty.json"
        decision_file.write_text("")

        result = parse_single_decision_file(decision_file)

        assert result is None


class TestParseJudgeDecision:
    """Tests for parse_judge_decision function."""

    def test_extracts_all_fields(self, mock_config, decisions_dir, sample_decision):
        """Extract judge, task_id, decision, winner, scores, blockers, recommendation."""
        decision_file = decisions_dir / "judge_1-test-task-decision.json"
        decision_file.write_text(json.dumps(sample_decision))

        result = parse_judge_decision("judge_1", "test-task", project_root=mock_config)

        assert result is not None
        assert result.judge == "judge_1"
        assert result.task_id == "test-task"
        assert result.decision == "APPROVED"
        assert result.winner == "writer_a"
        assert result.scores["writer_a"] == 8.5
        assert result.scores["writer_b"] == 7.2
        assert result.blocker_issues == []
        assert "Writer A solution" in result.recommendation

    def test_handles_nested_panel_recommendation(self, mock_config, decisions_dir):
        """Handle nested panel_recommendation structure."""
        nested_decision = {
            "judge": "judge_2",
            "task_id": "test-task",
            "panel_recommendation": {
                "final_decision": "APPROVED",
                "selected_writer": "Writer B",
                "reasoning": "Writer B has better test coverage.",
            },
            "scores": {
                "writer_a": {"total": 7.0},
                "writer_b": {"total": 8.0},
            },
        }
        decision_file = decisions_dir / "judge_2-test-task-decision.json"
        decision_file.write_text(json.dumps(nested_decision))

        result = parse_judge_decision("judge_2", "test-task", project_root=mock_config)

        assert result is not None
        assert result.decision == "APPROVED"
        assert result.winner == "writer_b"
        assert "test coverage" in result.recommendation

    def test_handles_comparison_structure(self, mock_config, decisions_dir):
        """Handle comparison structure with better_implementation."""
        comparison_decision = {
            "judge": "judge_3",
            "task_id": "test-task",
            "vote": "writer_a",
            "comparison": {
                "better_implementation": "writer_a",
                "rationale": "Writer A is more maintainable.",
            },
            "scores": {
                "writer_a": {"total": 8.0},
                "writer_b": {"total": 7.5},
            },
        }
        decision_file = decisions_dir / "judge_3-test-task-decision.json"
        decision_file.write_text(json.dumps(comparison_decision))

        result = parse_judge_decision("judge_3", "test-task", project_root=mock_config)

        assert result is not None
        assert result.winner == "writer_a"

    def test_returns_none_for_missing_file(self, mock_config):
        """Return None for missing decision file."""
        result = parse_judge_decision("judge_1", "nonexistent-task", project_root=mock_config)

        assert result is None

    def test_extracts_blockers(self, mock_config, decisions_dir):
        """Extract blocker issues correctly."""
        decision_with_blockers = {
            "judge": "judge_1",
            "task_id": "test-task",
            "decision": "REQUEST_CHANGES",
            "winner": "writer_a",
            "scores": {"writer_a": {"total": 6.0}, "writer_b": {"total": 5.0}},
            "blocker_issues": ["Missing error handling", "No tests"],
            "recommendation": "Needs work.",
        }
        decision_file = decisions_dir / "judge_1-test-task-decision.json"
        decision_file.write_text(json.dumps(decision_with_blockers))

        result = parse_judge_decision("judge_1", "test-task", project_root=mock_config)

        assert result is not None
        assert "Missing error handling" in result.blocker_issues
        assert "No tests" in result.blocker_issues


class TestAggregateDecisions:
    """Tests for aggregate_decisions function."""

    def test_majority_vote(self, mock_config):
        """3 judges vote: A, A, B -> Winner A."""
        decisions = [
            JudgeDecision("judge_1", "t1", "APPROVED", "writer_a", {}, [], "", ""),
            JudgeDecision("judge_2", "t1", "APPROVED", "writer_a", {}, [], "", ""),
            JudgeDecision("judge_3", "t1", "APPROVED", "writer_b", {}, [], "", ""),
        ]

        result = aggregate_decisions(decisions)

        assert result["winner"] == "writer_a"
        assert result["winner_votes"]["writer_a"] == 2
        assert result["winner_votes"]["writer_b"] == 1

    def test_unanimous_vote(self, mock_config):
        """3 judges all vote A -> Winner A with consensus."""
        decisions = [
            JudgeDecision("judge_1", "t1", "APPROVED", "writer_a", {}, [], "", ""),
            JudgeDecision("judge_2", "t1", "APPROVED", "writer_a", {}, [], "", ""),
            JudgeDecision("judge_3", "t1", "APPROVED", "writer_a", {}, [], "", ""),
        ]

        result = aggregate_decisions(decisions)

        assert result["winner"] == "writer_a"
        assert result["consensus"] is True
        assert result["votes"]["approve"] == 3

    def test_tie_handling(self, mock_config):
        """Tie when votes split: A, B -> higher count wins or TIE."""
        decisions = [
            JudgeDecision("judge_1", "t1", "APPROVED", "writer_a", {}, [], "", ""),
            JudgeDecision("judge_2", "t1", "APPROVED", "writer_b", {}, [], "", ""),
        ]

        result = aggregate_decisions(decisions)

        assert result["winner"] in ["writer_a", "writer_b"]
        assert result["winner_votes"]["writer_a"] == 1
        assert result["winner_votes"]["writer_b"] == 1

    def test_empty_list_returns_error(self, mock_config):
        """Empty list returns error state."""
        result = aggregate_decisions([])

        assert result["consensus"] is False
        assert result["winner"] is None
        assert result["next_action"] == "ERROR"
        assert "No decisions found" in result["message"]

    def test_collects_blockers(self, mock_config):
        """Blockers collected from all decisions."""
        decisions = [
            JudgeDecision("j1", "t1", "REQUEST_CHANGES", "writer_a", {}, ["Issue 1"], "", ""),
            JudgeDecision("j2", "t1", "REQUEST_CHANGES", "writer_a", {}, ["Issue 2", "Issue 3"], "", ""),
        ]

        result = aggregate_decisions(decisions)

        assert len(result["blocker_issues"]) == 3
        assert "Issue 1" in result["blocker_issues"]
        assert "Issue 2" in result["blocker_issues"]

    def test_calculates_average_scores(self, mock_config):
        """Average scores calculated for each writer."""
        decisions = [
            JudgeDecision("j1", "t1", "APPROVED", "writer_a", {"writer_a": 8.0, "writer_b": 7.0}, [], "", ""),
            JudgeDecision("j2", "t1", "APPROVED", "writer_a", {"writer_a": 9.0, "writer_b": 6.0}, [], "", ""),
        ]

        result = aggregate_decisions(decisions)

        assert result["avg_score_writer_a"] == 8.5
        assert result["avg_score_writer_b"] == 6.5

    def test_next_action_merge_for_clean_winner(self, mock_config):
        """Clear winner with no blockers -> MERGE."""
        decisions = [
            JudgeDecision("j1", "t1", "APPROVED", "writer_a", {}, [], "", ""),
            JudgeDecision("j2", "t1", "APPROVED", "writer_a", {}, [], "", ""),
            JudgeDecision("j3", "t1", "APPROVED", "writer_b", {}, [], "", ""),
        ]

        result = aggregate_decisions(decisions)

        assert result["next_action"] == "MERGE"

    def test_next_action_synthesis_for_winner_with_blockers(self, mock_config):
        """Clear winner with blockers -> SYNTHESIS."""
        decisions = [
            JudgeDecision("j1", "t1", "APPROVED", "writer_a", {}, ["Fix this"], "", ""),
            JudgeDecision("j2", "t1", "APPROVED", "writer_a", {}, [], "", ""),
            JudgeDecision("j3", "t1", "APPROVED", "writer_b", {}, [], "", ""),
        ]

        result = aggregate_decisions(decisions)

        assert result["next_action"] == "SYNTHESIS"

    def test_next_action_feedback_for_tie(self, mock_config):
        """Tie -> FEEDBACK."""
        decisions = [
            JudgeDecision("j1", "t1", "APPROVED", "TIE", {}, [], "", ""),
            JudgeDecision("j2", "t1", "APPROVED", "TIE", {}, [], "", ""),
        ]

        result = aggregate_decisions(decisions)

        assert result["next_action"] == "FEEDBACK"


class TestGetPeerReviewStatus:
    """Tests for get_peer_review_status function."""

    def test_all_approved(self, mock_config, decisions_dir):
        """All judges approved -> approved: True."""
        for judge in ["judge_1", "judge_2", "judge_3"]:
            decision_file = decisions_dir / f"{judge}-test-task-peer-review.json"
            decision_file.write_text(
                json.dumps(
                    {
                        "judge": judge,
                        "decision": "APPROVED",
                        "remaining_issues": [],
                    }
                )
            )

        result = get_peer_review_status("test-task", project_root=mock_config)

        assert result["approved"] is True
        assert result["decisions_found"] == 3
        assert result["approvals"] == 3

    def test_with_issues(self, mock_config, decisions_dir):
        """Issues collected from all judges."""
        decision_1 = decisions_dir / "judge_1-test-task-peer-review.json"
        decision_1.write_text(
            json.dumps(
                {
                    "judge": "judge_1",
                    "decision": "REQUEST_CHANGES",
                    "remaining_issues": ["Issue A", "Issue B"],
                }
            )
        )

        decision_2 = decisions_dir / "judge_2-test-task-peer-review.json"
        decision_2.write_text(
            json.dumps(
                {
                    "judge": "judge_2",
                    "decision": "APPROVED",
                    "remaining_issues": [],
                }
            )
        )

        result = get_peer_review_status("test-task", project_root=mock_config)

        assert result["approved"] is False
        assert "Issue A" in result["remaining_issues"]
        assert "Issue B" in result["remaining_issues"]

    def test_no_decisions_found(self, mock_config):
        """No decisions returns not approved with 0 found."""
        result = get_peer_review_status("nonexistent-task", project_root=mock_config)

        assert result["approved"] is False
        assert result["decisions_found"] == 0

    def test_skipped_counts_as_approval(self, mock_config, decisions_dir):
        """SKIPPED decision counts as approval (tool failure, not code issue)."""
        decision_file = decisions_dir / "judge_1-test-task-peer-review.json"
        decision_file.write_text(
            json.dumps(
                {
                    "judge": "judge_1",
                    "decision": "SKIPPED",
                    "remaining_issues": [],
                }
            )
        )

        result = get_peer_review_status("test-task", project_root=mock_config)

        assert result["approvals"] == 1


class TestJudgeDecision:
    """Tests for JudgeDecision dataclass."""

    def test_all_fields_accessible(self):
        """All fields are accessible on JudgeDecision."""
        decision = JudgeDecision(
            judge="judge_1",
            task_id="test-task",
            decision="APPROVED",
            winner="writer_a",
            scores={"writer_a": 8.0, "writer_b": 7.0},
            blocker_issues=["Issue 1"],
            recommendation="Good work.",
            timestamp="2026-01-02T10:00:00",
        )

        assert decision.judge == "judge_1"
        assert decision.task_id == "test-task"
        assert decision.decision == "APPROVED"
        assert decision.winner == "writer_a"
        assert decision.scores["writer_a"] == 8.0
        assert decision.blocker_issues == ["Issue 1"]
        assert decision.recommendation == "Good work."
        assert decision.timestamp == "2026-01-02T10:00:00"
