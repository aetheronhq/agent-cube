import { describe, it, expect } from 'vitest';
import { capitalize, slugify } from './string-utils';

describe('capitalize', () => {
  describe('basic functionality', () => {
    it('should capitalize first letter of lowercase word', () => {
      expect(capitalize('hello')).toBe('Hello');
    });

    it('should convert all-uppercase word to capitalized', () => {
      expect(capitalize('WORLD')).toBe('World');
    });

    it('should convert mixed case to capitalized', () => {
      expect(capitalize('hELLo WoRLD')).toBe('Hello world');
    });

    it('should handle lowercase multi-word string', () => {
      expect(capitalize('the quick brown fox')).toBe('The quick brown fox');
    });

    it('should handle uppercase multi-word string', () => {
      expect(capitalize('THE QUICK BROWN FOX')).toBe('The quick brown fox');
    });
  });

  describe('edge cases', () => {
    it('should handle empty string', () => {
      expect(capitalize('')).toBe('');
    });

    it('should handle single lowercase character', () => {
      expect(capitalize('a')).toBe('A');
    });

    it('should handle single uppercase character', () => {
      expect(capitalize('A')).toBe('A');
    });

    it('should preserve leading whitespace', () => {
      expect(capitalize('  hello')).toBe('  hello');
    });

    it('should preserve trailing whitespace', () => {
      expect(capitalize('hello  ')).toBe('Hello  ');
    });

    it('should preserve both leading and trailing whitespace', () => {
      expect(capitalize('  hello  ')).toBe('  hello  ');
    });

    it('should handle string with numbers', () => {
      expect(capitalize('hello123')).toBe('Hello123');
    });

    it('should handle string starting with number', () => {
      expect(capitalize('123hello')).toBe('123hello');
    });

    it('should handle special characters', () => {
      expect(capitalize('!hello')).toBe('!hello');
    });

    it('should handle string with special characters mixed in', () => {
      expect(capitalize('hello!world')).toBe('Hello!world');
    });
  });

  describe('unicode and international characters', () => {
    it('should handle basic unicode characters', () => {
      expect(capitalize('über')).toBe('Über');
    });

    it('should handle accented characters', () => {
      expect(capitalize('école')).toBe('École');
    });
  });
});

describe('slugify', () => {
  describe('basic functionality', () => {
    it('should convert simple string with spaces to slug', () => {
      expect(slugify('Hello World')).toBe('hello-world');
    });

    it('should handle multiple spaces between words', () => {
      expect(slugify('  Multiple   Spaces  ')).toBe('multiple-spaces');
    });

    it('should remove special characters', () => {
      expect(slugify('Special!@#$Characters')).toBe('specialcharacters');
    });

    it('should preserve numbers', () => {
      expect(slugify('Mix3d NUM83RS')).toBe('mix3d-num83rs');
    });

    it('should convert uppercase to lowercase', () => {
      expect(slugify('UPPERCASE')).toBe('uppercase');
    });

    it('should handle mixed case string', () => {
      expect(slugify('ThIs Is MiXeD CaSe')).toBe('this-is-mixed-case');
    });
  });

  describe('edge cases', () => {
    it('should handle empty string', () => {
      expect(slugify('')).toBe('');
    });

    it('should remove leading hyphens', () => {
      expect(slugify('---Hello')).toBe('hello');
    });

    it('should remove trailing hyphens', () => {
      expect(slugify('Hello---')).toBe('hello');
    });

    it('should remove leading and trailing hyphens', () => {
      expect(slugify('---Hyphens---')).toBe('hyphens');
    });

    it('should handle string with only special characters', () => {
      expect(slugify('!@#$%^&*()')).toBe('');
    });

    it('should handle leading spaces', () => {
      expect(slugify('   Hello World')).toBe('hello-world');
    });

    it('should handle trailing spaces', () => {
      expect(slugify('Hello World   ')).toBe('hello-world');
    });

    it('should collapse multiple consecutive hyphens', () => {
      expect(slugify('hello---world')).toBe('hello-world');
    });

    it('should handle mix of spaces and hyphens', () => {
      expect(slugify('hello - - - world')).toBe('hello-world');
    });

    it('should handle single character', () => {
      expect(slugify('a')).toBe('a');
    });

    it('should handle single number', () => {
      expect(slugify('5')).toBe('5');
    });
  });

  describe('idempotency', () => {
    it('should return same result when called on already slugified string', () => {
      const slug = 'hello-world';
      expect(slugify(slug)).toBe(slug);
    });

    it('should handle already slugified complex string', () => {
      const slug = 'this-is-a-slug-123';
      expect(slugify(slug)).toBe(slug);
    });
  });

  describe('special character combinations', () => {
    it('should handle parentheses', () => {
      expect(slugify('Hello (World)')).toBe('hello-world');
    });

    it('should handle brackets', () => {
      expect(slugify('Hello [World]')).toBe('hello-world');
    });

    it('should handle punctuation', () => {
      expect(slugify('Hello, World!')).toBe('hello-world');
    });

    it('should handle apostrophes', () => {
      expect(slugify("It's a beautiful day")).toBe('its-a-beautiful-day');
    });

    it('should handle quotes', () => {
      expect(slugify('"Hello World"')).toBe('hello-world');
    });

    it('should handle underscores', () => {
      expect(slugify('hello_world')).toBe('helloworld');
    });

    it('should handle ampersands', () => {
      expect(slugify('Tom & Jerry')).toBe('tom-jerry');
    });

    it('should handle dots', () => {
      expect(slugify('hello.world')).toBe('helloworld');
    });
  });

  describe('real-world examples', () => {
    it('should convert blog post title', () => {
      expect(slugify('How to Learn JavaScript in 2024')).toBe('how-to-learn-javascript-in-2024');
    });

    it('should convert product name', () => {
      expect(slugify('iPhone 15 Pro Max')).toBe('iphone-15-pro-max');
    });

    it('should convert page title with special chars', () => {
      expect(slugify('FAQ: Getting Started!')).toBe('faq-getting-started');
    });

    it('should convert messy user input', () => {
      expect(slugify('   !!!SALE!!!   50% OFF!!!   ')).toBe('sale-50-off');
    });
  });

  describe('numbers and alphanumeric', () => {
    it('should handle string starting with number', () => {
      expect(slugify('5 ways to improve')).toBe('5-ways-to-improve');
    });

    it('should handle string ending with number', () => {
      expect(slugify('version 2')).toBe('version-2');
    });

    it('should handle only numbers', () => {
      expect(slugify('123456')).toBe('123456');
    });

    it('should handle alphanumeric mix', () => {
      expect(slugify('abc123def456')).toBe('abc123def456');
    });
  });
});
