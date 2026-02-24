# Icon Rules

## Hard Rules

- Do not use emoji as icons or decoration.
- Use one icon family across the product. Do not mix outlined/filled/3D/emoji styles.
- Prefer obvious meanings over clever metaphors. If an icon can be misunderstood, add a text label.

## Intuitive and Refined Checklist

- Style consistency: same stroke weight (outline) or same fill style (filled).
- Sizes: standardize on 16/20/24 (or your system sizes); avoid random sizes per screen.
- Optical alignment: align visually (icon bounding boxes lie; nudge when needed).
- Touch targets: icon buttons still need adequate hit area; do not shrink interactive area to the glyph.
- Labels: primary actions should be text or text+icon; icon-only is reserved for universally-known actions.
- Tooltips: tooltips are support, not the primary way to understand an action.

## Prefer Text Over Icons When

- The action is uncommon in your product.
- The icon is domain-specific (users will not share the same mental model).
- The action is destructive or high-stakes (use explicit wording).

## Suggested Icon Sets (pick one; do not mix)

- Lucide / Feather-style outline icons (web-friendly)
- Material Symbols (outlined or rounded; pick one)
- SF Symbols (Apple platforms)

## Common Mappings

- Search: magnifier
- Filter: funnel
- Settings: gear
- More actions: kebab (vertical three dots)
- Close: x
- Back: left arrow
- Info: i in circle (use sparingly)

If an icon is not instantly clear, prefer a short label instead of inventing a new icon metaphor.
