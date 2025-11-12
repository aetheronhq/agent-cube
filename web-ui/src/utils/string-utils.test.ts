import { capitalize, truncate, slugify } from './string-utils';

function assert(condition: boolean, message: string) {
  if (!condition) {
    throw new Error(`Test failed: ${message}`);
  }
}

function testCapitalize() {
  assert(capitalize('hello') === 'Hello', 'capitalize("hello") should return "Hello"');
  assert(capitalize('world') === 'World', 'capitalize("world") should return "World"');
  assert(capitalize('') === '', 'capitalize("") should return ""');
  assert(capitalize('a') === 'A', 'capitalize("a") should return "A"');
  assert(capitalize('HELLO') === 'HELLO', 'capitalize("HELLO") should return "HELLO"');
  console.log('✓ capitalize tests passed');
}

function testTruncate() {
  assert(truncate('hello world', 8) === 'hello...', 'truncate("hello world", 8) should return "hello..."');
  assert(truncate('hello', 10) === 'hello', 'truncate("hello", 10) should return "hello"');
  assert(truncate('hello', 5) === 'hello', 'truncate("hello", 5) should return "hello"');
  assert(truncate('hello world', 5) === 'he...', 'truncate("hello world", 5) should return "he..."');
  assert(truncate('', 5) === '', 'truncate("", 5) should return ""');
  console.log('✓ truncate tests passed');
}

function testSlugify() {
  assert(slugify('Hello World') === 'hello-world', 'slugify("Hello World") should return "hello-world"');
  assert(slugify('  Hello  World  ') === 'hello-world', 'slugify with extra spaces should work');
  assert(slugify('Hello@World!') === 'helloworld', 'slugify should remove special characters');
  assert(slugify('Hello_World') === 'hello-world', 'slugify should convert underscores to hyphens');
  assert(slugify('Hello---World') === 'hello-world', 'slugify should collapse multiple hyphens');
  assert(slugify('') === '', 'slugify("") should return ""');
  console.log('✓ slugify tests passed');
}

export function runAllTests() {
  console.log('Running string-utils tests...\n');
  try {
    testCapitalize();
    testTruncate();
    testSlugify();
    console.log('\n✅ All tests passed!');
  } catch (error) {
    console.error('\n❌ Test suite failed:', error);
    throw error;
  }
}

runAllTests();
