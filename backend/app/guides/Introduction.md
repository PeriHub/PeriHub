<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

# PeriHub

PeriHub enables the generation, editing, execution and evaluation of standard peridynamic models

- FA-Services: https://perihub.fa-services.intra.dlr.de/
- API: https://perihub-api.fa-services.intra.dlr.de/docs

### Generate model

![](http://localhost:6020/assets/gif/generateModel.gif)

### View generated mesh

![](http://localhost:6020/assets/gif/viewMesh.gif)

### Edit input deck

![](http://localhost:6020/assets/gif/editInputDeck.gif)

### Submit model

![](http://localhost:6020/assets/gif/runModel.gif)

### Analyse results

![](http://localhost:6020/assets/gif/analyseResults.gif)

### Plot results

![](http://localhost:6020/assets/gif/plotResults.gif)

### Analyse fracture

![](http://localhost:6020/assets/gif/analyseFracture.gif)

## Building locally

Clone the repository

```
git clone https://gitlab.com/dlr-perihub/PeriHub/PeriHub.git
```

Go into the perihub folder.

```
cd perihub
```

Create a .env file and save following variables.

```
echo "DEV=True
DLR=False
VOLUME={PATHTOJOBFOLDER}" >> .env
```

Run docker-compose.

```
docker-compose up
```

If docker finished building PeriHub, go to http://localhost:6010

## Contact

- [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)
