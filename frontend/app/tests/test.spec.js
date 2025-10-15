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

test('Model generation', async ({ page }) => {
  await page.goto('/perihub');
  await page.locator('#ModelActions > button:nth-child(5)').first().click();
  await page.locator('button:nth-child(6)').first().click();
  await expect(page.getByTestId('textarea')).toHaveValue(
    "PeriLab:\n  Blocks:\n    Bottom_BC:\n      Block ID: 3\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: BC\n    Bottom_Part:\n      Block ID: 5\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: Aluminium\n    Part:\n      Block ID: 1\n      Damage Model: Damage\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: Aluminium\n    Top_BC:\n      Block ID: 2\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: BC\n    Top_Part:\n      Block ID: 4\n      Density: 2.699e-09\n      Horizon: 2.3205445544554455\n      Material Model: Aluminium\n  Boundary Conditions:\n    BC_1:\n      Coordinate: y\n      Node Set: Node Set 1\n      Type: Dirichlet\n      Value: 1000*t\n      Variable: Displacements\n    BC_2:\n      Coordinate: y\n      Node Set: Node Set 2\n      Type: Dirichlet\n      Value: -1000*t\n      Variable: Displacements\n  Compute Class Parameters:\n    External_Displacement:\n      Block: Top_BC\n      Calculation Type: Maximum\n      Compute Class: Block_Data\n      Variable: Displacements\n    External_Force:\n      Block: Bottom_BC\n      Calculation Type: Sum\n      Compute Class: Block_Data\n      Variable: Forces\n  Discretization:\n    Bond Filters:\n      bf_1:\n        Bottom Length: 56.75\n        Bottom Unit Vector X: 1.0\n        Bottom Unit Vector Y: 0.0\n        Bottom Unit Vector Z: 0.0\n        Lower Left Corner X: -0.5\n        Lower Left Corner Y: 0.0\n        Lower Left Corner Z: -2.0\n        Normal X: 0.0\n        Normal Y: 1.0\n        Normal Z: 0.0\n        Side Length: 4.0\n        Type: Rectangular_Plane\n    Input Mesh File: CompactTension.txt\n    Node Sets:\n      Node Set 1: ns_CompactTension_1.txt\n      Node Set 2: ns_CompactTension_2.txt\n    Type: Text File\n  Models:\n    Damage Models:\n      Damage:\n        Critical Value: 5.714285714285715\n        Damage Model: Critical Energy\n        Only Tension: true\n        Thickness: 1.0\n    Material Models:\n      Aluminium:\n        Material Model: Correspondence Elastic + Correspondence Plastic\n        Poisson's Ratio: 0.35\n        Symmetry: isotropic plane stress\n        Yield Stress: 350.0\n        Young's Modulus: 70000.0\n        Zero Energy Control: Global\n      BC:\n        Material Model: PD Solid Elastic\n        Poisson's Ratio: 0.35\n        Symmetry: isotropic plane stress\n        Young's Modulus: 200000.0\n        Zero Energy Control: Global\n  Outputs:\n    Output1:\n      Number of Output Steps: 100\n      Output File Type: Exodus\n      Output Filename: CompactTension_Output1\n      Output Variables:\n        Cauchy Stress: true\n        Damage: true\n        Displacements: true\n        External_Displacement: true\n        External_Force: true\n        Number of Neighbors: true\n        Strain: true\n    Output2:\n      Number of Output Steps: 500\n      Output File Type: CSV\n      Output Filename: CompactTension_Output2\n      Output Variables:\n        External_Displacement: true\n        External_Force: true\n  Solver:\n    Calculate Strain: true\n    Calculate von Mises stress: true\n    Damage Models: true\n    Final Time: 0.0005\n    Initial Time: 0.0\n    Material Models: true\n    Verlet:\n      Safety Factor: 0.95\n"
  );
  // await page.getByText('Results').click();
  // await page
  //   .locator('#ViewComp label')
  //   .filter({ hasText: 'DisplacementsVariablearrow_drop_down' })
  //   .locator('i')
  //   .click();
  // await page.getByText('Damage').click();
  await page.getByRole('button', { name: 'Expand "Model"' }).click();
  await page
    .locator('label')
    .filter({ hasText: 'Compact TenisonModel' })
    .locator('i')
    .click();
  await page
    .getByRole('option', { name: 'Dogbone' })
    .locator('div')
    .nth(2)
    .click();
  await page.locator('#ModelActions > button:nth-child(5)').first().click();
  await page.locator('button:nth-child(6)').first().click();
  await expect(page.getByTestId('textarea')).toHaveValue(
    "PeriLab:\n  Blocks:\n    block_1:\n      Block ID: 1\n      Density: 1.4e-08\n      Horizon: 0.25\n      Material Model: Aluminium\n    block_2:\n      Block ID: 2\n      Density: 1.4e-08\n      Horizon: 0.25\n      Material Model: Aluminium\n    block_3:\n      Block ID: 3\n      Damage Model: Damage\n      Density: 1.4e-08\n      Horizon: 0.25\n      Material Model: Aluminium\n    block_4:\n      Block ID: 4\n      Density: 1.4e-08\n      Horizon: 0.25\n      Material Model: Aluminium\n    block_5:\n      Block ID: 5\n      Density: 1.4e-08\n      Horizon: 0.25\n      Material Model: Aluminium\n  Boundary Conditions:\n    BC_1:\n      Coordinate: x\n      Node Set: Node Set 1\n      Type: Dirichlet\n      Value: 0*t\n      Variable: Displacements\n    BC_2:\n      Coordinate: x\n      Node Set: Node Set 2\n      Type: Dirichlet\n      Value: 0.5*t\n      Variable: Displacements\n  Compute Class Parameters:\n    External_Displacement:\n      Block: block_5\n      Calculation Type: Maximum\n      Compute Class: Block_Data\n      Variable: Displacements\n    External_Force:\n      Block: block_5\n      Calculation Type: Sum\n      Compute Class: Block_Data\n      Variable: Forces\n  Discretization:\n    Input Mesh File: Dogbone.txt\n    Node Sets:\n      Node Set 1: ns_Dogbone_1.txt\n      Node Set 2: ns_Dogbone_2.txt\n    Type: Text File\n  Models:\n    Damage Models:\n      Damage:\n        Critical Value: 1.0e-08\n        Damage Model: Critical Energy\n        Thickness: 1.0\n    Material Models:\n      Aluminium:\n        Material Model: PD Solid Elastic\n        Poisson's Ratio: 0.33\n        Symmetry: isotropic plane stress\n        Young's Modulus: 700000.0\n        Zero Energy Control: Global\n  Outputs:\n    Output1:\n      Number of Output Steps: 100\n      Output File Type: Exodus\n      Output Filename: Dogbone_Output1\n      Output Variables:\n        Damage: true\n        Displacements: true\n        External_Displacement: true\n        External_Force: true\n        Forces: true\n        von Mises Stress: true\n    Output2:\n      Number of Output Steps: 100\n      Output File Type: CSV\n      Output Filename: Dogbone_Output2\n      Output Variables:\n        External_Displacement: true\n        External_Force: true\n  Solver:\n    Calculate von Mises stress: true\n    Damage Models: true\n    Final Time: 1.0e-05\n    Initial Time: 0.0\n    Material Models: true\n    Verlet:\n      Safety Factor: 0.9\n"
  );
  await page
    .locator('label')
    .filter({ hasText: 'DogboneModel' })
    .locator('i')
    .click();
  await page
    .getByRole('option', { name: 'DCB Model' })
    .locator('div')
    .nth(2)
    .click();
  await page.locator('#ModelActions > button:nth-child(5)').first().click();
  await page.locator('button:nth-child(6)').first().click();
  await expect(page.getByTestId('textarea')).toHaveValue(
    "PeriLab:\n  Blocks:\n    Bottom_BC:\n      Block ID: 4\n      Density: 2.699e-09\n      Horizon: 1.2376237623762376\n      Material Model: Aluminium\n    Bottom_Part:\n      Block ID: 1\n      Damage Model: Damage\n      Density: 2.699e-09\n      Horizon: 1.2376237623762376\n      Material Model: Aluminium\n    Top_BC:\n      Block ID: 3\n      Density: 2.699e-09\n      Horizon: 1.2376237623762376\n      Material Model: Aluminium\n    Top_Part:\n      Block ID: 2\n      Damage Model: Damage\n      Density: 2.699e-09\n      Horizon: 1.2376237623762376\n      Material Model: Aluminium\n  Boundary Conditions:\n    BC_1:\n      Coordinate: y\n      Node Set: Node Set 1\n      Type: Dirichlet\n      Value: 100*t\n      Variable: Displacements\n    BC_2:\n      Coordinate: y\n      Node Set: Node Set 2\n      Type: Dirichlet\n      Value: -100*t\n      Variable: Displacements\n  Compute Class Parameters:\n    External_Displacement:\n      Block: Top_BC\n      Calculation Type: Maximum\n      Compute Class: Block_Data\n      Variable: Displacements\n    External_Force:\n      Block: Bottom_BC\n      Calculation Type: Sum\n      Compute Class: Block_Data\n      Variable: Forces\n  Discretization:\n    Bond Filters:\n      bf_1:\n        Bottom Length: 6.0\n        Bottom Unit Vector X: 1.0\n        Bottom Unit Vector Y: 0.0\n        Bottom Unit Vector Z: 0.0\n        Lower Left Corner X: -0.75\n        Lower Left Corner Y: 0.15\n        Lower Left Corner Z: -4.0\n        Normal X: 0.0\n        Normal Y: 1.0\n        Normal Z: 0.0\n        Side Length: 8.0\n        Type: Rectangular_Plane\n    Input Mesh File: DCBmodel.txt\n    Node Sets:\n      Node Set 1: ns_DCBmodel_1.txt\n      Node Set 2: ns_DCBmodel_2.txt\n    Type: Text File\n  Models:\n    Damage Models:\n      Damage:\n        Critical Value: 5.714285714285715\n        Damage Model: Critical Energy\n        Only Tension: true\n        Thickness: 1.0\n    Material Models:\n      Aluminium:\n        Material Model: Correspondence Elastic + Correspondence Plastic\n        Poisson's Ratio: 0.35\n        Symmetry: isotropic plane stress\n        Yield Stress: 350.0\n        Young's Modulus: 70000.0\n        Zero Energy Control: Global\n  Outputs:\n    Output1:\n      Number of Output Steps: 100\n      Output File Type: Exodus\n      Output Filename: DCBmodel_Output1\n      Output Variables:\n        Cauchy Stress: true\n        Damage: true\n        Displacements: true\n        External_Displacement: true\n        External_Force: true\n        Number of Neighbors: true\n        Strain: true\n    Output2:\n      Number of Output Steps: 500\n      Output File Type: CSV\n      Output Filename: DCBmodel_Output2\n      Output Variables:\n        External_Displacement: true\n        External_Force: true\n  Solver:\n    Calculate Strain: true\n    Calculate von Mises stress: true\n    Damage Models: true\n    Final Time: 0.0005\n    Initial Time: 0.0\n    Material Models: true\n    Verlet:\n      Safety Factor: 0.95\n"
  );
  // await page
  //   .locator('label')
  //   .filter({ hasText: 'DCB ModelModel' })
  //   .locator('i')
  //   .click();
  // await page
  //   .getByRole('option', { name: 'Kalthoff-Winkler' })
  //   .locator('div')
  //   .nth(2)
  //   .click();
  // await page.locator('#ModelActions > button:nth-child(5)').first().click();
  // await page.locator('button:nth-child(6)').first().click();
  // await expect(page.getByTestId('textarea')).toHaveValue(
  //   "PeriLab:\n  Blocks:\n    block_1:\n      Block ID: 1\n      Damage Model: PMMADamage\n      Density: 8.0e-09\n      Horizon: 2.4752475247524752\n      Material Model: PMMA\n    block_2:\n      Block ID: 2\n      Density: 8.0e-09\n      Horizon: 2.4752475247524752\n      Material Model: PMMA\n    block_3:\n      Block ID: 3\n      Density: 8.0e-09\n      Horizon: 2.4752475247524752\n      Material Model: PMMA\n  Boundary Conditions:\n    BC_1:\n      Coordinate: x\n      Node Set: Node Set 1\n      Type: Dirichlet\n      Value: 32e+3\n      Variable: Velocity\n  Discretization:\n    Bond Filters:\n      bf_1:\n        Bottom Length: 50.1\n        Bottom Unit Vector X: 1.0\n        Bottom Unit Vector Y: 0.0\n        Bottom Unit Vector Z: 0.0\n        Lower Left Corner X: -0.5\n        Lower Left Corner Y: 25.247524752475247\n        Lower Left Corner Z: -10.0\n        Normal X: 0.0\n        Normal Y: 1.0\n        Normal Z: 0.0\n        Side Length: 20.0\n        Type: Rectangular_Plane\n      bf_2:\n        Bottom Length: 50.1\n        Bottom Unit Vector X: 1.0\n        Bottom Unit Vector Y: 0.0\n        Bottom Unit Vector Z: 0.0\n        Lower Left Corner X: -0.5\n        Lower Left Corner Y: -25.247524752475247\n        Lower Left Corner Z: -10.0\n        Normal X: 0.0\n        Normal Y: 1.0\n        Normal Z: 0.0\n        Side Length: 20.0\n        Type: Rectangular_Plane\n    Input Mesh File: Kalthoff-Winkler.txt\n    Node Sets:\n      Node Set 1: ns_Kalthoff-Winkler_1.txt\n    Type: Text File\n  Models:\n    Damage Models:\n      PMMADamage:\n        Critical Value: 25.0\n        Damage Model: Critical Energy\n        Only Tension: true\n    Material Models:\n      PMMA:\n        Material Model: Bond-based Elastic\n        Poisson's Ratio: 0.333\n        Symmetry: isotropic plane stress\n        Young's Modulus: 191000.0\n        Zero Energy Control: Global\n  Outputs:\n    Output1:\n      Number of Output Steps: 100\n      Output File Type: Exodus\n      Output Filename: Kalthoff-Winkler_Output1\n      Output Variables:\n        Damage: true\n        Displacements: true\n        Forces: true\n        Number of Neighbors: true\n        Velocity: true\n  Solver:\n    Damage Models: true\n    Final Time: 0.0001\n    Initial Time: 0.0\n    Material Models: true\n    Numerical Damping: 5.0e-06\n    Thermal Models: false\n    Verlet:\n      Safety Factor: 0.95\n"
  // );
  // await page
  //   .locator('label')
  //   .filter({ hasText: 'Kalthoff-WinklerModel' })
  //   .locator('i')
  //   .click();
  // await page
  //   .getByRole('option', { name: 'Plate with Hole' })
  //   .locator('div')
  //   .nth(2)
  //   .click();
  // await page.locator('#ModelActions > button:nth-child(5)').first().click();
  // await page.locator('button:nth-child(6)').first().click();
  // await expect(page.getByTestId('textarea')).toHaveValue(
  //   "PeriLab:\n  Blocks:\n    block_1:\n      Block ID: 1\n      Damage Model: PMMADamage\n      Density: 8.0e-09\n      Horizon: 1.2376237623762376\n      Material Model: PMMA\n    block_2:\n      Block ID: 2\n      Density: 8.0e-09\n      Horizon: 1.2376237623762376\n      Material Model: PMMA\n    block_3:\n      Block ID: 3\n      Density: 8.0e-09\n      Horizon: 1.2376237623762376\n      Material Model: PMMA\n  Boundary Conditions:\n    BC_1:\n      Coordinate: y\n      Node Set: Node Set 1\n      Type: Dirichlet\n      Value: -1*t\n      Variable: Displacements\n    BC_2:\n      Coordinate: y\n      Node Set: Node Set 2\n      Type: Dirichlet\n      Value: 1*t\n      Variable: Displacements\n  Discretization:\n    Input Mesh File: PlateWithHole.txt\n    Node Sets:\n      Node Set 1: ns_PlateWithHole_1.txt\n      Node Set 2: ns_PlateWithHole_2.txt\n    Type: Text File\n  Models:\n    Damage Models:\n      PMMADamage:\n        Critical Value: 0.015\n        Damage Model: Critical Stretch\n        Only Tension: true\n        Thickness: 10.0\n    Material Models:\n      PMMA:\n        Material Model: Bond-based Elastic\n        Poisson's Ratio: 0.333\n        Symmetry: isotropic plane stress\n        Young's Modulus: 191000.0\n        Zero Energy Control: Global\n  Outputs:\n    Output1:\n      Number of Output Steps: 100\n      Output File Type: Exodus\n      Output Filename: PlateWithHole_Output1\n      Output Variables:\n        Damage: true\n        Displacements: true\n        Forces: true\n        Number of Neighbors: true\n  Solver:\n    Damage Models: true\n    Final Time: 0.0001\n    Initial Time: 0.0\n    Material Models: true\n    Verlet:\n      Safety Factor: 0.95\n"
  // );
  // await page
  //   .locator('label')
  //   .filter({ hasText: 'Plate with HoleModel' })
  //   .locator('i')
  //   .click();
  // await page
  //   .getByRole('option', { name: 'ENFmodel' })
  //   .locator('div')
  //   .nth(2)
  //   .click();
  // await page.locator('#ModelActions > button:nth-child(5)').first().click();
  // await page.locator('button:nth-child(6)').first().click();
  // await expect(page.getByTestId('textarea')).toHaveValue(
  //   "PeriLab:\n  Blocks:\n    block_1:\n      Block ID: 1\n      Damage Model: Damage\n      Density: 2.81e-09\n      Horizon: 0.23809523809523808\n      Material Model: Aluminium\n    block_2:\n      Block ID: 2\n      Damage Model: Damage\n      Density: 2.81e-09\n      Horizon: 0.23809523809523808\n      Material Model: Aluminium\n    block_3:\n      Block ID: 3\n      Density: 2.81e-09\n      Horizon: 0.23809523809523808\n      Material Model: Aluminium\n    block_4:\n      Block ID: 4\n      Density: 2.81e-09\n      Horizon: 0.23809523809523808\n      Material Model: Aluminium\n    block_5:\n      Block ID: 5\n      Density: 2.81e-09\n      Horizon: 0.23809523809523808\n      Material Model: Aluminium\n    block_6:\n      Block ID: 6\n      Density: 2.81e-09\n      Horizon: 0.23809523809523808\n      Material Model: Aluminium\n    block_7:\n      Block ID: 7\n      Density: 2.81e-09\n      Horizon: 0.23809523809523808\n      Material Model: Aluminium\n    block_8:\n      Block ID: 8\n      Density: 2.81e-09\n      Horizon: 0.23809523809523808\n      Material Model: Aluminium\n  Boundary Conditions:\n    BC_1:\n      Coordinate: y\n      Node Set: Node Set 1\n      Type: Dirichlet\n      Value: -50000*t\n      Variable: Force Densities\n    BC_2:\n      Coordinate: y\n      Node Set: Node Set 2\n      Type: Dirichlet\n      Value: '0'\n      Variable: Displacements\n    BC_3:\n      Coordinate: y\n      Node Set: Node Set 3\n      Type: Dirichlet\n      Value: '0'\n      Variable: Displacements\n  Compute Class Parameters:\n    External_Displacements:\n      Block: block_3\n      Calculation Type: Maximum\n      Compute Class: Block_Data\n      Variable: Displacements\n    External_Forces:\n      Block: block_3\n      Calculation Type: Sum\n      Compute Class: Block_Data\n      Variable: Forces\n  Discretization:\n    Bond Filters:\n      bf_1:\n        Allow Contact: true\n        Bottom Length: 6.5\n        Bottom Unit Vector X: 1.0\n        Bottom Unit Vector Y: 0.0\n        Bottom Unit Vector Z: 0.0\n        Lower Left Corner X: -0.5\n        Lower Left Corner Y: 0.5\n        Lower Left Corner Z: -0.5\n        Normal X: 0.0\n        Normal Y: 1.0\n        Normal Z: 0.0\n        Side Length: 1.0\n        Type: Rectangular_Plane\n    Input Mesh File: ENFmodel.txt\n    Node Sets:\n      Node Set 1: ns_ENFmodel_1.txt\n      Node Set 2: ns_ENFmodel_2.txt\n      Node Set 3: ns_ENFmodel_3.txt\n    Type: Text File\n  Models:\n    Damage Models:\n      Damage:\n        Critical Value: 1.3947001394700143\n        Damage Model: Critical Energy\n        Interblock Damage:\n          Interblock Critical Value 1_2: 0.1\n        Thickness: 10.0\n    Material Models:\n      Aluminium:\n        Material Model: Correspondence Elastic\n        Poisson's Ratio: 0.33\n        Symmetry: isotropic plane stress\n        Young's Modulus: 71700.0\n        Zero Energy Control: Global\n  Outputs:\n    Output1:\n      Number of Output Steps: 100\n      Output File Type: Exodus\n      Output Filename: ENFmodel_Output1\n      Output Variables:\n        Damage: true\n        Displacements: true\n        External_Displacements: true\n        External_Forces: true\n        Forces: true\n        Number of Filtered Neighbors: true\n        Number of Neighbors: true\n        von Mises Stress: true\n  Solver:\n    Calculate von Mises stress: true\n    Damage Models: true\n    Final Time: 1.0e-06\n    Initial Time: 0.0\n    Material Models: true\n    Verlet:\n      Safety Factor: 0.95\n"
  // );
});

