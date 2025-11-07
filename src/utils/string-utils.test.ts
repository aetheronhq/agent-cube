import { capitalize, truncate, slugify } from './string-utils';

describe('capitalize', () => {
  it('should capitalize first letter of lowercase string', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('should keep already capitalized string unchanged', () => {
    expect(capitalize('Hello')).toBe('Hello');
  });

  it('should return empty string for empty input', () => {
    expect(capitalize('')).toBe('');
  });

  it('should capitalize single character', () => {
    expect(capitalize('a')).toBe('A');
  });

  it('should not modify rest of string', () => {
    expect(capitalize('hELLO')).toBe('HELLO');
  });

  it('should handle strings with numbers', () => {
    expect(capitalize('123abc')).toBe('123abc');
  });
});

describe('truncate', () => {
  it('should return original string if within limit', () => {
    expect(truncate('hello', 10)).toBe('hello');
  });

  it('should truncate string exceeding limit with ellipsis', () => {
    expect(truncate('hello world', 8)).toBe('hello...');
  });

  it('should handle exact boundary case', () => {
    expect(truncate('hello', 5)).toBe('hello');
  });

  it('should return empty string for empty input', () => {
    expect(truncate('', 5)).toBe('');
  });

  it('should handle very short maxLength', () => {
    expect(truncate('hello', 2)).toBe('he');
  });

  it('should handle maxLength of 3', () => {
    expect(truncate('hello world', 3)).toBe('...');
  });

  it('should handle maxLength less than 3', () => {
    expect(truncate('hello', 1)).toBe('h');
  });

  it('should include ellipsis in maxLength calculation', () => {
    expect(truncate('hello world', 10)).toBe('hello w...');
    expect(truncate('hello world', 10).length).toBe(10);
  });

  it('should handle long strings', () => {
    const longString = 'a'.repeat(100);
    const result = truncate(longString, 20);
    expect(result.length).toBe(20);
    expect(result.endsWith('...')).toBe(true);
  });
});

describe('slugify', () => {
  it('should convert simple text to slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('should remove special characters', () => {
    expect(slugify('Hello, World!')).toBe('hello-world');
  });

  it('should handle multiple spaces', () => {
    expect(slugify('Hello   World')).toBe('hello-world');
  });

  it('should trim leading and trailing spaces', () => {
    expect(slugify(' hello world ')).toBe('hello-world');
  });

  it('should handle numbers', () => {
    expect(slugify('Test 123')).toBe('test-123');
  });

  it('should remove consecutive hyphens', () => {
    expect(slugify('hello---world')).toBe('hello-world');
  });

  it('should handle empty string', () => {
    expect(slugify('')).toBe('');
  });

  it('should handle string with only special characters', () => {
    expect(slugify('!@#$%^&*()')).toBe('');
  });

  it('should preserve existing hyphens', () => {
    expect(slugify('hello-world')).toBe('hello-world');
  });

  it('should handle mixed case with numbers and special chars', () => {
    expect(slugify('Hello World 2024!')).toBe('hello-world-2024');
  });

  it('should remove leading hyphens', () => {
    expect(slugify('-hello world')).toBe('hello-world');
  });

  it('should remove trailing hyphens', () => {
    expect(slugify('hello world-')).toBe('hello-world');
  });

  it('should handle complex strings', () => {
    expect(slugify('The Quick Brown Fox: A Story (2024)')).toBe('the-quick-brown-fox-a-story-2024');
  });
});
