import { defineConfig } from '@playwright/test'

export default defineConfig({
  use: { baseURL: 'http://127.0.0.1:3000' },
  webServer: {
    command: 'pnpm dev',
    cwd: __dirname,
    port: 3000,
    reuseExistingServer: true
  }
})
