# Tailwind CSS v4 Integration

**Purpose:** Define how to use Tailwind CSS v4 for styling in this project.

**Related Docs:**
- `planning/third-party-versions.md` - Version registry
- `planning/daisyui-v5.md` - DaisyUI v5 component patterns

---

## 🎯 Principles

### 1. Use Tailwind v4 CSS-First Configuration

- **Use `@theme` directive** for configuration (not JavaScript config)
- **Leverage CSS variables** for customization
- **Follow v4 conventions** from official documentation
- **Why:** v4's CSS-first approach is more performant, type-safe, and maintainable

### 2. Utility-First Approach

- **Prefer utility classes** over custom CSS
- **Use Tailwind's design system** (spacing, colors, typography)
- **Compose utilities** rather than writing custom styles
- **Why:** Consistency, maintainability, smaller CSS bundle

### 3. Mobile-First Responsive Design

- **Write mobile styles first** (no breakpoint)
- **Add larger breakpoints** progressively (sm:, md:, lg:, xl:, 2xl:)
- **Test on mobile devices** throughout development
- **Why:** Better mobile experience, progressive enhancement

---

## 📋 Requirements

### Installation and Setup

**Must have:**
```bash
npm install tailwindcss@^4.0.0
```

**v4 CSS-First Configuration:**

**File: `src/styles/theme.css`**
```css
@import "tailwindcss";

/* v4 uses @theme directive for configuration */
@theme {
  /* Custom Colors */
  --color-primary: oklch(0.7 0.2 250);
  --color-secondary: oklch(0.6 0.15 300);
  --color-accent: oklch(0.65 0.25 180);

  /* Custom Fonts */
  --font-family-sans: "Inter", system-ui, -apple-system, sans-serif;
  --font-family-mono: "Fira Code", "Consolas", monospace;

  /* Custom Spacing (if needed) */
  --spacing-128: 32rem;

  /* Custom Breakpoints (if needed) */
  --breakpoint-3xl: 1920px;
}

/* Global styles */
@layer base {
  body {
    @apply font-sans text-base-content bg-base-100;
  }

  h1 {
    @apply text-4xl font-bold;
  }

  h2 {
    @apply text-3xl font-semibold;
  }

  h3 {
    @apply text-2xl font-semibold;
  }
}

/* Custom utilities (if needed) */
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

**File: `src/main.tsx` or `src/index.tsx`**
```tsx
import './styles/theme.css';  // Import Tailwind CSS
```

**PostCSS Configuration (if needed):**

**File: `postcss.config.js`**
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

---

## 📝 Usage Patterns

### ✅ Layout & Spacing (Good)

**Example:**
```tsx
// Flexbox layout
<div className="flex items-center justify-between gap-4 p-4">
  <div>Left content</div>
  <div>Right content</div>
</div>

// Grid layout
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

// Container with max width
<div className="container mx-auto px-4 max-w-7xl">
  <h1>Content</h1>
</div>

// Responsive spacing
<div className="p-4 md:p-6 lg:p-8">
  <p className="mb-4">Paragraph 1</p>
  <p>Paragraph 2</p>
</div>
```

### ❌ Layout Anti-Patterns (Bad)

```tsx
// DON'T: Use inline styles instead of Tailwind
<div style={{ display: 'flex', padding: '16px' }}>
  Content
</div>

// DON'T: Create custom CSS classes for simple layouts
// styles.css
.my-flex-container {
  display: flex;
  padding: 1rem;
}
// Just use: className="flex p-4"

// DON'T: Use px values when Tailwind spacing exists
<div className="p-[16px]">  // Use p-4 instead
  Content
</div>
```

---

### ✅ Colors & Theming (Good)

**Example:**
```tsx
// Using semantic color classes
<div className="bg-primary text-primary-content">
  Primary colored div
</div>

<button className="bg-accent text-accent-content hover:bg-accent-focus">
  Accent button
</button>

// Using Tailwind default colors
<div className="bg-blue-500 text-white">
  Blue background
</div>

// Dark mode support (with DaisyUI data-theme)
<div className="bg-base-100 text-base-content">
  Adapts to theme
</div>

