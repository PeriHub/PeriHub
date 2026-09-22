---
layout: default
title: Contact
parent: Input
nav_order: 2
---

# Contact

Normally, material inside a simulation only interacts with its own bonds.
**Contact** makes regions interact _without_ touching — for example two separate
parts that can press against each other, or one part that can hit itself. When
regions come close, contact forces push them apart so they don't pass through
each other.

This is mostly used for impact, assembly, or multi-body problems. For a single
part under tension or bending, you almost never need it, and it costs extra
compute time, so leave it disabled unless you have a reason to enable it.

## Turning it on

Toggle **enabled** to activate contact for this model.

## Contact models

A **contact model** pairs two regions and defines how they push apart:

| Setting           | What it controls                                                      |
| ----------------- | --------------------------------------------------------------------- |
| Name              | A label for the contact model.                                        |
| Contact type      | The kind of contact calculation.                                      |
| Contact radius    | How far apart two regions must be before contact is considered.       |
| Contact stiffness | How strongly regions are pushed apart when in contact.                |
| Contact groups    | Which pairs of blocks can contact — a master block and a slave block. |

`onlySurfaceContactNodes` restricts the check to the surface points, which is
faster for large models.

## When contact is checked

`searchFrequency` controls how often the solver looks for new contacts. Checking
every step is most accurate but slowest; checking every few steps is faster but
can miss very fast-moving contact.

> **Tip:** contact settings are numerical, not physical. Different stiffness or
> radius values can change your results, so tune them only if you understand why
> you're doing so.
