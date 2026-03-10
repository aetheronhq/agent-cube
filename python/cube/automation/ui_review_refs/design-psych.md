# Design Psychology

Compact reference for explaining *why* a design is confusing and how to fix it.

## Affordances

- An affordance is what an object *allows* a person to do.
- In UI, you mostly manage **perceived affordances**: what people *think* they can do.

Practical rule:
- If an action is important, it must be discoverable without hover, tooltips, or prior training.

## Signifiers

- Signifiers are the cues that indicate possible actions.
- Examples in UI: button shape, link styling, icons + labels, hover/focus states, cursor changes, microcopy.

Practical rule:
- Use the smallest signifier that removes ambiguity. Default to labels for non-obvious actions.

## Mapping

- Mapping is the relationship between controls and their effects.
- Natural mapping means the layout/relationship mirrors the real-world mental model.

Practical rules:
- Put controls near what they control.
- Use spatial grouping to show what belongs together.
- For multi-part objects, align actions with the part they affect (per-item actions next to the item).

## Constraints

- Constraints limit possible actions, preventing errors and reducing thinking.
- Types: logical constraints (only valid combinations allowed), semantic constraints (meaning-based limits), cultural constraints (conventions users expect).

Practical rules:
- Prefer constraints + defaults over warnings.
- If you must block an action, explain the requirement and provide a path to satisfy it.

## Conceptual Model

- Users form an internal model of how the system works.
- Your UI should make the correct model obvious.

Practical rules:
- Use consistent nouns/labels for objects.
- Use consistent verbs for actions.
- Show cause-effect clearly: do X → see Y change.

## Feedback

- Feedback tells people what happened after an action.

Practical rules:
- Always provide immediate feedback for interaction (press/hover/loading).
- If an operation takes time, show progress or a clear waiting state.
- After success/failure, clearly state the outcome and the next step.

## Gulf of Execution and Gulf of Evaluation

- Execution gulf: user cannot figure out how to do what they want.
- Evaluation gulf: user cannot tell what happened or what state the system is in.

Practical diagnostic:
- If users hesitate before acting: reduce execution gulf (clear CTA, clearer signifiers, simpler choices).
- If users repeat actions / rage-click: reduce evaluation gulf (loading, disabled, progress, clearer results).

## Slips vs Mistakes

- Slip: the goal is correct, the action execution goes wrong (fat-finger, wrong click).
- Mistake: the mental model/goal is wrong (user thinks it works differently).

Practical rules:
- Slips: add undo, confirmations for destructive actions, safer hit targets, better spacing.
- Mistakes: fix labeling, mapping, and conceptual model; add just-enough explanation.

## Knowledge in the World vs in the Head

- Good design puts knowledge in the world: visible options, clear labels, previews, examples.

Practical rule:
- Do not force users to remember constraints. Surface them at the point of decision.

## Modes and Mode Errors

- Modes mean the same action produces different results depending on state.

Practical rule:
- Avoid modes; if unavoidable, make mode state extremely visible and easy to exit.