test('Tools Page', async ({ page }) => {
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

test('Model page', async ({ page }) => {
  await page.goto('/models');
  await page.getByRole('main').getByRole('button').click();
  await page.getByRole('textbox', { name: 'Model Name' }).click();
  await page.getByRole('textbox', { name: 'Model Name' }).fill('Test');
  await page.getByRole('textbox', { name: 'Description' }).click();
  await page
    .getByRole('textbox', { name: 'Description' })
    .fill('Test Description');
  await page.getByRole('button', { name: 'Create' }).click();
  await expect(page.getByTestId('textarea')).toHaveValue(
    '\n"""\n| title: Test\n| description: Test Description\n| author: user\n| requirements:\n| version: 0.1.0\n"""\nimport numpy as np\nfrom pydantic import BaseModel, Field\n\nfrom ..support.model.geometry import Geometry\n\nclass Valves(BaseModel):\n    DISCRETIZATION: float = Field(\n        default=21,\n        title="Discretization",\n        description="Discretization",\n    )\n    LENGTH: float = Field(\n        default=110,\n        title="Length",\n        description="Length",\n    )\n    HEIGHT: float = Field(\n        default=3,\n        title="Height",\n        description="Height",\n    )\n    WIDTH: float = Field(\n        default=25,\n        title="Width",\n        description="Width",\n    )\n\nclass main:\n    def __init__(\n        self,\n        valves,\n    ):\n        self.xbegin = 0\n        self.xend = valves["LENGTH"]\n        self.ybegin = 0\n        self.yend = valves["HEIGHT"]\n        self.discretization = valves["DISCRETIZATION"]\n        self.two_d = model_data.model.twoDimensional\n\n        if self.two_d:\n            self.zbegin = 0\n            self.zend = 0\n        else:\n            self.zbegin = -valves["WIDTH"] / 2\n            self.zend = valves["WIDTH"] / 2\n\n    def get_discretization(self):\n        number_nodes = 2 * int(self.discretization / 2) + 1\n        dx_value = [\n            self.yend / number_nodes,\n            self.yend / number_nodes,\n            self.yend / number_nodes,\n        ]\n        self.dx_value = dx_value\n        return dx_value\n\n    def create_geometry(self):\n        """doc"""\n\n        geo = Geometry()\n\n        x_value, y_value, z_value = geo.create_rectangle(\n            coor=[\n                self.xbegin,\n                self.xend,\n                self.ybegin,\n                self.yend,\n                self.zbegin,\n                self.zend,\n            ],\n            dx_value=self.dx_value,\n        )\n\n        return (\n            x_value,\n            y_value,\n            z_value,\n            None\n        )\n\n    def edit_model_data(self, model_data):\n        return model_data\n\n    def crate_block_definition(self, x_value, y_value, z_value, k):\n        """doc"""\n        k = np.where(\n            y_value <= self.yend / 2,\n            2,\n            k,\n        )\n        return k'
  );
});
