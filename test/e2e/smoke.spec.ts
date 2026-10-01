// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { expect, test } from '@playwright/test';

// No backend in e2e: pretend guest access is on so initAuth() gets a session instead of
// redirecting to /auth/login. /auth/me answers as a member so the full nav (incl. Models) shows.
test.beforeEach(async ({ page }) => {
  await page.route('**/api/config/public', (route) =>
    route.fulfill({
      json: {
        deployment_mode: 'community',
        guest_access: true,
        guest_limits: null,
        oauth_enabled: false
      }
    })
  );
  await page.route('**/api/auth/guest', (route) =>
    route.fulfill({
      json: { token: 'e2e-token', user_id: 'e2e', display_name: 'e2e', role: 'member' }
    })
  );
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({
      json: {
        user_id: 'e2e',
        email: null,
        display_name: 'e2e',
        role: 'member',
        auth_provider: 'local',
        org_id: null
      }
    })
  );
});

test('landing page renders and links to main sections', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1, name: /Peridynamics/ })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Open the editor' })).toHaveAttribute(
    'href',
    '/perihub'
  );
  const nav = page.getByRole('navigation').first();
  for (const name of ['PeriHub', 'Models', 'Tools', 'Publications']) {
    await expect(nav.getByRole('link', { name })).toBeVisible();
  }
});

test('tools page renders all four calculators', async ({ page }) => {
  await page.goto('/tools');
  await expect(page.getByRole('heading', { level: 1, name: 'Tools' })).toBeVisible();
  for (const name of [
    'Unit systems',
    'Isotropic elastic constants',
    'Orthotropic matrix',
    'Load amplitude'
  ]) {
    await expect(page.getByRole('heading', { level: 2, name })).toBeVisible();
  }
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

test('workflow page loads with a working-page title', async ({ page }) => {
  await page.goto('/perihub');
  await expect(page).toHaveTitle(/Model Builder/);
});

test('protected route sends anonymous visitors to login', async ({ page }) => {
  await page.route('**/api/config/public', (route) =>
    route.fulfill({
      json: {
        deployment_mode: 'community',
        guest_access: false,
        guest_limits: null,
        oauth_enabled: false
      }
    })
  );
  await page.goto('/auth/login');
  await page.goto('/perihub');
  await expect(page).toHaveURL(/\/auth\/login/);
});

test('header nav link to the editor also gets guarded client-side', async ({ page }) => {
  await page.route('**/api/config/public', (route) =>
    route.fulfill({
      json: {
        deployment_mode: 'community',
        guest_access: false,
        guest_limits: null,
        oauth_enabled: false
      }
    })
  );
  await page.goto('/auth/login');
  await page.locator('header a[href="/perihub"]').first().click();
  await expect(page).toHaveURL(/\/auth\/login/);
});
