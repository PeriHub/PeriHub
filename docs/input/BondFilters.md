---
layout: default
title: Bond Filters
parent: Input
nav_order: 2
---

# Bond Filters

A **bond filter** limits which points the solver considers — for example, you can
restrict bonds to a certain region of space, or to points of a certain type. This
is useful for focusing a calculation on the part of the model where you care
about the results, or for excluding bonds that would otherwise prevent contact
between regions.

Bond filters are an advanced feature. Most models don't need to change the
defaults, but if you build your own model you may want to adjust them.

## Filter settings

| Setting                | What it controls                                                      |
| ---------------------- | --------------------------------------------------------------------- |
| Name                   | A label for the bond filter.                                          |
| Type                   | The kind of filter — for example, a rectangular plane or a cylinder.  |
| Allow contact          | Whether bonds in this filter may still allow contact between regions. |
| Normal                 | The direction the filter plane faces (X, Y, Z components).            |
| Corner / center points | Positioning the filter region in space.                               |
| Vector, length, radius | Size and shape dimensions of the filter region.                       |
| Show                   | Toggle whether the filter is visible in the 3-D view.                 |

> **Tip:** bond filters change which bonds exist in the simulation, so they
> affect the results. Use them deliberately, and check your mesh looks right in
> the view afterwards.
