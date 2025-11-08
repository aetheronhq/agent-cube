import { describe, it, expect } from 'vitest';
import { capitalize, truncate, slugify } from './string-utils';

describe('capitalize', () => {
  it('capitalizes first letter and lowercases rest', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('handles already capitalized strings', () => {
    expect(capitalize('Hello')).toBe('Hello');
  });

  it('converts all caps to proper capitalization', () => {
    expect(capitalize('HELLO')).toBe('Hello');
  });

  it('handles empty string', () => {
    expect(capitalize('')).toBe('');
  });

  it('handles single lowercase character', () => {
    expect(capitalize('a')).toBe('A');
  });

  it('handles single uppercase character', () => {
    expect(capitalize('A')).toBe('A');
  });

  it('handles mixed case strings', () => {
    expect(capitalize('hELLo')).toBe('Hello');
  });
});

describe('truncate', () => {
  it('truncates string longer than maxLength with ellipsis', () => {
    expect(truncate('Hello World', 8)).toBe('Hello...');
  });

  it('returns unchanged string if shorter than maxLength', () => {
    expect(truncate('Hi', 10)).toBe('Hi');
  });

  it('returns unchanged string if exactly maxLength', () => {
    expect(truncate('Hello', 5)).toBe('Hello');
  });

  it('handles very short maxLength without ellipsis', () => {
    expect(truncate('Hello', 2)).toBe('He');
  });

  it('handles maxLength of 0', () => {
    expect(truncate('Hello', 0)).toBe('');
  });

  it('handles maxLength of 1', () => {
    expect(truncate('Hello', 1)).toBe('H');
  });

  it('handles maxLength of 3 with ellipsis', () => {
    expect(truncate('Hello', 3)).toBe('...');
  });

  it('handles empty string', () => {
    expect(truncate('', 5)).toBe('');
  });

  it('correctly counts ellipsis in maxLength', () => {
    expect(truncate('Hello World', 10)).toBe('Hello W...');
  });
});

describe('slugify', () => {
  it('converts spaces to hyphens and lowercases', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('removes special characters', () => {
    expect(slugify('Hello World!')).toBe('hello-world');
  });

  it('collapses multiple spaces to single hyphen', () => {
    expect(slugify('Hello  World')).toBe('hello-world');
  });

  it('removes leading and trailing spaces', () => {
    expect(slugify('  Hello World  ')).toBe('hello-world');
  });

  it('collapses consecutive hyphens', () => {
    expect(slugify('Hello---World')).toBe('hello-world');
  });

  it('handles already slug-like strings', () => {
    expect(slugify('hello-world')).toBe('hello-world');
  });

  it('handles empty string', () => {
    expect(slugify('')).toBe('');
  });

  it('removes all non-alphanumeric except hyphens', () => {
    expect(slugify('Hello@#$%World')).toBe('helloworld');
  });

  it('handles strings with only special characters', () => {
    expect(slugify('!!!')).toBe('');
  });

  it('handles complex mixed input', () => {
    expect(slugify('  Foo  Bar  Baz!  ')).toBe('foo-bar-baz');
  });

  it('removes leading hyphens', () => {
    expect(slugify('---hello-world')).toBe('hello-world');
  });

  it('removes trailing hyphens', () => {
    expect(slugify('hello-world---')).toBe('hello-world');
  });

  it('handles numbers in slugs', () => {
    expect(slugify('Hello World 123')).toBe('hello-world-123');
  });
});
