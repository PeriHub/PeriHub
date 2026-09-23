---
layout: default
title: Material
parent: Input
nav_order: 2
---

# Material

The **Material** section describes the substance your part is made of. Every
material has a set of properties — how heavy it is, how stiff, and so on. The
built-in models ship with a sensible material already chosen.

## Choosing a material

Pick a material from the list, then a **material model** — the mathematical
description of how it behaves. The default isotropic model is a good starting
point for most materials and needs no further settings.

## Property values

| Property           | Why it matters                                                            |
| ------------------ | ------------------------------------------------------------------------- |
| Density            | How much mass is packed into a unit of volume.                            |
| Young's Modulus    | How stiff the material is — high values mean it barely stretches.         |
| Poisson's Ratio    | How much a material thins sideways when you stretch it lengthwise.        |
| Bulk Modulus       | How resistant it is to being squeezed uniformly.                          |
| Shear Modulus      | How resistant it is to being sliced or skewed.                            |
| Tension Separation | The maximum stretch a bond can take before breaking (fracture toughness). |

You usually only need to enter the values you know. PeriHub can compute any value
you leave blank from the others.

## Advanced options

| Setting               | What it controls                                                                |
| --------------------- | ------------------------------------------------------------------------------- |
| Non linear            | Use a nonlinear calculation. More realistic for large deformations, but slower. |
| Stabilization type    | The numerical method used to keep the calculation stable.                       |
| Thickness             | The material thickness used in the calculations.                                |
| Hourglass coefficient | A damping factor; usually leave at the default.                                 |

> **Tip:** for a first simulation, keep the default material and its properties.
> Focus on getting the model to run before tuning the material.
