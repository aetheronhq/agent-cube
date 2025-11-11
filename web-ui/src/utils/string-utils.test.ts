import { describe, it, expect } from 'vitest';
import { capitalize, truncate, slugify } from './string-utils';

describe('capitalize', () => {
  it('capitalizes first letter of a string', () => {
    expect(capitalize('hello')).toBe('Hello');
    expect(capitalize('world')).toBe('World');
  });

  it('handles already capitalized strings', () => {
    expect(capitalize('Hello')).toBe('Hello');
  });

  it('handles empty strings', () => {
    expect(capitalize('')).toBe('');
  });

  it('handles single character strings', () => {
    expect(capitalize('a')).toBe('A');
  });
});

describe('truncate', () => {
  it('truncates strings longer than maxLength', () => {
    expect(truncate('Hello World', 8)).toBe('Hello...');
    expect(truncate('This is a long string', 10)).toBe('This is...');
  });

  it('does not truncate strings shorter than maxLength', () => {
    expect(truncate('Hello', 10)).toBe('Hello');
    expect(truncate('Hi', 5)).toBe('Hi');
  });

  it('handles strings exactly at maxLength', () => {
    expect(truncate('Hello', 5)).toBe('Hello');
  });

  it('handles empty strings', () => {
    expect(truncate('', 10)).toBe('');
  });

  it('handles very short maxLength', () => {
    expect(truncate('Hello World', 4)).toBe('H...');
  });
});

describe('slugify', () => {
  it('converts string to lowercase slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
    expect(slugify('TypeScript Utils')).toBe('typescript-utils');
  });

  it('removes special characters', () => {
    expect(slugify('Hello! World?')).toBe('hello-world');
    expect(slugify('Test@#$%123')).toBe('test123');
  });

  it('handles multiple spaces and underscores', () => {
    expect(slugify('hello   world')).toBe('hello-world');
    expect(slugify('hello_world')).toBe('hello-world');
    expect(slugify('hello---world')).toBe('hello-world');
  });

  it('trims leading and trailing hyphens', () => {
    expect(slugify(' hello world ')).toBe('hello-world');
    expect(slugify('--hello--')).toBe('hello');
  });

  it('handles empty strings', () => {
    expect(slugify('')).toBe('');
  });

  it('handles strings with only special characters', () => {
    expect(slugify('!@#$%')).toBe('');
  });
});
