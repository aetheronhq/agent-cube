"""Prompt builders for UI review mode."""

from pathlib import Path

from ..core.config import PROJECT_ROOT

_REFS_DIR = Path(__file__).parent / "ui_review_refs"

_REF_FILES = [
    "principles.md",
    "system-principles.md",
    "design-psych.md",
    "interaction-psychology.md",
    "checklists.md",
    "icons.md",
]


def _load_ref(filename: str) -> str:
    path = _REFS_DIR / filename
    return path.read_text() if path.exists() else ""


def _build_knowledge_base() -> str:
    parts = []
    for filename in _REF_FILES:
        content = _load_ref(filename)
        if content:
            parts.append(content)
    return "\n\n---\n\n".join(parts)


def build_ui_review_prompt(
    task_id: str,
    input_content: str,
    input_type: str,
    context: str = "",
) -> str:
    """Build the base UI review prompt saved to .prompts/<task_id>.md.

    Args:
        task_id: Unique identifier for this review session.
        input_content: The UI artifact to review (file contents, description, or PR diff).
        input_type: One of "file", "description", "pr_diff".
        context: Optional one-liner: platform, target user, primary task.
    """
    knowledge = _build_knowledge_base()
    review_template = _load_ref("review-template.md")

    context_section = f"\n## Review Context\n\n{context}\n" if context else ""

    input_labels = {
        "file": "UI Files",
        "description": "UI Description",
        "pr_diff": "PR Diff (UI-related files only)",
    }
    input_label = input_labels.get(input_type, "Input")

    return f"""# UI Review

You are a UI/UX reviewer. Use the knowledge base below to produce a structured, prioritized review report.
{context_section}
---

## Knowledge Base

{knowledge}

---

## {input_label}

{input_content}

---

## Output Format

Follow this exact template:

{review_template}
"""


def build_ui_review_judge_instructions(task_id: str) -> str:
    """Build the judge-panel-specific instructions prepended inside judge_panel.py.

    Contains only the decision file format — the knowledge base and input are
    already in the base prompt file.
    """
    return f"""## Decision File

You MUST write your findings to this JSON file at the end of your review.

**File:** `{PROJECT_ROOT}/.prompts/decisions/{{{{judge_key}}}}-{task_id}-ui-review.json`

Use this EXACT absolute path.

**Required format:**
```json
{{{{
  "judge": "{{{{judge_key}}}}",
  "task_id": "{task_id}",
  "review_type": "ui-review",
  "P0": [
    {{{{
      "problem": "Short description",
      "evidence": "What you observed in the UI",
      "diagnosis": "execution gulf | evaluation gulf | slip | mistake",
      "principle": "Optional: e.g. Fitts's Law, Hick's Law, Loss Aversion, Gulf of Evaluation",
      "fix": "Specific, implementable fix",
      "acceptance": "How to verify the fix is done"
    }}}}
  ],
  "P1": [
    {{{{
      "problem": "Short description",
      "evidence": "What you observed",
      "diagnosis": "execution gulf | evaluation gulf | slip | mistake",
      "principle": "Optional: relevant HCI law or cognitive principle",
      "fix": "Specific fix",
      "acceptance": "How to verify"
    }}}}
  ],
  "P2": [
    {{{{
      "problem": "Short description",
      "fix": "Specific fix"
    }}}}
  ],
  "quick_wins": ["Up to 3 small changes with noticeable improvement"],
  "summary": "2-3 sentence overall assessment"
}}}}
```

**Priority rules:**
- P0 (blocker): user cannot complete primary task, critical confusion, or broken state
- P1 (important): degrades experience meaningfully, but a workaround exists
- P2 (polish): minor improvements to clarity, spacing, or consistency

Each finding must be specific and actionable. No generic advice.

---
"""