// Custom color from theme
<div className="text-[color:var(--color-primary)]">
  Custom themed color
</div>
```

### ❌ Color Anti-Patterns (Bad)

```tsx
// DON'T: Use inline styles for colors
<div style={{ backgroundColor: '#3b82f6' }}>
  Content
</div>

// DON'T: Use arbitrary hex colors when theme colors exist
<div className="bg-[#3b82f6]">  // Use bg-blue-500 or bg-primary
  Content
</div>

// DON'T: Override theme colors with !important
<div className="bg-primary !bg-red-500">  // Don't fight the cascade
  Content
</div>
```

---

### ✅ Typography (Good)

**Example:**
```tsx
// Using Tailwind typography utilities
<h1 className="text-4xl font-bold mb-4">
  Main Heading
</h1>

<p className="text-base leading-relaxed text-gray-700">
  Body text with comfortable line height
</p>

// Responsive typography
<h2 className="text-2xl md:text-3xl lg:text-4xl font-semibold">
  Responsive Heading
</h2>

// Text truncation
<p className="truncate max-w-xs">
  Long text that will be truncated with ellipsis...
</p>

// Multi-line truncation
<p className="line-clamp-3">
  Long text that will be clamped to 3 lines with ellipsis
  at the end if it's too long to fit.
</p>
```

### ❌ Typography Anti-Patterns (Bad)

```tsx
// DON'T: Use inline styles for text
<h1 style={{ fontSize: '32px', fontWeight: 'bold' }}>
  Heading
</h1>

// DON'T: Use arbitrary values when Tailwind classes exist
<p className="text-[18px]">  // Use text-lg instead
  Text
</p>

// DON'T: Create custom font-size classes
// Use Tailwind's scale: text-xs, text-sm, text-base, text-lg, etc.
```

---

### ✅ Responsive Design (Good)

**Example:**
```tsx
// Mobile-first responsive design
<div className="w-full md:w-1/2 lg:w-1/3">
  {/* Full width on mobile, half on tablet, third on desktop */}
  Content
</div>

// Hide/show at different breakpoints
<div className="block lg:hidden">
  Mobile menu
</div>
<div className="hidden lg:block">
  Desktop menu
</div>

// Responsive flex direction
<div className="flex flex-col md:flex-row gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

// Responsive padding/margin
<section className="py-8 md:py-12 lg:py-16">
  <div className="px-4 md:px-6 lg:px-8">
    Content
  </div>
</section>
```

### ❌ Responsive Anti-Patterns (Bad)

```tsx
// DON'T: Use desktop-first approach
<div className="lg:w-1/3 md:w-1/2 w-full">  // Wrong order!
  // Write mobile styles first (w-full), then add breakpoints
</div>

// DON'T: Use CSS media queries instead of Tailwind breakpoints
<div className="custom-responsive">
  // Use Tailwind's responsive utilities instead
</div>

// DON'T: Use arbitrary breakpoint values
<div className="[@media(min-width:850px)]:block">
  // Use standard breakpoints: sm:, md:, lg:, xl:, 2xl:
</div>
```

---

### ✅ States & Interactions (Good)

**Example:**
```tsx
// Hover, focus, active states
<button className="bg-blue-500 hover:bg-blue-600 focus:ring-2 focus:ring-blue-300 active:bg-blue-700">
  Interactive Button
</button>

// Focus within
<div className="border border-gray-300 focus-within:border-blue-500">
  <input type="text" className="outline-none" />
</div>

// Disabled state
<button
  disabled
  className="bg-gray-300 text-gray-500 cursor-not-allowed disabled:opacity-50"
>
  Disabled Button
</button>

// Group hover
<div className="group hover:bg-gray-100">
  <p className="group-hover:text-blue-500">
    This text changes when parent is hovered
  </p>
</div>
```

---

### ✅ Transitions & Animations (Good)

**Example:**
```tsx
// Simple transitions
<button className="transition-colors duration-200 bg-blue-500 hover:bg-blue-600">
  Smooth Color Transition
</button>

// Multiple properties
<div className="transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg">
  Hover to scale and add shadow
</div>

// Transform
<div className="transform rotate-45 scale-110">
  Transformed element
</div>

