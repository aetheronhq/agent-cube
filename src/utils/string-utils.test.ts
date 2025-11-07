import { describe, expect, it } from 'vitest';

import { capitalize, slugify, truncate } from './string-utils';

describe('capitalize', () => {
  it('capitalizes the first letter of a lowercase string', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('leaves already capitalized strings unchanged', () => {
    expect(capitalize('Hello')).toBe('Hello');
  });

  it('handles empty strings', () => {
    expect(capitalize('')).toBe('');
  });

  it('capitalizes single characters', () => {
    expect(capitalize('a')).toBe('A');
  });

  // @ts-expect-error -- capitalize requires a string argument
  capitalize();
});

describe('truncate', () => {
  it('returns the original string when within the limit', () => {
    expect(truncate('hello', 10)).toBe('hello');
  });

  it('truncates and appends ellipsis when exceeding the limit', () => {
    expect(truncate('hello world', 8)).toBe('hello...');
  });

  it('handles exact boundary case without truncation', () => {
    expect(truncate('hello', 5)).toBe('hello');
  });

  it('handles empty strings', () => {
    expect(truncate('', 5)).toBe('');
  });

  it('truncates without ellipsis when maxLength is very small', () => {
    expect(truncate('abcdef', 2)).toBe('ab');
  });

  it('returns an empty string when maxLength is zero or negative', () => {
    expect(truncate('abc', 0)).toBe('');
    expect(truncate('abc', -1)).toBe('');
  });

  // @ts-expect-error -- truncate requires a numeric maxLength
  truncate('abc');
});

describe('slugify', () => {
  it('converts simple text to a slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('removes special characters', () => {
    expect(slugify('Hello, World!')).toBe('hello-world');
  });

  it('collapses multiple spaces', () => {
    expect(slugify('Hello   World')).toBe('hello-world');
  });

  it('trims leading and trailing spaces', () => {
    expect(slugify(' hello world ')).toBe('hello-world');
  });

  it('preserves numbers', () => {
    expect(slugify('Test 123')).toBe('test-123');
  });

  it('returns an empty string when normalization removes all characters', () => {
    expect(slugify('!@#$%^&*()')).toBe('');
  });

  // @ts-expect-error -- slugify requires a string argument
  slugify();
});
