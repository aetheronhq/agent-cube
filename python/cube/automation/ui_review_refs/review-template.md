# Review Output Template

Use this template for all review outputs. Keep each bullet short and implementable.

## Context

- Surface: (web/app) + page type (list/detail/form/dashboard/settings)
- Primary user task:
- Primary CTA:
- Constraints/assumptions:

## Diagnosis (pick one per major issue)

- Execution gulf: user cannot find *how* to do it (entry/signifier/IA/choices)
- Evaluation gulf: user cannot tell *what happened* (state/feedback/results)
- Slip: goal is correct, execution goes wrong (misclick, fat-finger, wrong target)
- Mistake: mental model is wrong (labels/mapping/conceptual model misleads)

## Findings (prioritized)

### P0 (blocker)

- Problem:
  - Evidence:
  - Diagnosis: execution gulf / evaluation gulf; slip / mistake
  - Why it hurts:
  - Fix (specific, implementable):
  - Acceptance check:

### P1 (important)

- Problem:
  - Evidence:
  - Diagnosis: execution gulf / evaluation gulf; slip / mistake
  - Fix:
  - Acceptance check:

### P2 (polish)

- Problem:
  - Diagnosis: execution gulf / evaluation gulf (optional)
  - Fix:

## Quick Wins (optional)

- 3 small changes that noticeably improve clarity or polish.

## Checklist to Verify

- Task clarity: primary CTA obvious and singular
- IA: groups and headings match mental model
- Feedback: loading/empty/error/success states present and helpful
- Consistency: components and wording stable across screens
- Affordance: clickable elements look clickable; icon-only is rare
- Errors: prevention + recovery + actionable messages
- Cognitive load: defaults and progressive disclosure reduce thinking
- CRAP: hierarchy, alignment, spacing, grouping feel intentional
- Modern minimal: restrained color, spacious layout, minimal copy
- Icons: no emoji; consistent set; labels where ambiguity exists
