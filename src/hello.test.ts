import { strict as assert } from 'node:assert';
import { test } from 'node:test';
import { hello } from './hello';

test('hello returns expected message', () => {
  assert.equal(hello(), 'Hello from Agent Cube!');
});
