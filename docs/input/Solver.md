---
layout: default
title: Solver
parent: Input
nav_order: 2
---

# Solver

The **Solver** section controls _how_ the simulation does its arithmetic, over
what time, and to what accuracy. These are the settings most likely to affect how
long your run takes and how accurate it is.

For most models the defaults work well. Adjust them only if your simulation is
too slow, unstable, or needs finer time resolution.

| Setting                       | What it controls                                                          |
| ----------------------------- | ------------------------------------------------------------------------- |
| Initial time                  | The start time of the simulation (usually 0).                             |
| Final time                    | The end time. The simulation runs until this point.                       |
| Fixed step time (dt)          | The size of each time step. Smaller steps are more accurate but slower.   |
| Verbose                       | Print extra information to the log.                                       |
| Solver type                   | The numerical method used to solve the equations.                         |
| Safety factor                 | A factor that keeps the time step safe; usually leave at the default.     |
| Numerical damping             | How much energy is intentionally dissipated each second.                  |
| Adaptive time stepping        | Let the solver choose the step size automatically (recommended).          |
| Stable step difference        | How many steps are needed before the calculation is trusted to be stable. |
| Maximum bond difference       | Bonds allowed to break in a single step.                                  |
| Stable bond difference        | The steady number of bonds breaking per step.                             |
| Stop after damage initiation  | Stop the run as soon as the first damage appears.                         |
| Stop before damage initiation | Stop the run just before damage would appear.                             |

> **Tip:** if your run blows up with huge, erratic numbers, that's often a sign
> of instability — the time step may be too large. Try enabling **adaptive time
> stepping**, which adjusts the step automatically.
