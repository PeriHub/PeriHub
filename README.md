# PeriHub
PeriHub enables the generation, editing, execution and evaluation of standard peridynamic models
## FA-Services
ToDo
## API
ToDo

## Building locally
Clone the repository
```
git clone https://gitlab.dlr.de/fa_sw/perihub.git
```
Go into the perihub folder.
```
cd perihub
```
Create a .env file an save your git username and token, in order to get the peridigm code.
```
echo "GITLAB_TOKEN=<YourToken>
GITLAB_USER=<YourUsername>
PERIDEV=False
EXTERNAL=False" >> .env
```
Go into the netcdf folder and build the netcdf image.
```
cd ../netcdf
docker build . -t netcdf
```
Go into the trilinos folder and build the trilinos image.
```
cd ../trilinos
docker build . -t trilinos
```
Go back to perihub folder and run Docker-Compose.
```
cd ..
docker-compose up
```
## Contact
* [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)
