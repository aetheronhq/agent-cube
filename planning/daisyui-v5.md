# DaisyUI v5 Integration

**Purpose:** Define how to use DaisyUI v5 for UI components in this project.

**Related Docs:**
- `planning/third-party-versions.md` - Version registry
- `planning/tailwindcss-v4.md` - Tailwind CSS v4 patterns

---

## 🎯 Principles

### 1. Use DaisyUI v5 Official Patterns

- **Always use DaisyUI v5 components** (not v4 or earlier)
- **Follow v5 conventions** from official documentation
- **No custom wrapper components** unless absolutely necessary
- **Why:** v5 has breaking changes from v4, maintainability, community support

### 2. Minimal Abstraction

- **Import DaisyUI classes directly** in JSX/HTML
- **Use Tailwind utilities** alongside DaisyUI components
- **No unnecessary abstraction layers**
- **Why:** KISS principle, easier debugging, better documentation alignment

### 3. Semantic Component Usage

- **Use appropriate semantic components** for their intended purpose
- **Don't misuse components** (e.g., using buttons as divs)
- **Follow accessibility guidelines** built into DaisyUI
- **Why:** Accessibility, semantic HTML, better UX

---

## 📋 Requirements

### Installation and Setup

**Must have:**
```bash
npm install daisyui@^5.0.0
```

**Tailwind Configuration (v4 compatible):**
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark", "cupcake"], // Choose your themes
    base: true, // Apply background color and foreground color
    styled: true, // Include DaisyUI colors and design decisions
    utils: true, // Add utility classes
    prefix: "", // Prefix for DaisyUI classnames (empty = no prefix)
    logs: true, // Show logs in terminal when compiling
    themeRoot: ":root", // Root element for theme
  },
}
```

### Usage Patterns

#### ✅ Button Component (Good)

**Example:**
```tsx
// Basic button - v5 syntax
<button className="btn">Button</button>

// Button with variants
<button className="btn btn-primary">Primary</button>
<button className="btn btn-secondary">Secondary</button>
<button className="btn btn-accent">Accent</button>
<button className="btn btn-ghost">Ghost</button>
<button className="btn btn-link">Link</button>

// Button sizes
<button className="btn btn-lg">Large</button>
<button className="btn btn-md">Medium (default)</button>
<button className="btn btn-sm">Small</button>
<button className="btn btn-xs">Extra Small</button>

// Button states
<button className="btn btn-disabled">Disabled</button>
<button className="btn loading">Loading</button>

// Combining with Tailwind utilities
<button className="btn btn-primary w-full mt-4">
  Full Width Button
</button>
```

#### ❌ Button Anti-Pattern (Bad)

```tsx
// DON'T: Create unnecessary wrapper components
const MyCustomButton = ({ children, onClick }) => (
  <button className="btn btn-primary" onClick={onClick}>
    {children}
  </button>
);
// This adds no value, just use btn directly!

// DON'T: Use v4 syntax (outdated)
<button className="btn-primary">Button</button> // Missing "btn" base class

// DON'T: Override DaisyUI styles unnecessarily
<button
  className="btn btn-primary"
  style={{ backgroundColor: 'red' }}  // Don't do this!
>
  Button
</button>
// Use DaisyUI's color system or create custom theme instead
```

---

#### ✅ Card Component (Good)

**Example:**
```tsx
// Basic card
<div className="card bg-base-100 shadow-xl">
  <div className="card-body">
    <h2 className="card-title">Card Title</h2>
    <p>Card content goes here</p>
    <div className="card-actions justify-end">
      <button className="btn btn-primary">Action</button>
    </div>
  </div>
</div>

// Card with image
<div className="card bg-base-100 shadow-xl">
  <figure>
    <img src="/image.jpg" alt="Album" />
  </figure>
  <div className="card-body">
    <h2 className="card-title">Card with Image</h2>
    <p>Description text</p>
    <div className="card-actions justify-end">
      <button className="btn btn-primary">Buy Now</button>
    </div>
  </div>
