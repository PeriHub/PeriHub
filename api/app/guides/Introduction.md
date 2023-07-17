<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

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
### Add materials or damage models
![](http://localhost:6020/assets/gif/addMaterialDamage.gif)
### Submit model
![](http://localhost:6020/assets/gif/runModel.gif)
### Analyse results
![](http://localhost:6020/assets/gif/analyseResults.gif)


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
