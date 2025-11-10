# Task 06: Decision Review Interface

**Goal:** Beautiful UI for viewing and understanding judge decisions

## Context

Judges file JSON decisions. This task makes them human-readable and actionable.

## Requirements

### 1. Decision Cards

**Panel Decision:**
```tsx
<DecisionCard
  judge={1}
  decision="APPROVED"
  winner="B"
  scores={{
    writerA: {kiss: 7, architecture: 8, total: 7.8},
    writerB: {kiss: 9, architecture: 9, total: 9.2}
  }}
  blockers={["Circuit breaker timeout missing"]}
  recommendation="Writer B has better architecture"
/>
```

**Visual:**
- Judge avatar/number
- Decision badge (green=APPROVED, yellow=REQUEST_CHANGES)
- Score comparison (A vs B bars)
- Blocker list (if any)
- Expandable recommendation

### 2. Aggregate View

```
┌──────────────────────────────────────┐
│ Panel Results                        │
├──────────────────────────────────────┤
│ Consensus: ✅ APPROVED (2/3)         │
│ Winner: Writer B (Codex)             │
│ Average: A=7.2, B=8.9                │
│                                      │
│ ┌─ Judge 1 ─┐ ┌─ Judge 2 ─┐ ┌─────┐ │
│ │ ✅ APPROVED│ │ ✅ APPROVED│ │ ⚠️  │ │
│ │ Winner: B  │ │ Winner: B  │ │ ... │ │
│ │ 7.8 → 9.2  │ │ 6.5 → 8.8  │ └─────┘ │
│ └───────────┘ └───────────┘         │
│                                      │
│ Next Action: SYNTHESIS               │
│ 3 blockers found → [View Details]    │
└──────────────────────────────────────┘
```

### 3. Comparison View

Side-by-side judge opinions:
- What Judge 1 liked about A vs B
- What Judge 2 disliked about A vs B
- Consensus points
- Disagreements highlighted

### 4. Blocker Tracking

- List all blockers from all judges
- Group by writer
- Show which judge flagged each
- Link to synthesis prompt

## Deliverables

- [ ] Decision card component
- [ ] Aggregate results view
- [ ] Score visualization (bars/charts)
- [ ] Blocker list with grouping
- [ ] Expandable judge details
- [ ] Both panel and peer-review views
- [ ] Navigate between views
- [ ] Export decisions as PDF (nice-to-have)

## Architecture Constraints

**Data Loading:**
```tsx
const { panel, peer } = useDecisions(taskId)

// Loads from:
// GET /api/workflows/{id}/decisions/panel
// GET /api/workflows/{id}/decisions/peer
```

**Visual Design:**
- ✅ Score bars (A vs B comparison)
- ✅ Color-coded decisions
- ✅ Badges for consensus
- ❌ No complex charts (keep simple)

## Styling

Use Tailwind + Headless UI:
- Cards with hover states
- Disclosure for expandable sections
- Badges for decisions
- Progress bars for scores

## Acceptance Criteria

1. Shows all 3 judge decisions
2. Aggregate results clear
3. Scores visualized well
4. Blockers easy to find
5. Can switch panel ↔ peer review
6. Responsive layout
7. Looks professional

## Time Estimate

4-5 hours

