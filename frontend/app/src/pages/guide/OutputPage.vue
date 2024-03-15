<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <h1>Modelview</h1>
    <p>The Modelview is able to show four different visual outputs:</p>

    <!-- Model view -->
    <h2>Model view</h2>
    <p>The basis of every predefined model, it shows the geometric and the block configuration</p>
    <q-img src="~assets/images/books.jpg" alt="Model view"/>

    <!-- VTK view -->
    <h2>VTK view</h2>
    <p>If a mesh is generated or uploaded the VTK view will show a modifiable representation. The block number of each node is shown by its color. The radius and resolution of every node is adjustable.</p>
    <q-img src="~assets/images/books.jpg" alt="VTK view" />

    <!-- ParaView image -->
    <h2>ParaView image</h2>
    <p>After the first output file is written by a running simulation the user can retrieve images from a ParaView instance.</p>
    <q-img src="~assets/images/books.jpg" alt="ParaView image" />

    <!-- Plotly view -->
    <h2>Plotly view</h2>
    <p>Similar to images the user also has the ability to retrieve a csv file from the ParaView instance. The data will then be visible and manageable in a Plotly environment.</p>
    <q-img src="~assets/images/books.jpg" alt="Plotly view" />
    
    <h1>Textview</h1>
    <p>The Textview will show two different files:</p>

    <!-- Input file -->
    <h2>Input file</h2>
    <p>The input file which will be generated or uploaded. The file contains all necessary configurations needed for a peridynamic simulation. In the Textview, the file can also be modified.</p>
    <q-img src="~assets/images/books.jpg" alt="Input file" />

    <!-- Log file -->
    <h2>Log file</h2>
    <p>For a running simulation, the log file can be retrieved manually or automatically.</p>
    <q-img src="~assets/images/books.jpg" alt="Log file" />
  </div>
</template>

  

<script>

export default {
    name: "OutputPage",
};
</script>

<style>
img {
    width: 100%;
}
</style>