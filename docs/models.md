---
layout: default
title: Models
nav_order: 2
has_children: true
---

# Models

A **model** is a ready-made geometry you can build your simulation on instead of
starting from scratch. Each model comes with sensible default settings, so it is
the fastest way to run a first simulation or to compare against published
results.

When you first open PeriHub the built-in models are shown automatically. You can
pick one and start editing it, or **upload your own** model — a saved configuration
you exported earlier as a JSON file. See **[First Simulation](/FirstSimulation.html)**
for the full walkthrough.

## Built-in models

PeriHub ships with a set of standard test specimens used throughout fracture
mechanics research. Each one is a small, well-understood experiment that is handy
for learning the software or for checking your setup. They show up in the model
list when you open PeriHub.

| Model                  | What it is                                                         |
| ---------------------- | ------------------------------------------------------------------ |
| Compact Tension        | A plate with a notch, pulled at two points. A classic crack study. |
| Double Cantilever Beam | Two beams popened apart, used to study crack growth.               |
| Dogbone                | A tensile specimen (wide narrow "dogbone" shape) pulled apart.     |
| End Notched Flexure    | A beam with a pre-cut notch, bent until it breaks.                 |
| Kalthoff–Winkler       | A plate struck by a projectile, used to study fast fracture.       |
| Plate with a Hole      | A plate with a hole, used to study stress around openings.         |

The default settings for each are good starting points, so try one and adjust
from there.

## Your own models

You are not limited to the built-in models. If you write a model in Python, you
can drop it into a folder and PeriHub will load it into the model list. See
**[Own Models](/models/OwnModels.html)** for how to write and add one.
