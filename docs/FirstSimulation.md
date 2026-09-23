---
layout: default
title: First Simulation
nav_order: 2
---

# Your first simulation

This page walks through a complete simulation end to end. If you prefer to learn
by reading the individual settings, see **[Input reference](/input.html)** and
**[Output reference](/output.html)** instead.

The example here is the built-in **Compact Tension (CT)** specimen — a small
rectangular plate with a pre-cut notch that is pulled apart at two points. It is
the textbook experiment for studying how cracks grow, and it is a great first
model because you can watch a crack start at the notch tip and travel across the
plate.

## 1. Pick a model

When you open PeriHub the built-in models are shown. Select **Compact Tension**
from the list. Its default settings are already reasonable, so you can move on
without changing anything yet.

If you ever want to start from a blank slate, use the **Reset data** button to
clear the current model.

## 2. Generate the model

In the **Model** section of the Setup panel, press **Generate model**. PeriHub
computes the mesh — the network of tiny points that stand in for your part — and
draws it in the Results panel. A crack or notch is already part of the geometry
for this model.

> **Tip:** the first generation can take a few seconds while the mesh is built.
> A spinner shows that work is in progress.

## 3. Inspect the mesh

Still in the Results panel, switch the view to **Mesh** to look at the part from
different angles. Use your mouse — drag to rotate, scroll to zoom, and
right-drag (or two-finger drag on a touchpad) to pan. This is a good moment to
check that the mesh looks dense enough; see the next step if the mesh looks
coarse.

## 4. Set the mesh size

Open the **Discretization** panel. The setting that matters most here is the
number of points per unit of height — a higher number means a finer, more
accurate mesh, at the cost of a longer run. The built-in model already sets this
to a good value, but if your results look rough or you want more detail, raise
it. If your run is slow, lower it.

## 5. Choose the material

Open the **Material** panel and pick a material. For a first simulation, the
default isotropic material is fine — it is a reasonable choice for many
materials and needs no further input.

Once you pick a material, open the **Blocks** panel. Blocks are the regions the
part is split into; here you attach a material and a damage model to each one.
Built-in models come with their blocks pre-configured.

## 6. Add boundary conditions

A simulation needs to know what is held fixed and what is allowed to move. The
**Boundary conditions** panel handles this. For the CT specimen, the two holes
where the machine grips the plate are held in place, and the plate is pulled in
the vertical direction until the crack grows.

These are already set up for the built-in model, so you can leave them as they
are. If you build your own model, you will need to add these conditions yourself.

## 7. Submit the job

When your model looks right, switch to the **Results** panel and press
**Submit model**. PeriHub prepares everything and hands the work to the solver.

As the simulation runs, the **Text view** at the bottom right shows the live
log — you can watch the progress there. If something goes wrong, use **Cancel
job** to stop it. If it finishes cleanly, the log will show an `Exit Success`
message.

> Submitting a job requires the solver to be running. When you run PeriHub
> yourself, start it with `docker compose up perilab -d` (see **[Getting
> Started](/GettingStarted.html)**).

## 8. View the results

After the job finishes, the **Results** panel shows your saved fields. Switch
between the **Mesh** and **Plot** views to inspect them, and use the mesh view to
zoom in on the crack tip.

## 9. Plot a curve

Fracture experiments are usually summarized by a curve. For the CT specimen, a
force versus displacement curve tells you how the plate responds as the crack
grows.

1. Open the **Plot** dialog from the Results panel.
2. Choose the property to plot (force) on one axis and the independent variable
   (displacement) on the other.
3. Press **Add to results**.

The chart appears in the Results panel.

## 10. Analyze the crack

PeriHub can automatically detect and characterize cracks from the broken bonds in
your simulation. Use the **fracture analysis** tools in the Results panel to
extract the crack path and its length over time.

## 11. Save your work

When you have something you want to come back to, save it:

- **Save as JSON** — export the full model so you can reopen and edit it later.
- **Save config** — export the settings only, to reuse on other models.
- **Download results** — save the computed data as a `.tar.gz` archive.

## What's next

You now know the complete loop. Try changing one thing — a finer mesh, a
different material, or a different boundary condition — and re-run to see how the
crack behavior changes. See **[Input reference](/input.html)** for what every
setting means, and **[Output reference](/output.html)** for how to explore and
save results.
