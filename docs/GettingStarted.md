---
layout: default
title: Getting Started
nav_order: 2
---

## Building locally

Clone the repository

```
git clone https://github.com/PeriHub/PeriHub/PeriHub.git
```

Go into the perihub folder.

```
cd perihub
```

Create a .env file and save following variables.

```
echo "DEV=True
VOLUME={PATHTOJOBFOLDER}" >> .env
```

Run docker-compose.

```
docker-compose up
```

If docker finished building PeriHub, go to http://localhost:6010

## Contact

- [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)
