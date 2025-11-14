/**
 * Capitalizes the first character of the provided string and lowercases the remaining characters.
 *
 * This function preserves surrounding whitespace and supports Unicode grapheme clusters (e.g., emoji)
 * by iterating over Unicode code points rather than UTF-16 code units.
 *
 * @param str - The input string to capitalize.
 * @returns A new string with the first character uppercased and the remainder lowercased.
 */
export function capitalize(str: string): string {
  if (str.length === 0) {
    return str;
  }

  const [firstCharacter, ...restCharacters] = Array.from(str);
  const capitalizedFirst = firstCharacter.toLocaleUpperCase();
  const lowercasedRest = restCharacters.join("").toLocaleLowerCase();

  return `${capitalizedFirst}${lowercasedRest}`;
}

/**
 * Converts a string into a URL-friendly slug composed of lowercase alphanumeric characters separated by hyphens.
 *
 * The transformation performs the following steps:
 * 1. Normalizes the string to separate base characters from diacritics.
 * 2. Removes diacritic marks and any non-alphanumeric characters (excluding spaces and hyphens).
 * 3. Replaces runs of whitespace or hyphens with a single hyphen.
 * 4. Trims leading and trailing hyphens.
 *
 * @param str - The input string to slugify.
 * @returns A URL-friendly slug. Returns an empty string if no alphanumeric characters remain.
 */
export function slugify(str: string): string {
  if (str.length === 0) {
    return str;
  }

  let slug = str.normalize("NFKD");
  slug = slug.replace(/[\u0300-\u036f]/g, "");
  slug = slug.toLocaleLowerCase();
  slug = slug.replace(/[^a-z0-9\s-]/g, "");
  slug = slug.replace(/[\s-]+/g, "-");
  slug = slug.replace(/^-+|-+$/g, "");

  return slug;
}
