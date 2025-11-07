/**
 * Capitalizes the first letter of a string.
 * @param str - The input string
 * @returns The string with the first letter capitalized
 */
export function capitalize(str: string): string {
  if (!str) {
    return str;
  }

  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncates a string to a maximum length, adding an ellipsis when possible.
 * @param str - The input string
 * @param maxLength - Maximum length including ellipsis when applied
 * @returns The truncated string or the original input when within the limit
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
 * Converts a string to a URL-safe slug format.
 * @param str - The input string
 * @returns A lowercase, hyphen-separated slug comprised of alphanumeric characters
 */
export function slugify(str: string): string {
  const normalized = str.trim().toLowerCase();

  if (!normalized) {
    return '';
  }

  const slug = normalized
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');

  return slug;
}