</div>

// Compact card
<div className="card card-compact bg-base-100 shadow-xl">
  <div className="card-body">
    <h2 className="card-title">Compact Card</h2>
    <p>Less padding</p>
  </div>
</div>
```

#### ❌ Card Anti-Pattern (Bad)

```tsx
// DON'T: Misuse card structure
<div className="card">
  <h2>Title</h2>  // Missing card-title class
  <p>Content</p>
</div>
// Use proper card-body and card-title structure

// DON'T: Create custom card components without good reason
const CustomCard = ({ title, content }) => (
  <div className="my-custom-card">  // Don't reinvent the wheel!
    <h2>{title}</h2>
    <p>{content}</p>
  </div>
);
```

---

#### ✅ Modal Component (Good)

**Example:**
```tsx
// Modal structure (v5)
<dialog id="my_modal" className="modal">
  <div className="modal-box">
    <h3 className="font-bold text-lg">Modal Title</h3>
    <p className="py-4">Modal content goes here</p>
    <div className="modal-action">
      <form method="dialog">
        <button className="btn">Close</button>
      </form>
    </div>
  </div>
</dialog>

// Open modal with button
<button
  className="btn"
  onClick={() => document.getElementById('my_modal').showModal()}
>
  Open Modal
</button>

// Modal with backdrop close
<dialog id="my_modal_2" className="modal modal-bottom sm:modal-middle">
  <div className="modal-box">
    <h3 className="font-bold text-lg">Hello!</h3>
    <p className="py-4">Press ESC or click outside to close</p>
  </div>
  <form method="dialog" className="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
```

#### ❌ Modal Anti-Pattern (Bad)

```tsx
// DON'T: Use v4 modal syntax (outdated)
<input type="checkbox" id="my-modal" className="modal-toggle" />
<div className="modal">
  // v4 structure - don't use!
</div>

// DON'T: Build custom modal from scratch
const CustomModal = ({ isOpen, onClose }) => (
  isOpen && <div className="custom-modal-overlay">
    // Custom implementation - use DaisyUI's <dialog> instead!
  </div>
);
```

---

#### ✅ Form Components (Good)

**Example:**
```tsx
// Input
<input
  type="text"
  placeholder="Type here"
  className="input input-bordered w-full max-w-xs"
/>

// Input with label
<label className="form-control w-full max-w-xs">
  <div className="label">
    <span className="label-text">What is your name?</span>
  </div>
  <input
    type="text"
    placeholder="Type here"
    className="input input-bordered w-full max-w-xs"
  />
  <div className="label">
    <span className="label-text-alt">Alt label</span>
  </div>
</label>

// Select
<select className="select select-bordered w-full max-w-xs">
  <option disabled selected>Pick one</option>
  <option>Option 1</option>
  <option>Option 2</option>
</select>

// Checkbox
<div className="form-control">
  <label className="label cursor-pointer">
    <span className="label-text">Remember me</span>
    <input type="checkbox" className="checkbox" />
  </label>
</div>

// Radio
<div className="form-control">
  <label className="label cursor-pointer">
    <span className="label-text">Option 1</span>
    <input type="radio" name="radio-1" className="radio" />
  </label>
</div>

// Textarea
<textarea
  className="textarea textarea-bordered"
  placeholder="Bio"
></textarea>
```

---

#### ✅ Navigation Components (Good)

**Example:**
```tsx
// Navbar
<div className="navbar bg-base-100">
  <div className="flex-1">
    <a className="btn btn-ghost text-xl">daisyUI</a>
  </div>
  <div className="flex-none">
    <ul className="menu menu-horizontal px-1">
      <li><a>Link</a></li>
      <li>
        <details>
          <summary>Parent</summary>
          <ul className="bg-base-100 rounded-t-none p-2">
            <li><a>Link 1</a></li>
            <li><a>Link 2</a></li>
          </ul>
        </details>
      </li>
    </ul>
  </div>
</div>

