import { describe, expect, it } from 'vitest'

import { capitalize, slugify, truncate } from './string-utils'

describe('capitalize', () => {
  it('capitalizes the first character of a string', () => {
    expect(capitalize('hello')).toBe('Hello')
  })

  it('returns an empty string when input is empty', () => {
    expect(capitalize('')).toBe('')
  })

  it('preserves the remainder of the string', () => {
    expect(capitalize('hello WORLD')).toBe('Hello WORLD')
  })
})

describe('truncate', () => {
  it('returns the original string when shorter than the limit', () => {
    expect(truncate('short', 10)).toBe('short')
  })

  it('truncates and appends an ellipsis when the text is too long', () => {
    expect(truncate('Hello world', 5)).toBe('He...')
  })

  it('does not add ellipsis when limit is very small', () => {
    expect(truncate('Hello', 3)).toBe('Hel')
  })

  it('returns an empty string for non-positive limits', () => {
    expect(truncate('Hello', 0)).toBe('')
    expect(truncate('Hello', -5)).toBe('')
  })
})

describe('slugify', () => {
  it('converts text to a URL-safe slug', () => {
    expect(slugify('Hello, World!')).toBe('hello-world')
  })

  it('collapses whitespace and trims separators', () => {
    expect(slugify('  Multiple   spaces here ')).toBe('multiple-spaces-here')
  })

  it('removes diacritics', () => {
    expect(slugify('Crème brûlée')).toBe('creme-brulee')
  })
})