// Animation
<div className="animate-pulse">
  Pulsing element
</div>

<div className="animate-bounce">
  Bouncing element
</div>
```

---

### ✅ Arbitrary Values (When Needed)

**Example:**
```tsx
// Use arbitrary values ONLY when Tailwind doesn't have it
<div className="top-[117px]">
  {/* Specific pixel value needed for sticky positioning */}
  Content
</div>

<div className="grid-cols-[200px_1fr_100px]">
  {/* Custom grid template */}
  <div>Sidebar</div>
  <div>Main</div>
  <div>Aside</div>
</div>

// But prefer Tailwind utilities when available:
<div className="w-48">  {/* Better than w-[192px] */}
  Content
</div>
```

---

## 🚫 Anti-Patterns

### ❌ Don't: Use Inline Styles Instead of Tailwind

**Problem:**
- Loses Tailwind's design system benefits
- Can't use responsive utilities
- Harder to maintain consistency
- No dark mode support

**Instead:**
```tsx
// Bad
<div style={{ padding: '16px', backgroundColor: '#3b82f6' }}>
  Content
</div>

// Good
<div className="p-4 bg-blue-500">
  Content
</div>
```

---

### ❌ Don't: Create Custom CSS for Simple Styles

**Problem:**
- Unnecessary abstraction
- Loses utility-first benefits
- Harder to modify
- Increases CSS bundle size

**Instead:**
```tsx
// Bad
// styles.css
.my-card {
  padding: 1.5rem;
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

// Good - use Tailwind utilities
<div className="p-6 bg-white rounded-lg shadow-md">
  Card content
</div>
```

---

### ❌ Don't: Use v3 JavaScript Configuration

**Problem:**
- v4 uses CSS-first configuration
- JavaScript config is deprecated
- Won't work with v4 features

**Instead:**
```javascript
// Bad (v3 style)
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
      },
    },
  },
}

// Good (v4 style)
// src/styles/theme.css
@theme {
  --color-primary: oklch(0.7 0.2 250);
}
```

---

### ❌ Don't: Fight the Cascade with !important

**Problem:**
- Makes debugging harder
- Creates specificity issues
- Not the Tailwind way

**Instead:**
```tsx
// Bad
<div className="bg-blue-500 !bg-red-500">
  Content
</div>

// Good - just use the class you want
<div className="bg-red-500">
  Content
</div>

// Or use conditional classes
<div className={isError ? "bg-red-500" : "bg-blue-500"}>
  Content
</div>
```

---

## 🔗 Integration Points

### With DaisyUI

**Connection:** DaisyUI is a Tailwind plugin. All Tailwind utilities work alongside DaisyUI.

**Example:**
```tsx
<button className="btn btn-primary mt-4 shadow-lg hover:shadow-xl">
  {/* DaisyUI: btn, btn-primary */}
  {/* Tailwind: mt-4, shadow-lg, hover:shadow-xl */}
  Combined styling
</button>
```

**Planning docs to read together:**
- `planning/daisyui-v5.md` - DaisyUI component patterns

---

### With React/Component Frameworks

**Connection:** Tailwind works naturally with component-based frameworks.

**Dynamic Classes with Conditional Logic:**
```tsx
// Using template literals
const buttonClass = `btn ${isPrimary ? 'btn-primary' : 'btn-secondary'} ${
  isLarge ? 'btn-lg' : 'btn-md'
}`;

// Using classnames library (recommended)
import classNames from 'classnames';

const buttonClass = classNames('btn', {
  'btn-primary': isPrimary,
  'btn-secondary': !isPrimary,
  'btn-lg': isLarge,
  'btn-md': !isLarge,
});

// Using clsx (lightweight alternative)
import clsx from 'clsx';

const buttonClass = clsx(
  'btn',
  isPrimary && 'btn-primary',
  !isPrimary && 'btn-secondary',
  isLarge ? 'btn-lg' : 'btn-md'
);
```

---

### With Dark Mode

**Connection:** Tailwind v4 has built-in dark mode support.

**Example:**
```tsx
// Dark mode variants
<div className="bg-white dark:bg-gray-800 text-black dark:text-white">
  Adapts to dark mode
</div>

