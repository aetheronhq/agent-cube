/**
 * Capitalizes the first letter of a string and lowercases the rest.
 * @param str - The string to capitalize
 * @returns The capitalized string
 * @example capitalize("hello") → "Hello"
 * @example capitalize("HELLO") → "Hello"
 */
export function capitalize(str: string): string {
  if (str.length === 0) return str;
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Truncates a string to a maximum length, adding "..." if truncated.
 * The ellipsis counts toward the maxLength.
 * @param str - The string to truncate
 * @param maxLength - Maximum length of the returned string
 * @returns The truncated string with ellipsis if needed
 * @example truncate("Hello World", 8) → "Hello..."
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  if (maxLength < 3) return str.slice(0, maxLength);
  return str.slice(0, maxLength - 3) + '...';
}

/**
 * Converts a string to a URL-safe slug format.
 * Lowercases all characters, replaces spaces with hyphens,
 * removes non-alphanumeric characters, and collapses multiple hyphens.
 * @param str - The string to slugify
 * @returns The slugified string
 * @example slugify("Hello World!") → "hello-world"
 * @example slugify("  Foo  Bar  ") → "foo-bar"
 */
export function slugify(str: string): string {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}
