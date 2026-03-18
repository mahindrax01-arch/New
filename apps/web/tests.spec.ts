import { test, expect } from '@playwright/test'

test('landing page renders headline', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Messenger-grade collaboration')).toBeVisible()
})