// With DaisyUI themes (preferred approach)
<div className="bg-base-100 text-base-content">
  {/* Uses DaisyUI's theme system */}
  {/* Automatically switches with data-theme attribute */}
  Content
</div>
```

---

## 📚 References

### External Documentation (MANDATORY READING)

**Primary:**
- **Tailwind CSS v4 Official Docs:** https://tailwindcss.com/docs
  - **Read first** - Overview and core concepts

- **Utility-First Fundamentals:** https://tailwindcss.com/docs/utility-first
  - **Essential** - Understanding the philosophy

- **v4 Configuration Guide:** https://tailwindcss.com/docs/configuration
  - **Critical** - CSS-first configuration with @theme

**Migration & Changes:**
- **v3 → v4 Upgrade Guide:** https://tailwindcss.com/docs/upgrade-guide
  - **Important** - Breaking changes and migration path

**Core Concepts:**
- **Responsive Design:** https://tailwindcss.com/docs/responsive-design
  - Mobile-first approach and breakpoints

- **Dark Mode:** https://tailwindcss.com/docs/dark-mode
  - Implementing dark mode support

- **Customization:** https://tailwindcss.com/docs/theme
  - Using @theme directive for customization

**Utilities Reference:**
- **Layout:** https://tailwindcss.com/docs/container
- **Flexbox:** https://tailwindcss.com/docs/flex
- **Grid:** https://tailwindcss.com/docs/grid-template-columns
- **Spacing:** https://tailwindcss.com/docs/padding
- **Typography:** https://tailwindcss.com/docs/font-size
- **Colors:** https://tailwindcss.com/docs/background-color
- **Effects:** https://tailwindcss.com/docs/box-shadow

**Keep the utility reference open during implementation!**

---

## ✅ Checklist for Implementation

Before implementing styles with Tailwind v4:

- [ ] Read Tailwind v4 documentation for utilities you'll use
- [ ] Understand CSS-first configuration with @theme
- [ ] Use utility-first approach (not custom CSS)
- [ ] Write mobile-first responsive styles
- [ ] Use Tailwind's design system (spacing scale, colors)
- [ ] Combine with DaisyUI components appropriately
- [ ] Test responsive behavior (mobile → desktop)
- [ ] Test dark mode (if applicable)
- [ ] Verify no inline styles or custom CSS for simple styles

---

## 🎨 Common Patterns

### Pattern: Card Component

```tsx
<div className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
  <h3 className="text-xl font-semibold mb-2">Card Title</h3>
  <p className="text-gray-600 dark:text-gray-300">
    Card description goes here.
  </p>
  <button className="mt-4 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors">
    Action
  </button>
</div>
```

### Pattern: Form Input

```tsx
<div className="mb-4">
  <label
    htmlFor="email"
    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
  >
    Email
  </label>
  <input
    id="email"
    type="email"
    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    placeholder="you@example.com"
  />
</div>
```

### Pattern: Container Layout

```tsx
<div className="min-h-screen bg-gray-50 dark:bg-gray-900">
  <div className="container mx-auto px-4 py-8 max-w-7xl">
    <header className="mb-8">
      <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
        Page Title
      </h1>
    </header>
    <main>
      {/* Content */}
    </main>
  </div>
</div>
```

---

## ❓ Open Questions / TBD

### Should we use Tailwind's container queries?

- **Status:** Evaluate if needed
- **Owner:** Frontend Team
- **Default:** Use standard responsive breakpoints until container queries prove necessary

### Do we need custom theme colors beyond DaisyUI?

- **Status:** TBD
- **Owner:** Design Team
- **Default:** Use DaisyUI's theme system; add custom colors in @theme only if needed

---

## 📝 Notes

- **v4 is CSS-first** - configuration happens in CSS with @theme, not JavaScript
- **Mobile-first is critical** - always design for mobile first, then enhance
- **Arbitrary values are escape hatch** - use Tailwind utilities when possible
- **Combine with DaisyUI** - Tailwind for layout/spacing, DaisyUI for components
- **Use clsx or classnames** for dynamic class composition in React

---

**Last Updated:** 2025-01-21

**Version:** Tailwind CSS v4.0.0
