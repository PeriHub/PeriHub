<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <div>
    <h1>Buttons</h1>

    <!-- Upload Button -->
    <q-btn @click="upload">
      <q-icon name="fas fa-upload" /> Upload
    </q-btn>
    <p>Model, mesh, or user material library files can be uploaded.</p>

    <!-- Save Button -->
    <q-btn @click="save">
      <q-icon name="fas fa-save" /> Save
    </q-btn>
    <p>Current model configurations can be saved as a JSON file.</p>

    <!-- Reset Data Button -->
    <q-btn @click="resetData">
      <q-icon name="fas fa-undo" /> Reset data
    </q-btn>
    <p>If a predefined model is used, current configurations can be restored.</p>

    <!-- Generate Button -->
    <q-btn @click="generate">
      <q-icon name="fas fa-cogs" /> Generate
    </q-btn>
    <p>The input and/or mesh file is generated.</p>

    <!-- Download Button -->
    <q-btn @click="download">
      <q-icon name="fas fa-download" /> Download
    </q-btn>
    <p>Model and result files are downloadable for further analysis.</p>

    <!-- Collapse/Expand Button -->
    <q-btn @click="collapseExpand">
      <q-icon name="fas fa-sort" /> Collapse/Expand
    </q-btn>
    <p>All configuration options can be collapsed or expanded.</p>

    <!-- Run Button -->
    <q-btn @click="run">
      <q-icon name="fas fa-play" /> Run
    </q-btn>
    <p>If a valid model is available, the user will be able to submit the analysis.</p>

    <!-- Cancel Button -->
    <q-btn @click="cancel">
      <q-icon name="fas fa-times" /> Cancel
    </q-btn>
    <p>Running simulations can be cancelled.</p>

    <!-- Cancel Button -->
    <q-btn @click="cancel">
      <q-icon name="fas fa-download" /> Cancel
    </q-btn>
    <p>Running simulations can be cancelled.</p>

    <!-- Cancel Button -->
    <q-btn @click="cancel">
      <q-icon name="fas fa-eye" /> Cancel
    </q-btn>
    <p>Running simulations can be cancelled.</p>

    <!-- Plot Button -->
    <q-btn @click="plot">
      <q-icon name="fas fa-chart-line" /> Plot
    </q-btn>
    <p>Plots and returns global data.</p>

    <!-- Image Button -->
    <q-btn @click="showImage">
      <q-icon name="fas fa-image" /> Image
    </q-btn>
    <p>Shows the image of the user-defined variable from the last step.</p>

    <!-- Mesh Button -->
    <q-btn @click="showMesh">
      <q-icon name="view_quilt" /> Mesh
    </q-btn>
    <p>Show the mesh of the current model.</p>

    <!-- Delete Button -->
    <q-btn @click="deleteData">
      <q-icon name="fas fa-trash" /> Delete
    </q-btn>
    <p>Model data, user data, or cookies can be deleted.</p>

    <!-- Expand Button -->
    <q-btn @click="expand">
      <q-icon name="fullscreen" /> Expand
    </q-btn>
  </div>
  </template>
  

<script>

export default {
    name: "ButtonPage",
};
</script>

<style>
img {
    width: 100%;
}
</style>