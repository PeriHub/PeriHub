---
title: Home
layout: home
nav_order: 1
---

# PeriHub - Empowering Research with Peridynamic Modeling

[![Pipeline Status](https://img.shields.io/github/actions/workflow/status/PeriHub/PeriHub/CI.yml?branch=main)](https://github.com/PeriHub/PeriLab.jl/actions)
[![docs](https://img.shields.io/badge/docs-v1-blue.svg)](https://perihub.github.io/PeriHub/)
[![License](https://img.shields.io/badge/License-Apache-blue.svg)](https://github.com/PeriHub/PeriHub/blob/main/LICENSE.md)
[![Docker Image](https://img.shields.io/docker/pulls/perihub/frontend)](https://hub.docker.com/r/perihub/frontend)
[![YouTube](https://img.shields.io/youtube/channel/subscribers/UCeky7HtUGlOJ2OKknvl6YnQ)](https://www.youtube.com/@PeriHub)

PeriHub is a web platform for running **peridynamic simulations**. You build a
model in your browser, describe the material and the forces acting on it, submit
the work to a solver, and get back 3-D visualizations, plots, and fracture
analysis. Nothing has to be installed to use the hosted version — it runs in any
modern browser.

## What is peridynamics?

To understand what PeriHub is for, it helps to know what problem it solves.

Most engineering software predicts how a solid behaves by assuming it is a
continuous material. That works well in most cases, but it breaks down when a
material **cracks, shatters, or splits** — the math cannot easily describe a
crack tip, which is a sudden break in the middle of the material.

**Peridynamics** is an alternative theory that avoids this problem. Instead of
treating material as continuous, it imagines the material as a large number of
small points, each of which can "reach out" and pull on or push away its nearby
neighbors. Every point is connected to the others by springs. This makes it very
good at handling **cracks and damage** — when a crack travels through the part,
the springs simply break at that spot, and the simulation continues naturally.

This makes peridynamics a popular choice for studying:

- **Crack propagation** — how a crack starts and spreads through a material.
- **Impact and fragmentation** — what happens when a material is struck hard.
- **Material characterization** — measuring properties such as toughness from
  the results of controlled experiments.

PeriHub packages all of the mathematics and heavy computing of peridynamics
behind a simple web interface, so you can focus on the physics of your problem
instead of the numerical details.

## What PeriHub does

PeriHub builds on the open-source **PeriLab** solver. In practice it takes care
of the tedious parts of a simulation:

- **Model building** — draw a shape, split it into regions, and pick materials.
- **Meshing** — automatically turn your shape into the tiny points described
  above.
- **Running the simulation** — hand off the work to a fast solver, either on
  your own machine or on a remote compute cluster.
- **Analyzing results** — visualize the deformed mesh, plot how quantities change
  over time, and analyze cracks as they form.

Everything in between — preparing the input the solver needs, running the math,
and pulling the results back — is handled for you.

## How a simulation works

Every simulation in PeriHub goes through the same five stages. You can follow
along in the browser in three panels: the **Setup** panel (left) for building and
configuring, the **Results** panel (top right) for running and visualizing, and the
**Input / Log** panel (bottom right) for the machine-readable file and live
simulation log.

1. **Generate a model.** Pick a built-in shape (a cracked plate, a tensile
   specimen, and so on) or upload your own. PeriHub computes the mesh for you.
2. **Configure the input.** Fill in the settings for each part of the model — the
   material, the fixed or moving regions (blocks), the boundary conditions, and
   the job details.
3. **Submit the job.** Send the model to the solver. You can watch the progress
   in the log and cancel it if needed.
4. **View results.** Inspect the mesh and any saved fields, then download them.
5. **Plot and analyze.** Plot a quantity against time (for example, force vs.
   displacement), and use the built-in tools to study the resulting cracks.

### Generate model

![](/assets/gif/generateModel.gif)

### View generated mesh

![](/assets/gif/viewMesh.gif)

### Edit input deck

![](/assets/gif/editInputDeck.gif)

### Submit model

![](/assets/gif/runModel.gif)

### Analyse results

![](/assets/gif/analyseResults.gif)

### Plot results

![](/assets/gif/plotResults.gif)

### Analyse fracture

![](/assets/gif/analyseFracture.gif)

## Where to go next

- **[Getting Started](/GettingStarted.html)** — install and run PeriHub yourself,
  or find the hosted version.
- **[First Simulation](/FirstSimulation.html)** — walk through a complete
  simulation from start to finish.
- **[Input reference](/input.html)** — what each setting in the Setup panel does.
- **[Output reference](/output.html)** — how to view and download your results.
- **[Models](/models.html)** — the built-in models and how to bring your own.
- **[FAQ](/FAQ.html)** — common questions.
