---
layout: default
title: Modelview
parent: Output
nav_order: 2
---

# Modelview

The Modelview is able to show four different visual outputs:

- Model view:
  - The basis of every predefined model, it shows the geometric and the block configuration
- VTK view:
  - If a mesh is generated or uploaded the VTK view will show a modifiable representation. The block number of each node is shown by its color. The radius and resolution of every node is adjustable.
- ParaView image:
  - After the first output file is written by a running simulation the user can retrieve images from a ParaView instance.
- Plotly view:
  - Similar to images the user also hast the ability to retrieve a csv file from the ParaView instance. The data will then by visible and manageable in a Plotly environment.

|                Model view                 |                 VTK view                  |
| :---------------------------------------: | :---------------------------------------: |
| ![drawing](/assets/images/modelView1.PNG) | ![drawing](/assets/images/modelView2.PNG) |
|            **ParaView image**             |              **Plotly view**              |
| ![drawing](/assets/images/modelView3.PNG) | ![drawing](/assets/images/modelView4.PNG) |
