# PeriHub

[![pipeline status](https://gitlab.dlr.de/fa_sw/peridynamik/PeriHub/badges/main/pipeline.svg)](https://gitlab.dlr.de/fa_sw/peridynamik/PeriHub/-/commits/main)
[![coverage report](https://gitlab.dlr.de/fa_sw/peridynamik/PeriHub/badges/main/coverage.svg)](https://gitlab.dlr.de/fa_sw/peridynamik/PeriHub/-/commits/main)
[![License](https://img.shields.io/badge/License-BSD-blue.svg)](https://gitlab.dlr.de/fa_sw/peridynamik/PeriHub/-/blob/main/LICENSE)


PeriHub enables the generation, editing, execution and evaluation of standard peridynamic models

- FA-Services: https://perihub.fa-services.intra.dlr.de/
- API: https://perihub-api.fa-services.intra.dlr.de/docs

![](gui/app/public/images/PeriHub.drawio.png)

### Generate model
![](gui/app/public/gif/generateModel.gif)
### View generated mesh
![](gui/app/public/gif/viewMesh.gif)
### Edit input deck
![](gui/app/public/gif/editInputDeck.gif)
### Add materials or damage models
![](gui/app/public/gif/addMaterialDamage.gif)
### Submit model
![](gui/app/public/gif/runModel.gif)
### Analyse results
![](gui/app/public/gif/analyseResults.gif)


## Building locally
Clone the repository
```
git clone https://github.com/PeriHub/PeriHub.git
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
* [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)
