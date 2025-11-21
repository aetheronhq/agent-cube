# Third-Party Tools - Version Registry

**Purpose:** Single source of truth for required tool versions and documentation.

**Usage:** Reference this in ALL tasks that use third-party tools.

**Related Docs:** Planning docs for specific tools contain detailed patterns and examples.

---

## UI Framework & Styling

### DaisyUI

**Required Version:** `^5.0.0`

**Status:** ✅ Active (use for all new UI components)

**Planning Doc:** `planning/daisyui-v5.md` (detailed patterns and examples)

**Documentation:**
- **Official Docs:** https://daisyui.com/docs/
- **Components Reference:** https://daisyui.com/components/
- **Themes:** https://daisyui.com/docs/themes/
- **v4 → v5 Migration:** https://daisyui.com/docs/changelog/

**Key Changes in v5:**
- Updated component API
- Improved theme customization
- Performance optimizations
- Breaking changes from v4 (see migration guide)

**Installation:**
```bash
npm install daisyui@^5.0.0
```

**Configuration (Tailwind v4 compatible):**
```javascript
// tailwind.config.js
module.exports = {
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
  }
}
```

---

### Tailwind CSS

**Required Version:** `^4.0.0`

**Status:** ✅ Active (use for all styling)

**Planning Doc:** `planning/tailwindcss-v4.md` (detailed patterns and examples)

**Documentation:**
- **Official Docs:** https://tailwindcss.com/docs
- **Configuration Guide:** https://tailwindcss.com/docs/configuration
- **Core Concepts:** https://tailwindcss.com/docs/utility-first
- **v3 → v4 Upgrade Guide:** https://tailwindcss.com/docs/upgrade-guide

**Key Changes in v4:**
- CSS-first configuration (new `@theme` directive)
- Improved performance and smaller bundle sizes
- Enhanced arbitrary value support
- Updated color palette system
- Native cascade layer support

**Installation:**
```bash
npm install tailwindcss@^4.0.0
```

**Configuration (v4 CSS-first approach):**
```css
/* styles/theme.css */
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.7 0.2 250);
  --font-family-sans: "Inter", system-ui, sans-serif;
}
```

---

## State Management

### React Context API

**Status:** ✅ Preferred for application state

**Documentation:**
- **Official Docs:** https://react.dev/reference/react/useContext
- **Best Practices:** https://react.dev/learn/scaling-up-with-reducer-and-context

**When to use:**
- Application-wide state (theme, auth, user preferences)
- Shared state across multiple components
- Avoiding prop drilling

**When NOT to use:**
- Frequently changing state (can cause performance issues)
- Complex state logic (consider useReducer instead)

---

## API & Data Fetching

### Fetch API (Native)

**Status:** ✅ Preferred for API calls

**Documentation:**
- **MDN Reference:** https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- **Using Fetch:** https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

**Rationale:**
- Native browser API (no dependencies)
- Modern and well-supported
- Sufficient for most use cases

**Pattern:**
```typescript
async function fetchData(endpoint: string) {
  try {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}
```

---

## Build Tools & Bundlers

### Vite

**Required Version:** `^5.0.0`

**Status:** ✅ Active (use for all React projects)

**Documentation:**
- **Official Docs:** https://vitejs.dev/guide/
- **Configuration Reference:** https://vitejs.dev/config/
- **Features:** https://vitejs.dev/guide/features

**Key Features:**
- Lightning-fast HMR (Hot Module Replacement)
- Optimized build with Rollup
- Built-in TypeScript support
- Plugin ecosystem

**Installation:**
```bash
npm install vite@^5.0.0
```

---

## Testing

### Vitest

**Required Version:** `^1.0.0`

**Status:** ✅ Preferred for unit/integration tests

**Documentation:**
- **Official Docs:** https://vitest.dev/guide/
- **API Reference:** https://vitest.dev/api/
- **Examples:** https://vitest.dev/guide/features

**Rationale:**
- Vite-native (fast and consistent with dev environment)
- Jest-compatible API
- Built-in TypeScript support

**Installation:**
```bash
npm install vitest@^1.0.0
```

---

### React Testing Library

**Required Version:** `^14.0.0`

**Status:** ✅ Preferred for React component testing

**Documentation:**
- **Official Docs:** https://testing-library.com/docs/react-testing-library/intro/
- **Queries:** https://testing-library.com/docs/queries/about
- **Best Practices:** https://kentcdodds.com/blog/common-mistakes-with-react-testing-library

**Installation:**
```bash
npm install @testing-library/react@^14.0.0
```

---

## Type Safety

### TypeScript

**Required Version:** `^5.3.0`

**Status:** ✅ Required for all code

**Documentation:**
- **Official Docs:** https://www.typescriptlang.org/docs/
- **Handbook:** https://www.typescriptlang.org/docs/handbook/intro.html
- **TypeScript 5.3 Release:** https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-3.html

**Key Features in 5.3:**
- Import attributes
- Resolution mode in import types
- Improved narrowing

---

## How to Use This Doc

### When Creating Tasks

1. **Check this doc** for required versions
2. **Link to relevant documentation** sections in task files
3. **Reference specific planning docs** for detailed patterns (e.g., `planning/daisyui-v5.md`)
4. **Note key changes** that affect implementation

### When Reviewing Code

1. **Verify correct versions** are used
2. **Check patterns** match latest documentation
3. **Ensure no deprecated APIs** are used
4. **Confirm external dependencies** align with this registry

### When Adding New Tools

1. **Add entry** to this file with version and documentation
2. **Create dedicated planning doc** if tool requires detailed patterns
3. **Update task template** to reference new tool
4. **Document rationale** for choosing this tool

---

## Maintenance

**Owner:** Tech Lead

**Update Frequency:** When tool versions change or new tools are added

**Last Updated:** 2025-01-21

---

## Notes

- **Prefer official documentation** over third-party tutorials
- **Link to specific sections** when possible (not just homepage)
- **Include migration guides** when major version changes occur
- **Document breaking changes** that affect existing code
- **Keep this registry updated** as single source of truth
