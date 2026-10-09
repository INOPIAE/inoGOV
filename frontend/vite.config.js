import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    pool: 'threads',
    maxWorkers: 2,
    testTimeout: 30000,
    include: ['src/**/*.test.js'],
  },
})
