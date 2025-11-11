export function capitalize(str: string): string {
  if (str.length === 0) {
    return '';
  }

  const [firstChar, ...rest] = str;
  return firstChar.toUpperCase() + rest.join('');
}

export function truncate(str: string, maxLength: number): string {
  if (!Number.isFinite(maxLength)) {
    throw new TypeError('maxLength must be a finite number');
  }

  if (maxLength < 0) {
    throw new RangeError('maxLength cannot be negative');
  }

  if (str.length <= maxLength) {
    return str;
  }

  if (maxLength <= 3) {
    return str.slice(0, maxLength);
  }

  return `${str.slice(0, maxLength - 3)}...`;
}

export function slugify(str: string): string {
  const normalized = str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();

  return normalized
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}
