# PeriHub
PeriHub enables the generation, editing, execution and evaluation of standard peridynamic models

- FA-Services: https://perihub.fa-services.intra.dlr.de/
- API: https://perihub-api.fa-services.intra.dlr.de/docs

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
git clone https://github.com/JTHesse/PeriHub.git
```
Go into the perihub folder.
```
cd perihub
```
Create a .env file and save following variables.
```
echo "DEV=True
EXTERNAL=True" >> .env
```
Run docker-compose.
```
docker-compose up
```
If docker finished building PeriHub, go to http://localhost:6010
## Contact
* [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)
