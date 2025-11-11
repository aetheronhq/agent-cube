import { describe, expect, it } from 'vitest';

import { capitalize, slugify, truncate } from './string-utils';

describe('capitalize', () => {
  it('returns an empty string as-is', () => {
    expect(capitalize('')).toBe('');
  });

  it('capitalizes only the first character', () => {
    expect(capitalize('hello world')).toBe('Hello world');
  });
});

describe('truncate', () => {
  it('returns the original string when shorter than the limit', () => {
    expect(truncate('short', 10)).toBe('short');
  });

  it('adds an ellipsis when truncation occurs', () => {
    expect(truncate('This is a long string', 10)).toBe('This is...');
  });

  it('omits the ellipsis when maxLength is three or less', () => {
    expect(truncate('truncate', 3)).toBe('tru');
  });

  it('throws when maxLength is negative', () => {
    expect(() => truncate('oops', -1)).toThrow(RangeError);
  });
});

describe('slugify', () => {
  it('creates a lowercase hyphenated slug', () => {
    expect(slugify('Hello World Example')).toBe('hello-world-example');
  });

  it('removes punctuation and diacritics', () => {
    expect(slugify('Café déjà vu!')).toBe('cafe-deja-vu');
  });

  it('collapses repeated separators', () => {
    expect(slugify('  spaced   out   ')).toBe('spaced-out');
  });
});
