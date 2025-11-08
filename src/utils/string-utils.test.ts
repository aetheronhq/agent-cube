import { capitalize, truncate, slugify } from './string-utils';

describe('capitalize', () => {
  it('should handle empty string', () => {
    expect(capitalize('')).toBe('');
  });

  it('should capitalize single character', () => {
    expect(capitalize('a')).toBe('A');
  });

  it('should handle already capitalized string', () => {
    expect(capitalize('Hello')).toBe('Hello');
  });

  it('should capitalize lowercase string', () => {
    expect(capitalize('hello world')).toBe('Hello world');
  });

  it('should preserve rest of string as-is', () => {
    expect(capitalize('hELLO WORLD')).toBe('HELLO WORLD');
  });

  it('should handle string with numbers and special chars', () => {
    expect(capitalize('123abc!@#')).toBe('123abc!@#');
  });
});

describe('truncate', () => {
  it('should return string unchanged if shorter than maxLength', () => {
    expect(truncate('Hello', 10)).toBe('Hello');
  });

  it('should return string unchanged if equal to maxLength', () => {
    expect(truncate('Hello', 5)).toBe('Hello');
  });

  it('should truncate string longer than maxLength', () => {
    expect(truncate('Hello World', 8)).toBe('Hello...');
  });

  it('should throw error if maxLength < 3', () => {
    expect(() => truncate('Hello', 2)).toThrow('maxLength must be >= 3');
  });

  it('should handle edge case maxLength = 3', () => {
    expect(truncate('Hello', 3)).toBe('...');
  });

  it('should handle very long strings', () => {
    const longString = 'a'.repeat(1000);
    const result = truncate(longString, 10);
    expect(result).toBe('aaaaaaa...');
    expect(result.length).toBe(10);
  });

  it('should truncate at exact position', () => {
    expect(truncate('12345678', 5)).toBe('12...');
  });
});

describe('slugify', () => {
  it('should convert simple words with spaces', () => {
    expect(slugify('hello world')).toBe('hello-world');
  });

  it('should handle mixed case', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('should replace special characters with hyphens', () => {
    expect(slugify('Hello World! 123')).toBe('hello-world-123');
  });

  it('should collapse multiple consecutive spaces', () => {
    expect(slugify('hello    world')).toBe('hello-world');
  });

  it('should trim leading and trailing spaces', () => {
    expect(slugify('  hello world  ')).toBe('hello-world');
  });

  it('should handle numbers and letters', () => {
    expect(slugify('Test 123 ABC')).toBe('test-123-abc');
  });

  it('should handle strings with only special characters', () => {
    expect(slugify('!!!')).toBe('');
  });

  it('should handle mixed special characters', () => {
    expect(slugify('hello@world#test')).toBe('hello-world-test');
  });

  it('should collapse multiple hyphens to single hyphen', () => {
    expect(slugify('hello---world')).toBe('hello-world');
  });

  it('should handle unicode characters', () => {
    expect(slugify('café résumé')).toBe('caf-r-sum');
  });

  it('should handle emoji', () => {
    expect(slugify('hello 👋 world')).toBe('hello-world');
  });

  it('should handle empty string', () => {
    expect(slugify('')).toBe('');
  });
});
