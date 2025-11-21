# Task 03: Build User Dashboard UI with DaisyUI

**Goal:** Create a responsive user dashboard interface using DaisyUI v5 components and Tailwind v4 utilities.

**Time Estimate:** 4-6 hours

---

## 📖 **Context**

**What this builds on:**
- Existing authentication system (Task 01)
- User data API endpoints (Task 02)
- This task delivers the frontend dashboard UI

**Planning docs (Golden Source):**
- `planning/daisyui-v5.md` [KEY] - DaisyUI v5 component patterns and usage
- `planning/tailwindcss-v4.md` [KEY] - Tailwind v4 styling conventions
- `planning/third-party-versions.md` - Required versions for all tools
- `planning/web-ui.md` - General web UI architecture

**Note:** Docs marked with `[KEY]` will be automatically included in writer prompts by the orchestrator. Reference-only docs are available but not included by default.

---

## 📚 **Required Reading** (MANDATORY)

**BEFORE implementing, you MUST read these external documentation sources:**

### DaisyUI v5

**Documentation:**
- **Primary Docs:** https://daisyui.com/docs/
  - **Why:** We use v5, NOT v4 - v5 has breaking changes in modal and form components
  - **Time:** 15 minutes

**Sections to read:**
- **Components Reference:** https://daisyui.com/components/
  - **Focus on:** Button, Card, Navbar, Modal, Alert components (we'll use all of these)
- **Card Component:** https://daisyui.com/components/card/
  - **Focus on:** Card structure, card-body, card-title, card-actions
- **Modal Component:** https://daisyui.com/components/modal/
  - **Focus on:** v5 uses native `<dialog>` element (NOT v4 checkbox pattern)
- **v4 → v5 Migration:** https://daisyui.com/docs/changelog/
  - **Focus on:** Breaking changes section

### Tailwind CSS v4

**Documentation:**
- **Primary Docs:** https://tailwindcss.com/docs
  - **Why:** v4 uses CSS-first configuration with @theme directive (NOT JavaScript config)
  - **Time:** 10 minutes

**Sections to read:**
- **Flexbox & Grid:** https://tailwindcss.com/docs/flex
  - **Focus on:** Layout utilities for dashboard grid
- **Responsive Design:** https://tailwindcss.com/docs/responsive-design
  - **Focus on:** Mobile-first approach (we support mobile, tablet, desktop)
- **Configuration (v4):** https://tailwindcss.com/docs/configuration
  - **Focus on:** Using @theme directive in CSS files

**Critical:** Don't skip these docs! Judges will verify you:
- ✅ Used DaisyUI v5 syntax (not v4)
- ✅ Used Tailwind v4 patterns (not v3 JavaScript config)
- ✅ Followed documented component structures
- ✅ Avoided deprecated APIs

---

## ✅ **Requirements**

### **1. Dashboard Layout**

**Deliverable:**
- Responsive grid layout with sidebar and main content area
- Mobile: Single column (sidebar collapses to drawer)
- Tablet/Desktop: Sidebar + content side by side

**Acceptance criteria:**
- [ ] Uses DaisyUI drawer component for mobile sidebar
- [ ] Uses Tailwind grid utilities for desktop layout
- [ ] Responsive breakpoints: mobile (default), tablet (md:), desktop (lg:)
- [ ] Sidebar navigation uses DaisyUI navbar component

### **2. Dashboard Cards**

**Deliverable:**
- Stats cards showing user metrics (followers, posts, likes)
- Activity feed card with recent actions
- Quick actions card with common tasks

**Acceptance criteria:**
- [ ] Uses DaisyUI card component with proper structure (card-body, card-title, card-actions)
- [ ] Cards are responsive (stack on mobile, grid on desktop)
- [ ] Stats display with appropriate typography and spacing
- [ ] Cards use DaisyUI theme colors (bg-base-100, text-base-content, etc.)

### **3. Interactive Elements**

**Deliverable:**
- Edit profile modal (triggered by button)
- Quick action buttons with hover states
- Alert notifications for user actions

**Acceptance criteria:**
- [ ] Modal uses DaisyUI v5 `<dialog>` element (NOT v4 checkbox pattern)
- [ ] Buttons use DaisyUI button variants (btn-primary, btn-secondary, etc.)
- [ ] Alerts use DaisyUI alert component with appropriate variants
- [ ] All interactive elements have proper hover/focus states

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Setup & Verification**
   - [ ] Verify DaisyUI v5 and Tailwind v4 are installed
   - [ ] Read required documentation (links above)
   - [ ] Check `planning/third-party-versions.md` for exact versions

2. **Dashboard Layout Structure**
   - [ ] Create responsive container with Tailwind utilities
   - [ ] Implement mobile drawer using DaisyUI drawer component
   - [ ] Implement desktop sidebar layout with Tailwind grid
   - [ ] Add navigation items to sidebar

3. **Stats Cards**
   - [ ] Create card component structure per DaisyUI v5 docs
   - [ ] Add stats content (followers, posts, likes)
   - [ ] Style with DaisyUI card utilities and Tailwind spacing
   - [ ] Make responsive (stack on mobile, grid on desktop)

4. **Activity Feed Card**
   - [ ] Create card with scrollable content area
   - [ ] Add list of recent activities
   - [ ] Style timestamps and action descriptions

5. **Quick Actions Card**
   - [ ] Add action buttons using DaisyUI button component
   - [ ] Implement hover states per Tailwind docs
   - [ ] Connect to edit profile modal trigger

6. **Edit Profile Modal**
   - [ ] Create modal using DaisyUI v5 `<dialog>` syntax
   - [ ] Add form inputs (DaisyUI input components)
   - [ ] Implement open/close logic
   - [ ] Add form validation feedback with alerts

7. **Verify**
   - [ ] Test on mobile viewport (320px - 640px)
   - [ ] Test on tablet viewport (768px - 1024px)
   - [ ] Test on desktop viewport (1280px+)
   - [ ] Verify all DaisyUI components match v5 docs
   - [ ] Verify no v4 patterns used
   - [ ] Check theme switching works (light/dark)
   - [ ] Run linter
   - [ ] Run build

8. **Finalize**
   - [ ] Commit changes with descriptive message
   - [ ] Push to branch
   - [ ] Verify push succeeded with `git status`

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Use DaisyUI v5 components per `planning/daisyui-v5.md`
- Use Tailwind v4 utilities per `planning/tailwindcss-v4.md`
- Follow responsive patterns from `planning/web-ui.md`

**Technical constraints:**
- DaisyUI version: `^5.0.0` (NOT v4)
- Tailwind CSS version: `^4.0.0` (NOT v3)
- TypeScript strict mode
- React functional components with hooks

**Required versions:**
```json
{
  "daisyui": "^5.0.0",
  "tailwindcss": "^4.0.0"
}
```

**Required imports:**
```tsx
// Use DaisyUI classes directly in JSX
// No custom wrappers unless necessary
```

**KISS Principles:**
- ✅ Use DaisyUI components directly (no unnecessary wrappers)
- ✅ Use Tailwind utilities for spacing/layout
- ✅ Simplest solution that meets requirements
- ❌ No custom CSS classes when Tailwind/DaisyUI exists
- ❌ No "for future flexibility" abstractions

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Use DaisyUI v4 Modal Syntax**

**Bad (v4 syntax):**
```tsx
// DON'T use v4 modal with checkbox toggle
<input type="checkbox" id="my-modal" className="modal-toggle" />
<div className="modal">
  <div className="modal-box">
    <h3>Modal Title</h3>
  </div>
</div>
```

**Instead (v5 syntax):**
```tsx
// Use v5 modal with <dialog> element
<dialog id="my_modal" className="modal">
  <div className="modal-box">
    <h3 className="font-bold text-lg">Modal Title</h3>
    <div className="modal-action">
      <form method="dialog">
        <button className="btn">Close</button>
      </form>
    </div>
  </div>
</dialog>

// Open with:
<button onClick={() => document.getElementById('my_modal').showModal()}>
  Open Modal
</button>
```

**Why:** v5 uses native HTML `<dialog>` for better accessibility and browser support.

---

### **❌ DON'T: Use Tailwind v3 JavaScript Config**

**Bad (v3 style):**
```javascript
// tailwind.config.js - DON'T use JavaScript config
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
      },
    },
  },
}
```

**Instead (v4 style):**
```css
/* src/styles/theme.css - Use CSS @theme directive */
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.7 0.2 250);
}
```

**Why:** Tailwind v4 uses CSS-first configuration for better performance and type safety.

---

### **❌ DON'T: Create Unnecessary Component Wrappers**

**Bad:**
```tsx
// DON'T create wrapper for simple DaisyUI components
const MyCard = ({ title, children }) => (
  <div className="card bg-base-100 shadow-xl">
    <div className="card-body">
      <h2 className="card-title">{title}</h2>
      {children}
    </div>
  </div>
);
```

**Instead:**
```tsx
// Use DaisyUI directly in your component
function Dashboard() {
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">Stats</h2>
        <p>Content here</p>
      </div>
    </div>
  );
}
```

**Why:** KISS principle - don't add abstraction layers without clear value.

---

## 📂 **Owned Paths**

**This task owns:**
```
src/components/Dashboard/
├── Dashboard.tsx
├── DashboardLayout.tsx
├── StatsCard.tsx
├── ActivityFeed.tsx
├── QuickActions.tsx
└── EditProfileModal.tsx
```

**Must NOT modify:**
- `src/App.tsx` (routing owned by integrator)
- `src/styles/theme.css` (unless adding theme variables)
- `tailwind.config.js` (unless coordinating with team)

**Integration:**
- Export Dashboard component from `Dashboard/index.ts`
- Integrator will import and add to routing in separate task

---

## 🧪 **Testing Requirements**

**Test coverage:**
- [ ] Visual regression tests for dashboard layout
- [ ] Responsive behavior tests (mobile, tablet, desktop)
- [ ] Modal open/close interaction tests
- [ ] Theme switching tests (light/dark mode)

**Test quality:**
- Use React Testing Library
- Test user interactions (button clicks, modal opens)
- Verify correct DaisyUI classes are applied
- No snapshot tests (too brittle for UI)

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] All requirements met
- [ ] Used DaisyUI v5 syntax (verified against docs)
- [ ] Used Tailwind v4 patterns (verified against docs)
- [ ] No v4 DaisyUI patterns (e.g., checkbox modal toggle)
- [ ] No v3 Tailwind patterns (e.g., JavaScript config)
- [ ] Responsive on mobile, tablet, desktop
- [ ] Theme switching works (light/dark)
- [ ] Tests written and passing
- [ ] TypeScript compiles (no errors)
- [ ] Linter passes (no warnings)
- [ ] Build succeeds
- [ ] Changes committed and pushed

