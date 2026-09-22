---
layout: default
title: Additive
parent: Input
nav_order: 2
---

# Additive

The **Additive** section simulates **additive manufacturing** — 3-D printing. It
models the process of building a part one thin layer at a time from hot material,
so you can study the stresses and distortions that come from melting and cooling.

This is an advanced use case. For ordinary simulations leave it disabled.

## Turning it on

Toggle **enabled** to activate additive-manufacturing analysis. When on, switch on
**Additive Models** in the **Solver** panel so the solver accounts for the extra
physics.

## Additive models

| Setting       | What it controls                                    |
| ------------- | --------------------------------------------------- |
| Name          | A label for the additive model.                     |
| Additive type | The kind of additive-manufacturing calculation.     |
| Print temp    | The temperature of the material as it is deposited. |

> **Tip:** additive manufacturing simulations are among the most expensive runs
> PeriHub can do. They need a fine mesh and many small time steps.
