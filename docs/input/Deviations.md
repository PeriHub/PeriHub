---
layout: default
title: Deviations
parent: Input
nav_order: 2
---

# Deviations

The **Deviations** section compares your simulation against a **real
experiment**. You enter the measured values from a physical test (for example, a
recorded force–displacement curve or a set of measured material properties), and
PeriHub calculates how far your simulation's numbers deviate from them.

This is mainly a research tool: it lets you check whether your model matches
reality, or tune it to match.

## Turning it on

Toggle **enabled** to activate the comparison. This feature is **disabled in the
trial version** of PeriHub.

## Providing data

There are two ways to give PeriHub your experimental values:

- **Enter them directly** — supply a sample size and the parameter values
  (their name, mean, and standard deviation).
- **Upload a file** — enable **additional txt input** and point it at a text
  file containing your measured data.

After the run, the panel shows the computed deviations between your model and the
measurements.

> **Tip:** to get a meaningful comparison, your simulation's parameters need to
> be set to the same values as the real experiment you are comparing against.
