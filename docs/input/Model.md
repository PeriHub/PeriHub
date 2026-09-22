---
layout: default
title: Model
parent: Input
nav_order: 2
---

# Model

The **Model** section is where you choose the shape of your part and set its size.
You can pick one of the built-in models or upload your own.

## Choosing or loading a model

Open the actions bar at the top of the Setup panel to select the model. You can
load a saved model, download the current one, or browse the built-in models. See
**[Models](/models.html)** for the full list.

## Size

Set the dimensions of the part you are creating:

| Field        | What it controls                                      |
| ------------ | ----------------------------------------------------- |
| Length       | Length of the part, along the X axis.                 |
| Height       | Height of the part, along the Y axis.                 |
| Inner Height | Height of any inner region for multi-part geometries. |
| Width        | Width (the Z axis). Only needed for 3-D models.       |

If your part is very thin, or you only care about two dimensions, switch on
**Two Dimensional**. This makes the part flat by setting its width to zero, which
makes the simulation faster.

## Mesh angles (advanced)

For models built from angled pieces, you can set the angle of the upper and lower
parts. Most users can leave these at their defaults. Some models offer a choice
of a **structured** or **unstructured** mesh; the built-in models set the right
one for you.

> **Tip:** don't set the size and the mesh size (Discretization) at the same
> time. Set the size here first, generate the model, and then decide how fine to
> make the mesh in the Discretization panel.