// Drawer (sidebar)
<div className="drawer">
  <input id="my-drawer" type="checkbox" className="drawer-toggle" />
  <div className="drawer-content">
    <label htmlFor="my-drawer" className="btn btn-primary drawer-button">
      Open drawer
    </label>
  </div>
  <div className="drawer-side">
    <label htmlFor="my-drawer" aria-label="close sidebar" className="drawer-overlay"></label>
    <ul className="menu bg-base-200 text-base-content min-h-full w-80 p-4">
      <li><a>Sidebar Item 1</a></li>
      <li><a>Sidebar Item 2</a></li>
    </ul>
  </div>
</div>

// Breadcrumbs
<div className="breadcrumbs text-sm">
  <ul>
    <li><a>Home</a></li>
    <li><a>Documents</a></li>
    <li>Add Document</li>
  </ul>
</div>
```

---

#### ✅ Alert & Toast Components (Good)

**Example:**
```tsx
// Alert
<div role="alert" className="alert">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-info h-6 w-6 shrink-0">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
  </svg>
  <span>Info: New software update available.</span>
</div>

// Alert variants
<div role="alert" className="alert alert-info">
  <span>Info alert</span>
</div>
<div role="alert" className="alert alert-success">
  <span>Success alert</span>
</div>
<div role="alert" className="alert alert-warning">
  <span>Warning alert</span>
</div>
<div role="alert" className="alert alert-error">
  <span>Error alert</span>
</div>

// Toast (position with Tailwind utilities)
<div className="toast toast-top toast-end">
  <div className="alert alert-info">
    <span>New message arrived.</span>
  </div>
</div>
```

---

## 🚫 Anti-Patterns

### ❌ Don't: Use v4 Syntax

**Problem:**
- v5 has breaking changes from v4
- v4 syntax may not work or behave unexpectedly
- Mixes old and new patterns causing confusion

**Instead:**
```tsx
// Bad (v4)
<input type="checkbox" id="my-modal" className="modal-toggle" />

// Good (v5)
<dialog id="my_modal" className="modal">
```

---

### ❌ Don't: Override DaisyUI Styles with Inline Styles

**Problem:**
- Breaks theme consistency
- Makes theming difficult
- Loses dark mode support
- Hard to maintain

**Instead:**
```tsx
// Bad
<button
  className="btn"
  style={{ backgroundColor: 'red', padding: '20px' }}
>
  Button
</button>

// Good - use DaisyUI modifiers and Tailwind utilities
<button className="btn btn-error btn-lg">
  Button
</button>

// Or create custom theme color if needed
```

---

### ❌ Don't: Create Unnecessary Wrapper Components

**Problem:**
- Adds abstraction layer with no value
- Makes debugging harder
- Breaks from DaisyUI documentation
- YAGNI violation

**Instead:**
```tsx
// Bad
const MyButton = ({ children, onClick }) => (
  <button className="btn btn-primary" onClick={onClick}>
    {children}
  </button>
);

// Good - use DaisyUI directly
<button className="btn btn-primary" onClick={handleClick}>
  Click Me
</button>

// Only create wrapper if there's ACTUAL shared logic:
const ConfirmButton = ({ onConfirm, message, children }) => {
  const handleClick = () => {
    if (window.confirm(message)) {
      onConfirm();
    }
  };
  return (
    <button className="btn btn-warning" onClick={handleClick}>
      {children}
    </button>
  );
};
```

---

### ❌ Don't: Mix Multiple UI Libraries

**Problem:**
- Inconsistent design language
- Bloated bundle size
- Conflicting styles
- Harder maintenance

**Instead:**
```tsx
// Bad - mixing DaisyUI and Material-UI
import Button from '@mui/material/Button';
<Button>MUI Button</Button>
<button className="btn">DaisyUI Button</button>

