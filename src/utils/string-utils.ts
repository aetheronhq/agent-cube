/**
 * Capitalizes the first letter of a string.
 * @param str - The input string
 * @returns The string with first letter capitalized
 */
export function capitalize(str: string): string {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncates a string to a maximum length, adding ellipsis if needed.
 * @param str - The input string
 * @param maxLength - Maximum length including ellipsis
 * @returns Truncated string with ellipsis or original string
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  if (maxLength < 3) return str.slice(0, maxLength);
  return str.slice(0, maxLength - 3) + '...';
}

/**
 * Converts a string to a URL-safe slug.
 * @param str - The input string
 * @returns URL-safe slug with lowercase letters, numbers, and hyphens
 */
export function slugify(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}
