---
layout: default
title: Input
nav_order: 2
has_children: true
---

# The input reference

The **Setup** panel is where you describe your simulation. It is organized as a
set of expandable sections, or _panels_. Each panel asks for the settings that
belong to one part of the model. You do not have to fill every panel in for every
simulation — only the ones relevant to the model you are working on.

The panels are grouped into three themes. Start with the first group, work
forward, and only expand the later ones if your model needs them.

## Geometry

These panels build the shape of your part.

- **[Model](/input/Model.html)** — choose a built-in shape or upload your own; set the size.
- **[Discretization](/input/Discretization.html)** — decide how the part is divided into tiny points (the mesh).
- **[Blocks](/input/Blocks.html)** — split the part into regions and assign a material + damage model.

## Physics

These panels describe how the part behaves.

- **[Material](/input/Material.html)** — choose the material and the property values it needs.
- **[Thermal](/input/Thermal.html)** — heat and temperature effects (optional).
- **[Additive](/input/Additive.html)** — additive manufacturing / 3-D printing simulation (optional).
- **[Damage Models](/input/DamageModels.html)** — when and how bonds break (i.e. when the material cracks).
- **[Contact](/input/Contact.html)** — prevent regions from passing through each other (optional).

## Simulation

These panels control how the run is executed and what is recorded.

- **[Boundary Conditions](/input/BoundaryConditions.html)** — fix regions in place, or move/pull them.
- **[Bond Filters](/input/BondFilters.html)** — keep certain bonds in or out (optional).
- **[Output](/input/Output.html)** — which quantities to save and how often.
- **[Solver](/input/Solver.html)** — time steps, accuracy, and how the math is solved.
- **[Deviations](/input/Deviations.html)** — compare against a real experiment (not available in the trial).
- **[Job](/input/Job.html)** — where to run the simulation and how many processors to use (shown only with a cluster).

Tip: open the panel to read the description of each field, then set the value.
You can always expand or collapse every panel at once with the button at the top
of the panel.
