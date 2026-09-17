// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from '@playwright/test';

test('landing page renders and links to main sections', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Welcome to PeriHub' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'PeriHub' }).first()).toBeVisible();
});

test('tools page renders all four calculators', async ({ page }) => {
  await page.goto('/tools');
  await expect(page.getByRole('heading', { name: 'Tools' })).toBeVisible();
  await expect(page.getByText('Conversion of elastic isotropic constants').first()).toBeVisible();
  await expect(page.getByText('Typical Conversions')).toBeVisible();
  await expect(page.getByText('Amplitude Generator')).toBeVisible();
});

test('legal pages render without crashing', async ({ page }) => {
  for (const path of ['/impressum', '/privacy', '/copyright', '/accessibility']) {
    await page.goto(path);
    await expect(page.locator('article.legal-page')).toBeVisible();
  }
});

test('unknown route shows 404', async ({ page }) => {
  await page.goto('/this-route-does-not-exist');
  await expect(page.getByText('404')).toBeVisible();
});
