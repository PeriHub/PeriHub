import { expect, test, type Page } from '@playwright/test';

// No backend in e2e: pretend guest access is on so initAuth() gets a session instead of
// redirecting to /auth/login. /auth/me answers as a member so the full nav (incl. Models) shows.
test.beforeEach(async ({ page }) => {
  // The editor auto-launches its driver.js tour on a first visit; its overlay would swallow clicks.
  await page.addInitScript(() => localStorage.setItem('periHubTourSeen', 'true'));
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

// A first visit to the editor loads the default model's config from the backend, which replaces modelData
// whenever it arrives - wait for it before editing, or it silently undoes the edits.
async function gotoEditor(page: Page) {
  const configLoaded = page.waitForResponse((r) =>
    /\/models\/[^/]+\/config$/.test(new URL(r.url()).pathname)
  );
  await page.goto('/perihub');
  await configLoaded;
}

// The Solver/Material forms are generated from src/lib/perilab/schema.json (npm run perilab-schema) - this
// pins the resulting show/hide behavior (x-perilab-when) to the schema's actual content instead of only to
// perilab-schema.test.ts's parsing of it.
test('solver and material forms follow the PeriLab schema', async ({ page }) => {
  await gotoEditor(page);
  await page.getByRole('button', { name: 'Solver' }).click();
  // Final Time is required: ParamLabel appends an aria-hidden "*" to the <label> text, which getByLabel's
  // exact match compares against literally - getByRole (name from the accessible-name algorithm, which drops
  // aria-hidden content) avoids that.
  await expect(page.getByRole('spinbutton', { name: 'Final Time', exact: true })).toBeVisible();
  await expect(page.getByRole('spinbutton', { name: 'Number of Steps' })).toHaveCount(0); // default solver is Verlet
  await page.getByRole('combobox', { name: 'Solver', exact: true }).selectOption('Static');
  await expect(page.getByRole('spinbutton', { name: 'Number of Steps' })).toBeVisible();

  // Close the Solver panel first: its own "Duplicate ..." button would otherwise match the add button below
  // before the Material panel has rendered. Not exact: the accordion trigger's accessible name also carries its
  // status dot's title (e.g. "Material Required fields filled in"), so anchor it instead.
  await page.getByRole('button', { name: /^Solver\b/ }).click();
  await expect(page.getByRole('spinbutton', { name: 'Number of Steps' })).toHaveCount(0);
  await page.getByRole('button', { name: /^Material\b/ }).click();
  // The materials depend on the default model (PeriHubLogo from the backend has none), so add one and check that
  // (the last): "Add material" creates an isotropic plane stress PD Solid Elastic one, "Duplicate <last>" copies
  // an isotropic default one. getByRole for the same reason as Final Time: C11 is required once anisotropic.
  await page.getByRole('button', { name: /^(Add material|Duplicate )/ }).click();
  await expect(
    page.getByRole('spinbutton', { name: "Young's Modulus", exact: true }).last()
  ).toBeVisible();
  await expect(page.getByRole('spinbutton', { name: 'C11', exact: true })).toHaveCount(0);
  await page
    .getByRole('combobox', { name: 'Symmetry', exact: true })
    .last()
    .selectOption('anisotropic');
  await expect(page.getByRole('spinbutton', { name: 'C11', exact: true }).last()).toBeVisible();
});

test('a missing required value is marked and counted', async ({ page }) => {
  await gotoEditor(page);
  await page.getByRole('button', { name: 'Blocks' }).click();
  await page.getByLabel('Density of Part').fill('');
  await page.getByLabel('Density of Part').blur();
  await expect(page.getByText(/1 missing/)).toBeVisible();
});
