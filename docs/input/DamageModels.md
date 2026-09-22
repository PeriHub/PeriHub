---
layout: default
title: Damage Models
parent: Input
nav_order: 2
---

# Damage Models

In peridynamics, a material breaks when the bonds connecting its points break.
A **damage model** is the rule that decides _when_ a bond breaks. These settings
are applied per block, in the **Blocks** panel.

| Setting                  | What it controls                                                                               |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| Damage name              | A label for this damage definition, so you can tell several apart.                             |
| Damage model name        | The type of damage rule to use.                                                                |
| Critical stretch         | How far a bond can stretch before it breaks. Pull too hard and it snaps.                       |
| Critical energy          | How much energy a bond can absorb before it breaks.                                            |
| Interblock damage energy | Energy needed to break the bonds _between_ two blocks (useful where different materials meet). |
| Only tension             | Allow damage only when the bond is being pulled apart, not squeezed.                           |
| Stabilization type       | The numerical method used to keep the calculation stable.                                      |
| Detached nodes check     | Whether the solver checks for points that have already become detached.                        |
| Thickness                | The thickness used in the damage calculations.                                                 |
| Hourglass coefficient    | A factor that damps a numerical artefact; usually leave at the default.                        |

> **Tip:** most models only need one damage definition, with the default rule.
> Raise the **critical stretch** or **critical energy** to make the material
> tougher, or lower them to make it more brittle.
