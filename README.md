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
GITLAB_USER=<YourUsername>" >> .env
```
Go into the netcdf folder.
```
cd ../netcdf
```
Build the netcdf image.
```
docker build . -t netcdf
```
Go into the trilinos folder.
```
cd ../trilinos
```
Build the trilinos image.
```
docker build . -t trilinos
```
Go back to perihub folder.
```
cd ..
```
Run Docker-Compose.
```
docker-compose up
```
## Contact
* [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)