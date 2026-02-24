# Interaction Psychology

Compact reference of HCI laws, cognitive biases, and flow principles that directly inform design decisions.

## A) Classic HCI Laws

### Fitts's Law

- Core idea: the time to reach a target is a function of target size and distance. Larger and closer targets are faster and easier to hit.

Practical rules:
- Primary CTA: make it the largest interactive element in its section and place it near the user's visual focus.
- Destructive actions: keep them small and spatially separated from the primary CTA to prevent slips.
- Touch targets: minimum 44x44 CSS px (web) / 48x48 dp (mobile).
- Edges and corners of the viewport are effectively infinite-size targets — use them for key navigation.

Review question: Is the primary action button large enough and close to the user's focus? Are destructive actions physically separated?

### Hick's Law

- Core idea: decision time increases logarithmically with the number of choices. More options means slower decisions and higher abandonment.

Practical rules:
- Limit visible choices: if a list/menu exceeds ~7 items, add grouping, search, or filtering.
- Use smart defaults to eliminate decisions entirely.
- Progressive disclosure: show basic options first, reveal advanced options on demand.
- Avoid paradox of choice in onboarding: guide users through a recommended path.

Review question: Is the user facing too many options at once? Can grouping, search, or defaults reduce the decision burden?

### Miller's Law

- Core idea: working memory holds roughly 7 ± 2 items. Exceeding this limit causes cognitive overload and errors.

Practical rules:
- Navigation / tab bars: keep to 7 or fewer top-level items.
- Long forms: chunk fields into labeled groups (5-7 fields per group).
- Break long lists into scannable sections with headings.
- Do not force users to remember information across screens — carry context forward.

Review question: Does a single screen require the user to hold more than 7 independent pieces of information in mind?

---

## B) Cognitive Biases in UI Design

### Anchoring Effect

- Users are influenced by the first piece of information they see.

Practical rules:
- Form defaults: the pre-filled value becomes the user's baseline — choose it carefully.
- Progress indicators: showing "step 2 of 3" anchors the user's effort expectation.

### Default Effect

- Users disproportionately stick with the default option.

Practical rules:
- Set defaults to the safest and most common choice.
- Never use defaults to trick users into unfavorable choices.
- When there is no safe default, force an explicit choice instead of pre-selecting.

### Peak-End Rule

- Users judge an experience primarily by its most intense moment and its ending.

Practical rules:
- Invest in the completion/success screen — it is the last impression.
- Celebrate meaningful milestones (first project created, first successful deploy).

### Loss Aversion

- The pain of losing something is roughly 2x stronger than the pleasure of gaining the same thing.

Practical rules:
- Destructive actions: frame confirmation around what will be lost, not just the action name.
- Unsaved changes: warn clearly before navigation away; show exactly what will be lost.

### Inattentional Blindness

- When focused on a task, users fail to notice information outside their attention focus.

Practical rules:
- Place critical feedback near the user's point of action (inline validation, not page-top banners).
- Do not rely on peripheral notifications for urgent information during focused tasks.

---

## C) Interaction Flow and Rhythm

### Interruption Cost

- Every interruption (modal, page redirect, loading spinner) has a cognitive recovery cost.

Practical rules:
- Prefer inline interactions over modals; prefer modals over page redirects.
- If a sub-task can be completed in the current context, do not navigate away.
- Batch confirmations: one confirmation for a batch operation, not one per item.

Review question: How many page jumps or modal interruptions does it take to complete the primary task?

### Action Momentum

- Users build rhythm during sequential operations; design should sustain, not break, this rhythm.

Practical rules:
- In batch/sequential workflows, do not require confirmation at every step.
- Tab order between form fields should follow the natural reading/input sequence.

### Reversibility Principle

- Users explore more confidently when they know actions can be undone.

Practical rules:
- Provide undo for common actions (delete, move, edit).
- Non-destructive actions should not require confirmation dialogs.
- For truly irreversible actions, make the consequences explicit and require deliberate confirmation.

---

## D) Attention Economy

### Visual Weight Budget

- A page has a finite attention budget. Emphasizing too many things emphasizes nothing.

Practical rules:
- One visual focal point per screen section (the primary CTA or key metric).
- Secondary information: reduce contrast, size, or weight to create clear hierarchy.
- If everything looks important, re-evaluate: what is the ONE thing the user should do or notice here?

Review question: Close your eyes, then open them — is the first thing you see the most important thing on the page?

### Scanning Patterns

- Users do not read; they scan. Common patterns: F-shape (content pages) and Z-shape (landing pages).

Practical rules:
- Place critical information at the top-left and in headings (F-pattern entry points).
- In data tables, put the most important column on the far left.
- Use visual anchors (bold text, icons, color) to create scan stops at key information.
- Front-load sentences and labels: put the differentiating word first.

Review question: If the user spends only 3 seconds scanning, can they extract the most critical information?
