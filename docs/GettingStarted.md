---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started with PeriHub

There are two ways to use PeriHub: **run it yourself** on your computer with
Docker, or use a **hosted** version if one is available to you. This guide
covers installing and running it yourself.

## Before you start

PeriHub is a set of services that run together. The easiest way to run them is
[Docker Compose](https://docs.docker.com/compose/). Install
[Docker Desktop](https://www.docker.com/products/docker-desktop/) first and make
sure the Docker engine is running (its menu-bar / tray icon should show as
running) before continuing.

## Clone the repository

```
git clone https://github.com/PeriHub/PeriHub.git
```

```
cd PeriHub
```

## Configure

PeriHub reads a `.env` file for its settings. One is included in the repository —
copy it and leave the defaults as they are for a first run:

```
cp .env.example .env
```

The most useful setting to know about is `MAX_NODES`, which limits the size of a
simulation to protect your computer. If you have a powerful machine you can raise
it; for a first test, leave it as is.

## Run

```
docker compose up
```

This builds and starts all the services. It can take a few minutes the first time
because it downloads the required images. Once it reports that the services are
running, open

[http://localhost:8080](http://localhost:8080)

in your browser.

If you want to actually **submit simulations** to run (not just build and view
models), you also need the solver container started:

```
docker compose up perilab -d
```

You will usually be greeted by a short interactive tour the first time you open
the app. Walk through it — it points out the three main areas of the interface.
You can open it again any time from the **Help** button in the header.

## Stop

When you are done, stop the services to free up memory and CPU:

```
docker compose down
```

## Updating

PeriHub is updated frequently. To pull the latest version, re-run the steps:

```
git pull
docker compose up --build
```

## Using a hosted version

Some organizations run their own hosted copy of PeriHub so that many users share
one installation and its compute resources. If you are given a hosted URL, simply
open it in a browser — no installation is required. Log in with the account your
organization gave you, and skip straight to **[First Simulation](/FirstSimulation.html)**.

## Contact

- [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)
