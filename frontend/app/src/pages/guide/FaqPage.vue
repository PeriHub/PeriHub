<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <h1>Frequently Asked Questions</h1>

    <q-card v-for="(item, index) in faqItems" :key="index">
      <q-card-section>
        <div class="text-h6">{{ item.question }}</div>
      </q-card-section>
      <q-card-section>
        <div>{{ item.answer }}</div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script>
export default {
  name: "FaqPage",
  data() {
    return {
      faqItems: [
        {
          question: "What is PeriHub?",
          answer: "PeriHub is a collaborative platform for conducting simulations and research tasks in material behavior.",
        },
        {
          question: "Is PeriHub user-friendly?",
          answer: "Yes, PeriHub offers a user-friendly interface accessible to both experienced researchers and newcomers.",
        },
        // Add more FAQ items as needed
      ],
    };
  },
};
</script>