---
layout: default
title: Output
nav_order: 2
has_children: true
---

# The output reference

The **Results** panel is where you look at and save what your simulation found.
It shows two things at once:

- A set of buttons (**View Actions**) to submit the job, view, download, or
  delete results, and to make a plot.
- A **Results view** that renders your data.

See also **[First Simulation](/FirstSimulation.html)** for the same steps written
out as a walkthrough.

## Viewing results

| View      | What you see                                                               |
| --------- | -------------------------------------------------------------------------- |
| Mesh view | The 3-D mesh of your model. Nodes are colored by the block they belong to. |
| Plot view | A chart of a quantity (force, displacement, damage …) against time.        |
| Text view | The human-readable results and log files as text.                          |

## Downloading results

Use **Download Results** to save a snapshot of your current state. You can save
only the essential result, or **all data**, and the download comes as a `.tar.gz`
archive.

## Deleting results

In the **Jobs** view, the trash icon on a job deletes that job's log and result
files. **Delete all** next to a model's name deletes all of its jobs together
with the model's input files on the server; other models are not touched.
Active jobs have to be cancelled first.

## Plotting results

Use **Plot Results** to add a chart to your results. Choose the quantity to plot,
the type of plot, the property, and the data range, then press **Add to
results**.
