---
layout: default
title: Output
parent: Input
nav_order: 2
---

# Output

The **Output** section decides _what_ your simulation writes down as it runs, and
how often. The more you ask it to save, the more disk space the run uses and the
slower it runs — so save only what you need to analyze.

| Setting          | What it controls                                                 |
| ---------------- | ---------------------------------------------------------------- |
| Name             | A label for the output set you are configuring.                  |
| Variable         | Which quantity to save (displacement, force, damage, and so on). |
| Calculation type | How the quantity should be computed or aggregated.               |
| Block id         | Which block(s) the output applies to.                            |

## Available quantities

| Quantity            | What you get from it                                              |
| ------------------- | ----------------------------------------------------------------- |
| Displacement        | How far each point has moved — the basis for most visualizations. |
| Force               | The forces between points.                                        |
| Damage              | Which bonds have broken — how far the crack has spread.           |
| Partial stress      | The stress carried by individual bonds.                           |
| Number of neighbors | How many neighbors each point still has connected to it.          |

| Setting             | What it controls                                            |
| ------------------- | ----------------------------------------------------------- |
| Output frequency    | How often, in steps, data is written to disk.               |
| Initial output step | The step at which output begins (useful to skip the start). |

> **Tip:** displacement and damage are the quantities you will want most often,
> since they are what the mesh view, plots, and crack analysis use.
