<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <!-- Existing content -->

    <h2>Building locally</h2>
    <p>Clone the repository:</p>
    <q-code>
      git clone https://gitlab.com/dlr-perihub/PeriHub/PeriHub.git
    </q-code>
    <p>Go into the perihub folder:</p>
    <q-code>
      cd perihub
    </q-code>
    <p>Create a .env file and save following variables:</p>
    <q-code>
      DEV=True
      DLR=False
      VOLUME={PATHTOJOBFOLDER}
    </q-code>
    <p>Run docker-compose:</p>
    <q-code>
      docker-compose up
    </q-code>
    <p>If docker finished building PeriHub, go to <a href="http://localhost:6010">http://localhost:6010</a></p>

    <h2>Contact</h2>
    <ul>
      <li><a href="mailto:Jan-Timo.Hesse@dlr.de">Jan-Timo Hesse</a></li>
    </ul>
  </div>
</template>
  

<script>

export default {
    name: "GettingStartedPage",
};
</script>

<style>
img {
    width: 100%;
}
</style>