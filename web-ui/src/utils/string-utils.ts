export function capitalize(str: string): string {
  if (str.length === 0) {
    return ''
  }

  const [firstChar, ...rest] = str
  return firstChar.toUpperCase() + rest.join('')
}

export function truncate(str: string, maxLength: number): string {
  if (!Number.isFinite(maxLength)) {
    throw new RangeError('maxLength must be a finite number')
  }

  const limit = Math.max(0, Math.floor(maxLength))

  if (limit === 0) {
    return ''
  }

  if (str.length <= limit) {
    return str
  }

  if (limit <= 3) {
    return str.slice(0, limit)
  }

  const truncated = str.slice(0, limit - 3).trimEnd()
  return `${truncated}...`
}

export function slugify(str: string): string {
  const ascii = str.normalize('NFKD').replace(/[\u0300-\u036f]/g, '')

  return ascii
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}
