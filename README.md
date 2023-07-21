<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

# PeriHub

PeriHub enables the generation, editing, execution and evaluation of standard peridynamic models.

![](backend/app/assets/images/PeriHub.drawio.png)

### Generate model
![](backend/app/assets/gif/generateModel.gif)
### View generated mesh
![](backend/app/assets/gif/viewMesh.gif)
### Edit input deck
![](backend/app/assets/gif/editInputDeck.gif)
### Add materials or damage models
![](backend/app/assets/gif/addMaterialDamage.gif)
### Submit model
![](backend/app/assets/gif/runModel.gif)
### Analyse results
![](backend/app/assets/gif/analyseResults.gif)


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

## License

Please see the file [LICENSE.md](LICENSE.md) for further information about how the content is licensed.