// Good - use DaisyUI consistently
<button className="btn">Button 1</button>
<button className="btn btn-primary">Button 2</button>
```

---

## 🔗 Integration Points

### With Tailwind CSS v4

**Connection:** DaisyUI is a Tailwind plugin, all Tailwind utilities work alongside DaisyUI classes.

**Example:**
```tsx
<button className="btn btn-primary mt-4 shadow-lg hover:shadow-xl">
  {/* DaisyUI: btn, btn-primary */}
  {/* Tailwind: mt-4, shadow-lg, hover:shadow-xl */}
  Combined Button
</button>
```

**Planning docs to read together:**
- `planning/tailwindcss-v4.md` - Tailwind v4 patterns

---

### With React State

**Connection:** DaisyUI components work naturally with React state.

**Example:**
```tsx
// Modal with React state
const [isOpen, setIsOpen] = useState(false);

<dialog id="my_modal" className="modal" open={isOpen}>
  <div className="modal-box">
    <h3>Modal Title</h3>
    <button
      className="btn"
      onClick={() => setIsOpen(false)}
    >
      Close
    </button>
  </div>
</dialog>

<button className="btn" onClick={() => setIsOpen(true)}>
  Open Modal
</button>
```

---

### With Forms

**Connection:** Use DaisyUI form components with form libraries or native form handling.

**Example:**
```tsx
// With React Hook Form
import { useForm } from 'react-hook-form';

function MyForm() {
  const { register, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <label className="form-control">
        <div className="label">
          <span className="label-text">Your email</span>
        </div>
        <input
          type="email"
          {...register('email')}
          className="input input-bordered"
        />
      </label>
      <button type="submit" className="btn btn-primary mt-4">
        Submit
      </button>
    </form>
  );
}
```

---

## 📚 References

### External Documentation (MANDATORY READING)

**Primary:**
- **DaisyUI v5 Official Docs:** https://daisyui.com/docs/
  - **Read first** - Overview and getting started

- **Components Reference:** https://daisyui.com/components/
  - **Essential** - Complete component list with examples

- **Themes Documentation:** https://daisyui.com/docs/themes/
  - **Important** - How to use and customize themes

**Migration & Changes:**
- **v4 → v5 Changelog:** https://daisyui.com/docs/changelog/
  - **Critical** - Breaking changes and new features

**Advanced:**
- **Customization Guide:** https://daisyui.com/docs/customize/
  - Theming and style customization

- **Config Reference:** https://daisyui.com/docs/config/
  - All configuration options

### Component Quick Reference

**Most Used Components:**
- Buttons: https://daisyui.com/components/button/
- Cards: https://daisyui.com/components/card/
- Modals: https://daisyui.com/components/modal/
- Forms: https://daisyui.com/components/input/
- Navbar: https://daisyui.com/components/navbar/
- Alerts: https://daisyui.com/components/alert/

**Keep these tabs open during implementation!**

---

## ✅ Checklist for Implementation

Before implementing UI with DaisyUI:

- [ ] Read DaisyUI v5 documentation for components you'll use
- [ ] Check component examples from official docs
- [ ] Verify you're using v5 syntax (not v4)
- [ ] Use DaisyUI classes directly (no unnecessary wrappers)
- [ ] Combine with Tailwind utilities for spacing/sizing
- [ ] Test with light and dark themes
- [ ] Verify accessibility (screen readers, keyboard navigation)
- [ ] Check responsive behavior on mobile

---

## ❓ Open Questions / TBD

### Should we create a custom theme?

- **Status:** TBD
- **Owner:** Design Team
- **Due:** Before UI implementation
- **Default:** Use built-in "light" and "dark" themes until custom theme is designed

### Do we need all DaisyUI components?

- **Status:** No - use only what's needed
- **Approach:** Import components as needed, don't bloat bundle
- **Monitor:** Bundle size with each addition

---

## 📝 Notes

- **v5 uses native `<dialog>` element** for modals (modern and accessible)
- **DaisyUI is theme-agnostic** - works with any Tailwind theme
- **All components are responsive** by default
- **Dark mode is built-in** via data-theme attribute
- **No JavaScript required** for most components (pure CSS)

---

**Last Updated:** 2025-01-21

**Version:** DaisyUI v5.0.0
