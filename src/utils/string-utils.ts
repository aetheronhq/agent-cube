/**
 * Capitalize the first letter of a string
 * @param str - Input string
 * @returns String with first letter capitalized
 * @example capitalize("hello world") // "Hello world"
 */
export function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncate a string to a maximum length with ellipsis
 * @param str - Input string
 * @param maxLength - Maximum length (must be >= 3 for ellipsis)
 * @returns Truncated string with '...' if truncated
 * @example truncate("Hello World", 8) // "Hello..."
 */
export function truncate(str: string, maxLength: number): string {
  if (maxLength < 3) {
    throw new Error('maxLength must be >= 3');
  }
  if (str.length <= maxLength) {
    return str;
  }
  return str.slice(0, maxLength - 3) + '...';
}

/**
 * Convert string to URL-safe slug
 * @param str - Input string
 * @returns Lowercase slug with hyphens
 * @example slugify("Hello World! 123") // "hello-world-123"
 */
export function slugify(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