**Quality gates:**
- [ ] Follows KISS principles (no unnecessary wrappers)
- [ ] Uses DaisyUI directly per planning docs
- [ ] Combines Tailwind utilities appropriately
- [ ] Code is self-documenting
- [ ] No security issues (XSS, injection)

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- Task 01: Authentication system (for user context)
- Task 02: User data API (for fetching stats)

**Dependents (these will use this):**
- Task 04: Settings page (will reuse modal pattern)
- Task 05: Profile page (will reuse card components)

**Integrator task:**
- Task 06: Main app routing integration
- Integrator will import Dashboard and add route

---

## 📊 **Examples**

### **Success Example: DaisyUI v5 Card**

**From:** DaisyUI official docs

**What makes it good:**
- Uses proper card structure (card-body, card-title, card-actions)
- Combines DaisyUI classes with Tailwind utilities
- Responsive and theme-aware
- No custom CSS or wrappers

**Code snippet:**
```tsx
<div className="card bg-base-100 shadow-xl w-96">
  <div className="card-body">
    <h2 className="card-title">User Stats</h2>
    <div className="stats stats-vertical">
      <div className="stat">
        <div className="stat-title">Followers</div>
        <div className="stat-value">1,234</div>
      </div>
    </div>
    <div className="card-actions justify-end">
      <button className="btn btn-primary">View Details</button>
    </div>
  </div>
</div>
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ **Using v4 modal syntax** - v5 uses `<dialog>`, not checkbox toggle
- ⚠️ **Using v3 Tailwind config** - v4 uses CSS @theme, not tailwind.config.js
- ⚠️ **Creating wrapper components** - use DaisyUI directly unless clear value
- ⚠️ **Inline styles** - use Tailwind utilities instead
- ⚠️ **Arbitrary values** - prefer Tailwind's spacing scale (p-4, not p-[16px])
- ⚠️ **Missing responsive breakpoints** - test mobile-first, add md: and lg: variants

**If you see [X], it means [Y] - fix by [Z]:**
- **modal-toggle class** → You're using v4 syntax → Switch to `<dialog>` element
- **tailwind.config.js theme.extend** → v3 syntax → Move to @theme in CSS file
- **Custom component wrapper** → Unnecessary abstraction → Use DaisyUI directly

---

## 📝 **Notes**

**Additional context:**
- DaisyUI v5 has breaking changes from v4 - READ THE DOCS
- Tailwind v4 uses CSS-first configuration - different from v3
- All components should work in light and dark themes
- Test theme switching before committing

**Nice-to-haves (not required):**
- Skeleton loading states for async data
- Animations for modal open/close
- Keyboard shortcuts for quick actions

---

**FINAL STEPS - CRITICAL:**

After completing implementation and verifying all tests pass:

```bash
# Stage your changes
git add src/components/Dashboard/

# Commit with descriptive message
git commit -m "feat: add user dashboard UI with DaisyUI v5 and Tailwind v4

- Implement responsive dashboard layout with sidebar
- Add stats cards, activity feed, and quick actions
- Create edit profile modal using v5 dialog element
- Use Tailwind v4 utilities for styling
- Ensure mobile, tablet, and desktop responsive
- Support light/dark theme switching"

# Push to remote
git push origin writer-[your-model-slug]/task-03

# Verify push succeeded
git status  # Should show "up to date with origin"
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v2.0
**Template version:** 2.0
**Last updated:** 2025-01-21

**Required Tool Versions:**
- DaisyUI: v5.0.0
- Tailwind CSS: v4.0.0
- React: v18.0.0
