<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

# Solver

The solver configuration panel defines are necessary solver settings:

Configuration | Sub-Configuration | Description
--- |--- | ---
Inital Time | `$\phantom{++++++}$` | Initial simulation time
Final Time | |  Final simulation time
Fixed dt | |  User defined step time
Verbose | |  Enable verbose
Solvertype | |  Defines the used solver
Safety Factor | |  Safety factor for dt calculation
Numerical Damping | |  Defines the percentage of energy that will be dissipated in one second
Adaptive Time Stepping | |  Enables the adaptive time stepping method
`$\phantom{++++++}$` | Stable Step Difference |  Number of steps that are needed to stabilize the calculation
`$\phantom{++++++}$` | Maximum Bond Difference |  Number of bonds that are allowed to break in one step
`$\phantom{++++++}$` | Stable Bond Difference |  Stable number of bonds that are allowed to break in one step
Stop after damage initiation | | Enable to stop the simulation after first damage occurs
Stop before damage initiation | |  Enable to stop the simulation before first damage occurs
