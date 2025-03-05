---
layout: default
title: Own Models
parent: Models
nav_order: 2
---

## PeriHub Model Documentation

### Introduction

This document provides a guide on how to write a Python file that defines your own model in PeriHub.

### Model Definition and Imports

The following is a basic structure for defining a model in Python:

```python
"""
title: NAME OF YOUR MODEL
description: DESCRIPTION OF YOUR MODEL
author: YOUR USERNAME
requirements: PIP REQUIREMENTS
version: 0.1.0
"""
import numpy as np
from pydantic import BaseModel, Field

from ...support.model.geometry import Geometry
```

### Valves Class

The following is a basic structure for defining a class that represents valves in the model.
You can define as much valves as you need. Theses will be represented in the frontend under the Model section.

```python
class Valves(BaseModel):
    FLOAT: float = Field(
        default=10.5,
        title="FLOAT",
        description="FLOAT",
    )
    BOOLEAN: bool = Field(
        default=True,
        title="BOOLEAN",
        description="BOOLEAN",
    )
```

### Main Class

The following is a basic structure for defining a class that represents the main model.
The first function is the constructor of the class, here you can define the variables that will be used in the model.
Availabe variables are the valves as well as the two_dimensional parameter.

```python
class main:
    def __init__(self, valves, two_dimensional):
        self.FLOAT = valves["FLOAT"]
```

The second function is the `get_discretization` function, here you can define the discretization of the model.
The discretization is a list of three floats that represent the discretization in the x, y and z directions.

```python
def get_discretization(self):
    disc = [self.FLOAT, self.FLOAT, self.FLOAT]
    self.disc = disc
    return disc
```

The third function is the `create_geometry` function, here you can define the geometry of the model.
For basic shapes you can use the Geometry class.
The function returns the x, y and z values of the geometry.

```python
def create_geometry(self):
    geo = Geometry()

    x_values, y_values, z_values = geo.create_rectangle(
        coor=[
            self.FLOAT,
            self.FLOAT,
            self.FLOAT,
            self.FLOAT,
            self.FLOAT,
            self.FLOAT,
        ],
        dx_value=self.disc,
    )
    return x_values, y_values, z_values
```

The last function is the `crate_block_definition` function, here you can define the blocks of the model.
The function returns an array of block ids.
Input values are the x, y and z values of the geometry, as well as the default block id array with all values set to 1.

```python
def crate_block_definition(self, x_values, y_values, z_values, k):
    """doc"""
    k = np.where(
        x_values >= self.FLOAT,
        2,
        k,
    )
    return k
```

Optionally, you can the `edit_model_data` function, here you can change any values of the model retrieved from PeriHub.

```python
def edit_model_data(self, model_data):
    model_data.bondFilters[0].lowerLeftCornerX = self.FLOAT
    return model_data
```

### Full Example

```python
"""
title: Kalthoff-Winkler
description: Crack propagation
author: Jan-Timo Hesse
requirements:
version: 0.1.0
"""
import numpy as np
from pydantic import BaseModel, Field

from ...support.model.geometry import Geometry


class Valves(BaseModel):
    DISCRETIZATION: float = Field(
        default=100,
        title="Discretization",
        description="Discretization",
    )
    LENGTH: float = Field(
        default=100,
        title="Length",
        description="Length",
    )
    HEIGHT: float = Field(
        default=200,
        title="Height",
        description="Height",
    )
    WIDTH: float = Field(
        default=10,
        title="Width",
        description="Width",
    )

class main:
    def __init__(self, valves, twoDimensional):
        self.xbegin = 0
        self.xend = valves["LENGTH"]
        self.ybegin = -valves["HEIGHT"] / 2
        self.yend = valves["HEIGHT"] / 2
        self.discretization = valves["DISCRETIZATION"]

        if twoDimensional:
            self.zbegin = 0
            self.zend = 0
        else:
            self.zbegin = -valves["WIDTH"] / 2
            self.zend = valves["WIDTH"] / 2

    def get_discretization(self):
        number_nodes = 2 * int(self.discretization / 2) + 1
        disc = [
            self.yend / number_nodes,
            self.yend / number_nodes,
            self.yend / number_nodes,
        ]
        self.disc = disc
        return disc

    def create_geometry(self):
        """doc"""

        geo = Geometry()

        x_values, y_values, z_values = geo.create_rectangle(
            coor=[
                self.xbegin,
                self.xend,
                self.ybegin,
                self.yend,
                self.zbegin,
                self.zend,
            ],
            dx_value=self.disc,
        )

        return (
            x_values,
            y_value,
            z_values,
        )

    def crate_block_definition(self, x_values, y_values, z_values, k):
        """doc"""
        k = np.where(
            np.logical_and(
                x_values < self.disc[0] * 5,
                np.logical_and(y_values <= 25, y_values >= -25),
            ),
            2,
            k,
        )
        k = np.where(
            np.logical_and(
                x_values < self.disc[0],
                np.logical_and(y_values <= 25, y_values >= -25),
            ),
            3,
            k,
        )
        return k
```
