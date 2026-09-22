---
layout: default
title: Modelview
parent: Output
nav_order: 2
---

# Model view

The model view renders your simulation in 3-D. You can switch between several
views depending on what you want to look at.

- **Model view** — the starting point for every model. It shows the geometry and
  the blocks (regions) you defined, each block colored differently so you can see
  how the part is split up.

- **VTK view** — the full mesh of points and bonds that the solver actually
  computes with. Points are colored by which block they belong to, and you can
  adjust the size and density of the points to inspect the mesh closely. After a
  run you can use this view to spot a crack — the broken bonds show up as gaps.

- **Plotly view** — a simpler, web-based version of the same data, handy for a
  quick check without loading the heavier 3-D view.

Use your mouse to navigate: **drag to rotate**, **scroll to zoom**, and
**right-drag to pan**.

| Model view | VTK view |
| :--------: | :------: |
| ![drawing](/assets/images/modelView1.PNG) | ![drawing](/assets/images/modelView2.PNG) |
