---
layout: default
title: Thermal
parent: Input
nav_order: 2
---

# Thermal

The **Thermal** section adds temperature and heat effects to your simulation.
When enabled, the model can carry heat, expand as it heats up, exchange heat with
its surroundings, or even simulate additive manufacturing (3-D printing), where a
layer is laid down hot and cools.

## Turning it on

Toggle **enabled** to turn on thermal behavior for the whole model. When a
thermal model is enabled, also switch on **Thermal Models** in the **Solver**
panel so the solver actually computes the heat.

## Thermal models

| Setting                       | What it controls                                                      |
| ----------------------------- | --------------------------------------------------------------------- |
| Name                          | A label for the thermal model.                                        |
| Thermal type                  | The kind of thermal calculation.                                      |
| Heat transfer coefficient     | How quickly heat moves between the part and its surroundings.         |
| Environmental temperature     | The temperature of the surroundings.                                  |
| Thermal conductivity          | How well the material conducts heat.                                  |
| Thermal expansion coefficient | How much the part grows when heated.                                  |
| Print bed temperature         | Temperature of the surface the part sits on (additive manufacturing). |
| Print bed Z coordinate        | The height of the print bed.                                          |
| File                          | An external file with temperature data to apply.                      |
| Predefined field names        | Names of temperature fields to read from an input file.               |

> **Tip:** thermal simulations are more expensive than mechanical-only ones. Only
> enable them if your problem involves heat.
