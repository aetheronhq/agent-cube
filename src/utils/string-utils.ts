/**
 * Capitalizes the first letter of a string and lowercases the remaining characters.
 * @param str - String to capitalize.
 * @returns Capitalized string.
 */
export function capitalize(str: string): string {
  if (str.length === 0) {
    return str;
  }

  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Truncates a string to the provided maximum length, appending an ellipsis when truncation occurs.
 * @param str - String to truncate.
 * @param maxLength - Maximum number of characters to keep.
 * @returns Truncated string respecting the maximum length.
 */
export function truncate(str: string, maxLength: number): string {
  if (maxLength <= 0) {
    return '';
  }

  if (str.length <= maxLength) {
    return str;
  }

  if (maxLength < 3) {
    return str.slice(0, maxLength);
  }

  return `${str.slice(0, maxLength - 3)}...`;
}

/**
 * Converts a string into a lowercase, hyphen-separated, URL-safe slug.
 * @param str - String to convert into a slug.
 * @returns Slugified representation of the input string.
 */
export function slugify(str: string): string {
  const cleaned = str
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');

  return cleaned.replace(/^-+|-+$/g, '');
}
