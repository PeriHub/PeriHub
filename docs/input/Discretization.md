---
layout: default
title: Discretization
parent: Input
nav_order: 2
---

# Discretization

**Discretization** is how your part is turned into the network of tiny points
(the _mesh_) that the solver actually computes with. Peridynamics works on
discrete points, so this is the step that turns your smooth geometry into
something a computer can simulate.

## How the points are generated

The most common option is a **random distribution** — points are spread through
your part. The **node type** controls how the mesh is created.

## Mesh density

The mesh density (sometimes called _discretization_ or _resolution_) controls how
many points are placed in a unit of length. This is usually the single most
important setting for accuracy and speed:

- **More points** — a finer mesh. More accurate results, especially around a
  crack tip, but a longer run and more disk usage.
- **Fewer points** — a coarser mesh. Faster and cheaper, but you may miss detail.

A good workflow is to start with a coarse mesh and get a simulation running, then
refine it to check that the results don't change. If results change a lot when you
refine the mesh, the mesh was too coarse.

## Node sets

For boundary conditions and output, you often need to select a specific group of
points — for example, the points along a grip, or the points at a cut. A **node
set** is a named group of points you can create from a file and then refer to by
name from other panels. See the **Boundary conditions** and **Output** panels.

## Generating from a G-code file

Advanced users can build a mesh from a G-code file (for example, one produced by
a 3-D printer or CNC machine) instead of a simple box. When **overwrite mesh** is
enabled, PeriHub generates the point distribution from the file's sampling
parameters and dimensions instead of the default geometry.

> **Tip:** don't set an extremely fine mesh for a first run. It will take much
> longer to solve and use more disk. Refine only when you need to.
