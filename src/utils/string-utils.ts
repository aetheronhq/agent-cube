/**
 * Capitalizes the first character of the provided string and lowercases the rest.
 * @param str - The input string to transform.
 * @returns A string with the first character capitalized and the remainder lowercased.
 */
export function capitalize(str: string): string {
  if (str.length === 0) {
    return str;
  }

  const firstChar = str.charAt(0);
  const rest = str.slice(1);
  return firstChar.toUpperCase() + rest.toLowerCase();
}

/**
 * Truncates the provided string to the specified maximum length, appending an ellipsis when appropriate.
 * @param str - The input string to truncate.
 * @param maxLength - The maximum length of the resulting string.
 * @returns The truncated string, optionally with an ellipsis suffix.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) {
    return str;
  }

  if (maxLength < 3) {
    return str.slice(0, Math.max(maxLength, 0));
  }

  const sliceLength = maxLength - 3;
  return str.slice(0, sliceLength) + '...';
}

/**
 * Converts the provided string into a URL-safe slug comprised of lowercase letters, digits, and hyphens.
 * @param str - The input string to convert.
 * @returns A slugified representation of the input.
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
