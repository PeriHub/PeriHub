---
layout: default
title: Job
parent: Input
nav_order: 2
---

# Job

The **Job** section decides _where_ your simulation runs and _how much
compute_ it is allowed to use.

## Choosing where to run

The built-in models run on a local solver (the `perilab` container when you run
PeriHub yourself, or the shared solver when you use a hosted version). If you have
access to a remote **HPC cluster**, you can select it here to run larger
simulations on more powerful hardware.

| Setting | What it controls                                                        |
| ------- | ----------------------------------------------------------------------- |
| Cluster | The machine that will run the simulation — local, or a remote cluster.  |
| Tasks   | The number of processors (cores) to use. More cores means a faster run. |
| Time    | The maximum time the job may run before it is stopped.                  |
| Account | The account number used to bill the compute time, for cluster jobs.     |

> **Note:** if you are running PeriHub yourself for the first time, leave the
> cluster at its default (the local solver) and make sure the `perilab` container
> is running. See **[Getting Started](/GettingStarted.html)**.
