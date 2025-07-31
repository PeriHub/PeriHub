// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

// @ts-check
const { test, expect } = require('@playwright/test');

test('Landing page', async ({ page }) => {
  await page.goto('');

  // Expect a title 'to contain' a substring.
  await expect(page).toHaveTitle(/PeriHub/);
  await expect(page.getByRole('main')).toMatchAriaSnapshot(`
    - main:
      - text: Welcome to PeriHub! PeriHub is a platform that provides a numerical implementation of the peridynamic theory. It is an extension of the open source PeriLab software. Peridynamics is a non-local theory that overcomes discontinuity problems of the classical theory of continuum mechanics. It is an effective method to model fracture mechanics problems.
      - link:
        - /url: /perihub
        - img: PeriHub
      - link:
        - /url: https://perihub.github.io/PeriHub/
        - img: Guide
      - link:
        - /url: /publications
        - img: Publications
      - link:
        - /url: /tools
        - img: Tools
      - link:
        - /url: /api/docs
        - img: API
      - link:
        - /url: https://github.com/PeriHub/PeriHub
        - img: GitHub
      - link:
        - /url: https://perilab-results.nimbus-extern.dlr.de
        - img: PeriLab-Results
      - link:
        - /url: https://www.youtube.com/@PeriHub
        - img: YouTube
    `);
});

test('Tools', async ({ page }) => {
  await page.goto('tools');
  await page
    .locator('label')
    .filter({ hasText: /^Young's Modulus\(E\)$/ })
    .getByLabel("Young's Modulus(E)")
    .click();
  await page
    .locator('label')
    .filter({ hasText: /^Young's Modulus\(E\)$/ })
    .getByLabel("Young's Modulus(E)")
    .fill('3800');
  await page
    .locator('label')
    .filter({ hasText: /^Poisson's Ratio\(v\)$/ })
    .getByLabel("Poisson's Ratio(v)")
    .click();
  await page
    .locator('label')
    .filter({ hasText: /^Poisson's Ratio\(v\)$/ })
    .getByLabel("Poisson's Ratio(v)")
    .fill('0.33');
  await expect(
    page.getByRole('textbox', { name: 'Bulk Modulus (K)' }).nth(1)
  ).toHaveValue('3.7254901960784314e+3');
  await expect(
    page.getByRole('textbox', { name: 'Shear Modulus (G)' }).nth(1)
  ).toHaveValue('1.4285714285714284e+3');
  await expect(
    page.getByRole('textbox', { name: 'P-wave modulus (M)' }).nth(1)
  ).toHaveValue('5.6302521008403355e+3');
  await expect(
    page.getByRole('textbox', { name: "Lamé's first parameter(m)" }).nth(1)
  ).toHaveValue('2.773109243697479e+3');
});

test('Compact Tension', async ({ page }) => {
  await page.goto('/perihub');

  await page.getByRole('button', { name: 'Expand "Model"' }).click();
  await page
    .locator('label')
    .filter({ hasText: 'DogboneModel' })
    .locator('i')
    .click();
  await page
    .getByRole('option', { name: 'Compact Tension', exact: true })
    .locator('div')
    .nth(2)
    .click();
  await page.locator('button:nth-child(5)').first().click();
  await page.locator('button:nth-child(6)').first().click();
  await expect(page.getByTestId('textarea')).toHaveValue(
    "PeriLab:\n  Blocks:\n    Bottom_BC:\n      Block ID: 3\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: BC\n    Bottom_Part:\n      Block ID: 5\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: Aluminium\n    Part:\n      Block ID: 1\n      Damage Model: Damage\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: Aluminium\n    Top_BC:\n      Block ID: 2\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: BC\n    Top_Part:\n      Block ID: 4\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: Aluminium\n  Boundary Conditions:\n    BC_1:\n      Coordinate: y\n      Node Set: Node Set 1\n      Type: Dirichlet\n      Value: 1000*t\n      Variable: Displacements\n    BC_2:\n      Coordinate: y\n      Node Set: Node Set 2\n      Type: Dirichlet\n      Value: -1000*t\n      Variable: Displacements\n  Compute Class Parameters:\n    External_Displacement:\n      Block: Top_BC\n      Calculation Type: Maximum\n      Compute Class: Block_Data\n      Variable: Displacements\n    External_Force:\n      Block: Bottom_BC\n      Calculation Type: Sum\n      Compute Class: Block_Data\n      Variable: Forces\n  Discretization:\n    Bond Filters:\n      bf_1:\n        Bottom Length: 56.75\n        Bottom Unit Vector X: 1.0\n        Bottom Unit Vector Y: 0.0\n        Bottom Unit Vector Z: 0.0\n        Lower Left Corner X: -0.5\n        Lower Left Corner Y: 0.0\n        Lower Left Corner Z: -2.0\n        Normal X: 0.0\n        Normal Y: 1.0\n        Normal Z: 0.0\n        Side Length: 4.0\n        Type: Rectangular_Plane\n    Input Mesh File: CompactTension.txt\n    Node Sets:\n      Node Set 1: ns_CompactTension_1.txt\n      Node Set 2: ns_CompactTension_2.txt\n    Type: Text File\n  Models:\n    Damage Models:\n      Damage:\n        Critical Value: 5.714285714285715\n        Damage Model: Critical Energy\n        Only Tension: true\n        Thickness: 1.0\n    Material Models:\n      Aluminium:\n        Material Model: Correspondence Elastic + Correspondence Plastic\n        Poisson's Ratio: 0.35\n        Symmetry: isotropic plane stress\n        Yield Stress: 350.0\n        Young's Modulus: 70000.0\n        Zero Energy Control: Global\n      BC:\n        Material Model: PD Solid Elastic\n        Poisson's Ratio: 0.35\n        Symmetry: isotropic plane stress\n        Young's Modulus: 200000.0\n        Zero Energy Control: Global\n  Outputs:\n    Output1:\n      Number of Output Steps: 100\n      Output File Type: Exodus\n      Output Filename: CompactTension_Output1\n      Output Variables:\n        Cauchy Stress: true\n        Damage: true\n        Displacements: true\n        External_Displacement: true\n        External_Force: true\n        Number of Neighbors: true\n        Strain: true\n    Output2:\n      Number of Output Steps: 500\n      Output File Type: CSV\n      Output Filename: CompactTension_Output2\n      Output Variables:\n        External_Displacement: true\n        External_Force: true\n  Solver:\n    Calculate Strain: true\n    Calculate von Mises stress: true\n    Damage Models: true\n    Final Time: 0.0005\n    Initial Time: 0.0\n    Material Models: true\n    Verlet:\n      Safety Factor: 0.95\n"
  );
});
