import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
  },
  resolve: {
    alias: {
      '@/utils': path.resolve(__dirname, './src/utils/index.ts'),
    },
  },
});
