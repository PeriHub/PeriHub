<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <div>
      <h1>PeriHub</h1>
      <p>
        PeriHub enables the generation, editing, execution and evaluation of standard peridynamic models
      </p>
      <ul>
        <li><a href="https://perihub.fa-services.intra.dlr.de/">FA-Services</a></li>
        <li><a href="https://perihub-api.fa-services.intra.dlr.de/docs">API</a></li>
      </ul>
  
      <h3>Generate model</h3>
      <q-img src="~assets/gif/generateModel.gif" />
  
      <h3>View generated mesh</h3>
      <q-img src="~assets/gif/viewMesh.gif" />
  
      <h3>Edit input deck</h3>
      <q-img src="~assets/gif/editInputDeck.gif" />
  
      <h3>Submit model</h3>
      <q-img src="~assets/gif/runModel.gif" />
  
      <h3>Analyse results</h3>
      <q-img src="~assets/gif/analyseResults.gif" />
  
      <h3>Plot results</h3>
      <q-img src="~assets/gif/plotResults.gif" />
  
      <h3>Analyse fracture</h3>
      <q-img src="~assets/gif/analyseFracture.gif" />
  
      <h2>Building locally</h2>
      <p>
        Clone the repository:
        <code>git clone https://gitlab.com/dlr-perihub/PeriHub/PeriHub.git</code>
      </p>
      <p>
        Go into the perihub folder:
        <code>cd perihub</code>
      </p>
      <p>
        Run docker-compose:
        <code>docker-compose up</code>
      </p>
      <p>
        If docker finished building PeriHub, go to <a href="http://localhost:8000">http://localhost:8000</a>
      </p>
  
      <h2>Contact</h2>
      <ul>
        <li><a href="mailto:Jan-Timo.Hesse@dlr.de">Jan-Timo Hesse</a></li>
      </ul>
    </div>
  </template>
  

<script>

export default {
    name: "IntroductionPage",
};
</script>

<style>
img {
    width: 100%;
}
</style>