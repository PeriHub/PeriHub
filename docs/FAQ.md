---
layout: default
title: FAQ
nav_order: 2
---

# PeriHub FAQ

Answers to the most common questions, written for new users.

### What is PeriHub?

PeriHub is a web application for running peridynamic simulations. You build and
configure a model in your browser, submit it to a solver, and get back 3-D
visualizations, plots, and fracture analysis. You don't need to install anything
to use a hosted version.

### What is peridynamics?

Peridynamics is a way of modeling how solid materials behave. Unlike traditional
methods that treat a material as a continuous object, peridynamics treats it as a
large number of points that pull and push on each other, connected by springs.
Because a "spring" can simply break, peridynamics is especially good at predicting
**cracks, damage, and fragmentation** — things that are hard for other methods to
handle.

### What is PeriLab?

PeriLab is the open-source solver that actually does the heavy computing.
PeriHub is the web interface in front of it, taking your model, running it on
PeriLab, and presenting the results back to you.

### Who is PeriHub for?

Anyone studying how materials break or deform — researchers and engineers in
materials science, mechanical engineering, and computational physics. Common
uses include studying how cracks grow, testing how materials respond to impact,
and measuring material properties.

### What does a typical simulation look like?

The loop is: generate a model → configure material, blocks, and boundary
conditions → submit the job → view and plot the results → download them. See
**[First Simulation](/FirstSimulation.html)** for a complete walkthrough.

### Is PeriHub free and open source?

Yes. It is open source under the Apache 2.0 license, which allows both
non-commercial and commercial use. See the [LICENSE](https://github.com/PeriHub/PeriHub/blob/main/LICENSE.md)
for details.

### How do I install and run it myself?

Use Docker Compose. See **[Getting Started](/GettingStarted.html)** for the
full step-by-step, including how to start the solver so you can submit jobs.

### How large a simulation can I run?

Performance depends on your hardware and on how large or fine-grained your model
is. The built-in models are good starting points; the built-in tour explains how
the three panels (Setup, Results, Input/Log) fit together and how to get the most
out of them. See **[Getting Started](/GettingStarted.html)** for how to launch it.

### Can I use my own models?

Yes. You can write your own model and drop it into a folder to have it appear in
the model list. See the model documentation for how to create one.

### Where can I get help or report a bug?

Open a [GitHub Discussion](https://github.com/PeriHub/PeriHub/discussions/new/choose)
for questions, or the [issue tracker](https://github.com/PeriHub/PeriHub/issues)
for bugs. The community and maintainers are happy to help.
