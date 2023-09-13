<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

# PeriHub - Empowering Research with Peridynamic Modeling

PeriHub is a powerful software solution that can significantly benefit research in various fields. It is an extension of the open-source Peridigm software, providing a numerical implementation of the peridynamic theory. With PeriHub, researchers gain access to a valuable tool for addressing specific challenges and exploring diverse use cases in materials science, engineering, and related disciplines.

## Key Features

- **Peridynamic Modeling:** PeriHub excels at facilitating peridynamic modeling, enabling researchers to analyze material behavior and complex systems. Its unique approach empowers users to explore new frontiers and deepen their understanding of material behavior.

- **User-Friendly Interface:** PeriHub offers a user-friendly interface, making it accessible to both experienced researchers and newcomers in the field. The platform's ease of use ensures efficient simulations, analysis of results, and gaining valuable insights into material behavior.

- **REST API and GUI Support:** Researchers can seamlessly interact with PeriHub using its REST API and GUI support, providing flexibility and convenience in conducting simulations and research tasks.

- **High-Quality and Reliable:** Developed collaboratively by a dedicated group of experts, PeriHub adheres to high standards of quality, reliability, and FAIRness (Findability, Accessibility, Interoperability, and Reusability). The German Aerospace Center (DLR) has played a significant role in fostering an environment that encourages innovation and interdisciplinary collaboration throughout the software's development process.

- **Portability and Scalability:** PeriHub utilizes Docker containers, ensuring seamless integration and deployment across various computing environments. This approach enhances the software's portability, scalability, and ease of use, making it even more practical for research purposes.

![](backend/app/assets/images/PeriHub.drawio.png)

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

## Analyse fracture

![](backend/app/assets/gif/analyseFracture.gif)

# Getting Started with PeriHub Services

To get started with PeriHub, you can use Docker Compose to easily set up the required services. Here's a step-by-step guide:

- Clone the repository

```
git clone https://github.com/dlr-perihub/PeriHub.git
```

- Go into the perihub folder.

```
cd perihub
```

- Create a .env file and save following variables, replace the `{PATHTOJOBFOLDER}` whith an existing directory, for example `/c/Users/YOU/perihubJobs`

```
echo "DEV=True
DLR=False
VOLUME={PATHTOJOBFOLDER}" >> .env
```

- Run docker-compose.

```
docker-compose up
```

- If docker finished building PeriHub, go to http://localhost:6010

## Contact

- [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)

## License

Please see the file [LICENSE.md](LICENSE.md) for further information about how the content is licensed.
