# Expanded Checklists

Use these when the task needs more detail than the core principles alone.

## Universal States

- Loading:
  - Avoid layout jumps (skeleton/placeholder with stable height)
  - Prevent double-submit; show progress when waiting is noticeable
- Empty:
  - Explain what "empty" means
  - Provide a next step (create/import/change filters)
- Error:
  - Message: what happened + why (if safe) + what to do
  - Preserve user input where possible
- Success:
  - Confirm outcome + provide next action (view, undo, share)
- Permission:
  - Explain why access is blocked + where to request access

## Affordance and Signifiers

- Primary actions look like actions:
  - Use a real primary button; label with a verb (avoid OK/Done).
  - Icon-only is reserved for universally-known actions (search/close/more/settings).
- Links look like links:
  - Ensure a clear link signifier (underline or strong hover/contrast), not color-only subtlety.
- Clickable surfaces communicate clickability:
  - Web: for custom clickable surfaces (non-button/a), use cursor: pointer and a visible focus style.
  - Card/list rows that open should have hover + chevron/affordance cue or a clear "View" action.
  - Do not make plain body text behave like a button.
- Controls match outcomes:
  - Place controls near what they affect; keep directionality intuitive.
  - Group controls with the content they control (filters above list; section actions in section header).

## Lists (table / cards)

- Scannability:
  - One primary column/field; secondary details visually muted
  - Consistent row height and alignment; avoid jagged columns
- Controls:
  - Search/filter/sort appear before the list, not after
  - Selected filters are visible and removable
- Row actions:
  - Keep high-frequency actions visible
  - Hide long-tail actions under a "more" menu (but not the primary action)

## Detail Pages

- Clear page title that matches the object
- Key facts near the top; secondary info below or collapsed
- Actions grouped by intent (primary, secondary, destructive)
- Related items and history: grouped and titled

## Forms (create / edit / config)

- Reduce thinking:
  - Use defaults and reasonable prefill
  - Use presets when choices are complex
- Prevent errors:
  - Inline validation; format hints before submit
  - Do not require users to memorize constraints
- Layout:
  - Group fields by meaning; use headings (not just spacing)
  - Keep labels consistent (position + style) across the product
- Submission:
  - One primary submit action
  - Disabled state and clear error placement

## Settings / Preferences

- Group by mental model (account, security, notifications, integrations, appearance)
- For each setting: clear label + short value explanation only if needed
- Destructive actions separated and clearly labeled

## Motion Checklist

- Purpose: each animation explains hierarchy (panel/overlay) or state change (feedback). If not, remove or downgrade.
- Vocabulary: prefer fade; then small translate+fade; allow tiny scale+fade for overlays. Avoid showy motion.
- Canvas stability: keep the work surface stable. Move panels/overlays, not the core content.
- Responsiveness: interaction feedback (hover/pressed) feels immediate.
- Consistency: same component type uses the same motion pattern.
- Stability: no layout shift/jank during loading or transitions; use skeleton/placeholder to preserve layout.
- Red flags: continuous decorative motion; large bouncy/elastic overshoot; big page-level transitions for routine navigation.

## Dashboards

- Decide the story: what decision should the user make here?
- Keep top KPI set small; avoid wall-of-numbers
- Make time range and filters obvious and persistent
- Provide drill-down paths (click-through) for every key metric

## Copy Rules

- Prefer short labels over helper paragraphs.
- Use helper text only when it:
  - prevents an error
  - clarifies a non-obvious term
  - explains consequences (especially destructive actions)
  - builds trust (privacy, payment, external side effects)
- Replace vague verbs ("Do", "OK") with concrete actions ("Create", "Save", "Publish").
