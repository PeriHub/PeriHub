// @ts-check
const { test, expect } = require("@playwright/test");

test("Landing page", async ({ page }) => {
  await page.goto("");

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/PeriHub/);
  await expect(page.getByRole("main")).toContainText("Welcome to PeriHub!");
});

test("Compact Tension", async ({ page }) => {
  await page.goto("/perihub");

  await page.getByLabel('Expand "Model"').click();
  await page
    .locator("label")
    .filter({ hasText: "DogboneModel" })
    .locator("i")
    .click();
  await page
    .getByRole("option", { name: "CompactTension" })
    .locator("div")
    .nth(2)
    .click();
  await page.locator("button:nth-child(7)").first().click();
  await page.locator("button:nth-child(8)").first().click();
  await expect(page.getByTestId("textarea")).toHaveValue(
    "PeriLab:\n  Blocks:\n    block_1:\n      Damage Model: Damage\n      Density: 2.81e-09\n      Horizon: 2.7939356435643563\n      Material Model: Aluminium\n    block_2:\n      Density: 2.81e-09\n      Horizon: 2.7939356435643563\n      Material Model: Aluminium\n    block_3:\n      Density: 2.81e-09\n      Horizon: 2.7939356435643563\n      Material Model: Aluminium\n    block_4:\n      Density: 2.81e-09\n      Horizon: 2.7939356435643563\n      Material Model: Aluminium\n    block_5:\n      Density: 2.81e-09\n      Horizon: 2.7939356435643563\n      Material Model: Aluminium\n  Boundary Conditions:\n    BC_1:\n      Coordinate: y\n      Node Set: Node Set 1\n      Type: Force Densities\n      Value: 50000*t\n    BC_2:\n      Coordinate: y\n      Node Set: Node Set 2\n      Type: Force Densities\n      Value: -50000*t\n  Compute Class Parameters:\n    External_Displacement:\n      Block: block_2\n      Calculation Type: Maximum\n      Compute Class: Block_Data\n      Variable: Displacements\n    External_Force:\n      Block: block_2\n      Calculation Type: Sum\n      Compute Class: Block_Data\n      Variable: Forces\n  Discretization:\n    Bond Filters:\n      bf_1:\n        Bottom Length: 56.75\n        Bottom Unit Vector X: 1.0\n        Bottom Unit Vector Y: 0.0\n        Bottom Unit Vector Z: 0.0\n        Lower Left Corner X: -0.5\n        Lower Left Corner Y: 0.0\n        Lower Left Corner Z: -1.0\n        Normal X: 0.0\n        Normal Y: 1.0\n        Normal Z: 0.0\n        Side Length: 2.0\n        Type: Rectangular_Plane\n    Input Mesh File: CompactTension.txt\n    Node Sets:\n      Node Set 1: ns_CompactTension_1.txt\n      Node Set 2: ns_CompactTension_2.txt\n    Type: Text File\n  Outputs:\n    Output1:\n      Number of Output Steps: 100\n      Output File Type: Exodus\n      Output Filename: CompactTension_Output1\n      Output Variables:\n        Damage: true\n        Displacements: true\n        External_Displacement: true\n        External_Force: true\n  Physics:\n    Damage Models:\n      Damage:\n        Critical Value: 5.578800557880057\n        Damage Model: Critical Energy\n    Material Models:\n      Aluminium:\n        Material Model: PD Solid Elastic\n        Poisson's Ratio: 0.33\n        Symmetry: isotropic plane stress\n        Yield Stress: 74.0\n        Young's Modulus: 71700.0\n        Zero Energy Control: Global\n  Solver:\n    Damage Models: true\n    Final Time: 0.0001\n    Initial Time: 0.0\n    Material Models: true\n    Numerical Damping: 5.0e-06\n    Thermal Models: false\n    Verlet:\n      Safety Factor: 0.95\n"
  );
});
