import { describe, expect, it } from 'vitest';
import { capitalize, slugify, truncate } from './string-utils';

describe('capitalize', () => {
  it('capitalizes a lowercase word', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('returns an empty string when input is empty', () => {
    expect(capitalize('')).toBe('');
  });

  it('handles single character strings', () => {
    expect(capitalize('a')).toBe('A');
  });

  it('lowercases the remainder of the string', () => {
    expect(capitalize('hELLO WORLD')).toBe('Hello world');
  });

  it('leaves non-letter first characters unchanged', () => {
    expect(capitalize('123abc')).toBe('123abc');
  });
});

describe('truncate', () => {
  it('returns the string unchanged when shorter than maxLength', () => {
    expect(truncate('Hello', 10)).toBe('Hello');
  });

  it('returns the string unchanged when equal to maxLength', () => {
    expect(truncate('Hello', 5)).toBe('Hello');
  });

  it('appends an ellipsis when truncating', () => {
    expect(truncate('Hello World', 8)).toBe('Hello...');
  });

  it('returns exactly maxLength characters when maxLength is less than 3', () => {
    expect(truncate('Hello', 2)).toBe('He');
  });

  it('handles zero or negative maxLength values', () => {
    expect(truncate('Hello', 0)).toBe('');
    expect(truncate('Hello', -1)).toBe('');
  });

  it('returns an ellipsis when maxLength equals 3 and truncation is needed', () => {
    expect(truncate('Hello', 3)).toBe('...');
  });
});

describe('slugify', () => {
  it('converts spaces to hyphens and lowercases the string', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('removes special characters', () => {
    expect(slugify('Hello, World!')).toBe('hello-world');
  });

  it('collapses multiple spaces and hyphens', () => {
    expect(slugify('  Foo   Bar -- Baz  ')).toBe('foo-bar-baz');
  });

  it('handles strings that are already slugified', () => {
    expect(slugify('already-slugified-string')).toBe('already-slugified-string');
  });

  it('removes leading and trailing hyphens after cleanup', () => {
    expect(slugify('---Leading and Trailing---')).toBe('leading-and-trailing');
  });

  it('removes emoji and other unicode symbols', () => {
    expect(slugify('Emoji 😀 test')).toBe('emoji-test');
  });

  it('returns an empty string when input is empty', () => {
    expect(slugify('')).toBe('');
  });
});
