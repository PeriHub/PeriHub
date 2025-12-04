<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

# PeriHub - Empowering Research with Peridynamic Modeling

[![Pipeline Status](https://img.shields.io/github/actions/workflow/status/PeriHub/PeriHub/CI.yml?branch=main)](https://github.com/PeriHub/PeriLab.jl/actions)
[![docs](https://img.shields.io/badge/docs-v1-blue.svg)](https://perihub.github.io/PeriHub/)
[![License](https://img.shields.io/badge/License-Apache-blue.svg)](https://github.com/PeriHub/PeriHub/blob/main/LICENSE.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8159334.svg)](https://doi.org/10.5281/zenodo.8159334)
[![Docker Image](https://img.shields.io/docker/pulls/perihub/frontend)](https://hub.docker.com/r/perihub/frontend)
[![YouTube](https://img.shields.io/youtube/channel/subscribers/UCeky7HtUGlOJ2OKknvl6YnQ)](https://www.youtube.com/@PeriHub)

PeriHub is a powerful software solution that can significantly benefit research in various fields. It is an extension of the open-source PeriLab software, providing a numerical implementation of the peridynamic theory. With PeriHub, researchers gain access to a valuable tool for addressing specific challenges and exploring diverse use cases in materials science, engineering, and related disciplines.

## Key Features

- **Peridynamic Modeling:** PeriHub excels at facilitating peridynamic modeling, enabling researchers to analyze material behavior and complex systems. Its unique approach empowers users to explore new frontiers and deepen their understanding of material behavior.

- **User-Friendly Interface:** PeriHub offers a user-friendly interface, making it accessible to both experienced researchers and newcomers in the field. The platform's ease of use ensures efficient simulations, analysis of results, and gaining valuable insights into material behavior.

- **REST API and GUI Support:** Researchers can seamlessly interact with PeriHub using its REST API and GUI support, providing flexibility and convenience in conducting simulations and research tasks.

- **High-Quality and Reliable:** Developed collaboratively by a dedicated group of experts, PeriHub adheres to high standards of quality, reliability, and FAIRness (Findability, Accessibility, Interoperability, and Reusability). The German Aerospace Center (DLR) has played a significant role in fostering an environment that encourages innovation and interdisciplinary collaboration throughout the software's development process.

- **Portability and Scalability:** PeriHub utilizes Docker containers, ensuring seamless integration and deployment across various computing environments. This approach enhances the software's portability, scalability, and ease of use, making it even more practical for research purposes.

### Overview

![](docs/assets/images/PeriHub.svg)

### Generate model

![](docs/assets/gif/generateModel.gif)

### View generated mesh

![](docs/assets/gif/viewMesh.gif)

### Edit input deck

![](docs/assets/gif/editInputDeck.gif)

### Submit model

![](docs/assets/gif/runModel.gif)

### Analyse results

![](docs/assets/gif/analyseResults.gif)

### Plot results

![](docs/assets/gif/plotResults.gif)

### Analyse fracture

![](docs/assets/gif/analyseFracture.gif)

# Getting Started with PeriHub Services

To get started with PeriHub, you can use Docker Compose to easily set up the required services. Here's a step-by-step guide:

- Clone the repository

```
git clone https://github.com/PeriHub/PeriHub.git
```

- Go into the PeriHub folder.

```
cd PeriHub
```

- Copy the .env file and edit its contents (Optional).

```
cp .env.example .env
```

- Run docker-compose.

```
docker-compose up
```

- If docker finished starting PeriHub, go to http://localhost:8080

# Contributing

If you like to start PeriHub in a development mode, you will need to install following requirements

## Requirements

- Install the [node version manager](https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script) and node itself

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install --lts
```

- Now you can get the [quasar cli](https://quasar.dev/start/quick-start) and install the node packages

```
cd frontend/app
npm i -g @quasar/cli
npm install
```

- For the python backend we need to make sure that [pip](https://pip.pypa.io/en/stable/installation/), [fastapi](https://fastapi.tiangolo.com/) and further dependencies are installed

```
cd backend
pip install "fastapi[standard]"
pip install -r requirements.txt
pip install git+https://github.com/JTHesse/crackpy.git
```

Now you are able to start the services

## Starting the services

```
cd frontend/app
quasar dev
```

```
cd backend/app
fastapi dev main.py
```

> If you also want to submit any simulations, make sure to start the perilab container:

```
docker compose up perilab -d
```

## Contact

- [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)

## License

Please see the file [LICENSE.md](LICENSE.md) for further information about how the content is licensed.
