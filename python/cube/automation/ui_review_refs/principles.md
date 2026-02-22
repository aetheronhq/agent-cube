# UI/UX Review Principles

Keep outputs concise. Prefer bullets, not long paragraphs.

## Non-negotiables (hard rules)

- No emoji used as icons or UI decoration. If an emoji appears, replace it with a proper icon.
- Icons must be intuitive and refined. Use a single consistent icon set for the product.
- Minimize copy by default. Add explanatory text only when it prevents errors, reduces ambiguity, or improves trust.

## System-Level Guiding Principles

Apply these as first-order constraints before choosing components or page patterns.

Key principles: concept constancy · primary task focus · UI copy source discipline · state perceptibility · help text layering (L0-L3) · feedback loop closure · prevention + recoverability · progressive complexity · action perceptibility · cognitive load budget · evolution with semantic continuity.

## Core Principles

### A) Task-first UX

- Make the primary task obvious in under 3 seconds.
- Allow exactly one primary CTA per screen/section.
- Optimize the happy path; hide advanced controls behind progressive disclosure.

### B) Information architecture

- Group by user mental model (goal/object/time/status), not by backend fields.
- Use clear section titles; keep navigation patterns stable across similar screens.
- When item count grows: add search/filter/sort early, not late.

### C) Feedback and system status

- Cover all states: loading, empty, error, success, permission.
- After any action, answer: "did it work?" + "what changed?" + "what can I do next?"
- Prefer inline, contextual feedback over global toasts (except for cross-page actions).

### D) Consistency and predictability

- Same interaction = same component + same wording + same placement.
- Use a small, stable set of component variants; avoid one-off styles.

### E) Affordance and signifiers

- Clickable things must look clickable (button/link styling + hover/focus + cursor).
- Primary actions need a label; icon-only is reserved for universally-known actions.
- Show constraints before submit (format, units, required), not only after errors.

### F) Error prevention and recovery

- Prevent errors with constraints, defaults, and inline validation.
- Make destructive actions reversible when possible; otherwise require deliberate confirmation.
- Error messages must be actionable (what happened + how to fix).

### G) Cognitive load control

- Reduce choices: sensible defaults, presets, and progressive disclosure.
- Break long tasks into steps only when it reduces thinking.
- Keep visual noise low: fewer borders, fewer colors, fewer competing highlights.

### H) CRAP — visual hierarchy and layout

- Contrast: emphasize the few things that matter (CTA, current state, key numbers).
- Repetition: tokens/components/spacing follow a scale; avoid "almost the same" styles.
- Alignment: align to a clear grid; fix 2px drift; align baselines where text matters.
- Proximity: tight within a group, loose between groups; spacing is the primary grouping tool.

## Spacing and Layout Discipline

- Base unit: 4px. Allowed spacing set: 4 / 8 / 12 / 16 / 24 / 32 / 40 / 48.
- Same component type keeps the same internal spacing (cards, list rows, form groups, section blocks).
- Align to one grid and fix 1-2px drift. Tight spacing within a group, looser between groups.
- Extra wrappers must add real function (grouping, state, scroll, affordance). If a wrapper only adds border/background, remove it and group with spacing instead.
- Quick review pass: any off-scale spacing? any baseline misalignment? any removable wrapper layer?

## Modern Minimal Style

- Use whitespace and typography to create hierarchy; avoid decoration-first design.
- Prefer subtle surfaces (light elevation, low-contrast borders). Avoid heavy shadows.
- Keep color palette small; use one accent color for primary actions and key states.
- Copy: short, direct labels; add helper text only when it reduces mistakes or increases trust.

## Motion Guidance

- Motion explains hierarchy (what is a layer/panel) and state change (what just happened). Avoid motion as decoration.
- Default motion vocabulary: fade; then small translate+fade; allow tiny scale+fade for overlays.
- Keep the canvas/content area stable. Panels/overlays can move; the work surface should not.
- Same component type uses the same motion pattern. Avoid layout jumps; use placeholders/skeletons.

## Anti-AI Self-Check

Before finalizing any generated UI, verify these. Violating any one is a mandatory fix.

- Gradient restraint: purely decorative gradients at most one per page. If background, buttons, and borders all use gradients simultaneously, that is overuse.
- No emoji as UI: no emoji slipped in as section icons, status indicators, or button labels.
- Copy necessity: for every piece of text, ask — if I remove this, can the user still understand through layout, icons, and position alone? If yes, remove it.
- Decoration justification: every purely visual effect must answer "what does this help the user understand?" No answer means remove it.
