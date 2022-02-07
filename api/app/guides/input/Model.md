# Model

The model configuration panel includes specific settings for the model generation, some settings are only needed for certain models:

- Model Name                
  - Current used Model
- Length 
  - Length of the mesh to be created
- Height 
  - Height of the mesh to be created
- Inner Height
  - Inner Height of the mesh to be created
- Discretization 
  - Number of nodes per height
---
- Two Dimensional | Bool
  - Set the Width/Z-Axis to zero
  - Width 
    - Width of the mesh to be created
- Rotated Angles | Bool 
  - Use user defined angles
  - Angle 0 | `$\circ$`
    - Angle of the upper part of the mesh
  - Angle 1 | `$\circ$`
    - Angle of the lower part of the mesh
- Structured | Bool 
  - Switch from an unstructured to a structured Dogbone mesh

Configuration | Sub-Configuration | Description
--- | --- | ---
Model Name | `$\phantom{++++++++++}$` | Current used Model
Length | | Length of the mesh to be created
Height | | Height of the mesh to be created
Inner Height | | Inner Height of the mesh to be created
Discretization | | Number of nodes per height
Two Dimensional | | Set the Width/Z-Axis to zero
`$\phantom{++++++++++}$` | Width | Width of the mesh to be created
Rotated Angles | | Use user defined angles
`$\phantom{}$` | Angle 0 | Angle of the upper part of the mesh
`$\phantom{}$` | Angle 1 | Angle of the lower part of the mesh
Structured | | Switch from an unstructured to a structured Dogbone mesh