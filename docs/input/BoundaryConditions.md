---
layout: default
title: Boundary Conditions
parent: Input
nav_order: 2
---

# Boundary Conditions

A simulation won't run — or will give meaningless results — unless it knows what
is held fixed and what is allowed to move. **Boundary conditions** are how you
express that.

For example, in a tension test the two ends of a specimen are gripped: one end is
held still, the other is pulled. Those grips are boundary conditions. Without
them the whole part would just float away.

A condition is set for one **block** and points in one direction:

| Setting    | What it controls                                                            |
| ---------- | --------------------------------------------------------------------------- |
| Name       | A label for the condition.                                                  |
| Type       | What kind of condition this is (fixed, prescribed displacement, and so on). |
| Block id   | The block the condition applies to.                                         |
| Coordinate | The direction the condition acts in (X, Y, or Z).                           |
| Value      | The value the condition applies, for example how far the block moves.       |

The built-in models come with the right boundary conditions already set up. You
usually only need to adjust them when building a model of your own.
