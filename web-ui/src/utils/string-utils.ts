/**
 * Capitalizes the first character of a string and converts the rest to lowercase.
 * 
 * @param str - The input string to capitalize
 * @returns The capitalized string with first character uppercase and remaining lowercase
 * 
 * @example
 * ```typescript
 * capitalize("hello")        // "Hello"
 * capitalize("WORLD")        // "World"
 * capitalize("hELLo WoRLD")  // "Hello world"
 * capitalize("")             // ""
 * capitalize("a")            // "A"
 * ```
 */
export function capitalize(str: string): string {
  // Handle empty string edge case
  if (str.length === 0) {
    return str;
  }
  
  // Get first character and convert to uppercase
  const firstChar = str.charAt(0).toUpperCase();
  
  // Get remaining characters and convert to lowercase
  const restOfString = str.slice(1).toLowerCase();
  
  return firstChar + restOfString;
}

/**
 * Converts a string to a URL-friendly slug format.
 * - Converts to lowercase
 * - Replaces spaces with hyphens
 * - Removes special characters (keeps only alphanumeric and hyphens)
 * - Removes leading/trailing hyphens
 * - Collapses multiple consecutive hyphens/spaces into single hyphen
 * 
 * @param str - The input string to convert to slug format
 * @returns The slugified string (lowercase, hyphenated, alphanumeric only)
 * 
 * @example
 * ```typescript
 * slugify("Hello World")              // "hello-world"
 * slugify("  Multiple   Spaces  ")    // "multiple-spaces"
 * slugify("Special!@#$Characters")    // "specialcharacters"
 * slugify("Mix3d NUM83RS")            // "mix3d-num83rs"
 * slugify("UPPERCASE")                // "uppercase"
 * slugify("")                         // ""
 * slugify("---Hyphens---")            // "hyphens"
 * ```
 */
export function slugify(str: string): string {
  // Handle empty string edge case
  if (str.length === 0) {
    return str;
  }
  
  // Step 1: Convert to lowercase
  let slug = str.toLowerCase();
  
  // Step 2: Remove special characters (keep only alphanumeric, spaces, and hyphens)
  slug = slug.replace(/[^a-z0-9\s-]/g, '');
  
  // Step 3: Replace one or more spaces with a single hyphen
  slug = slug.replace(/\s+/g, '-');
  
  // Step 4: Replace multiple consecutive hyphens with a single hyphen
  slug = slug.replace(/-+/g, '-');
  
  // Step 5: Remove leading and trailing hyphens
  slug = slug.replace(/^-+|-+$/g, '');
  
  return slug;
}
