<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Tabs } from 'bits-ui';
  import Card from '$lib/components/ui/Card.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import SeriesLineChart from '$lib/components/views/SeriesLineChart.svelte';
  import CodeBlock from '$lib/components/views/CodeBlock.svelte';

  const amplitudeTypes = ['Type 1', 'Type 2', 'Sinus'];

  let amplitude = $state({
    max: 10,
    min: 2,
    frequency: 5,
    end: 5,
    type: 'Type 1'
  });

  let valueOutput = $state('A*sin(B*(t-C))+D');
  let tab = $state('plotly');

  let plotData = $state<{ name: string; x: number[]; y: number[] }[]>([
    { name: 'Load', x: [1, 2, 3, 4], y: [10, 15, 20, 17] }
  ]);

  function plotType1() {
    const { max, min, frequency, end } = amplitude;
    const n = 10 * frequency;
    const x: number[] = [];
    const y: number[] = [];
    for (let i = 0; i < n; i++) {
      const t = (i / (n - 1)) * end;
      x[i] = t;
      for (let j = 0; j < frequency; j++) {
        if (j === 0) {
          if (t <= (1 / frequency) * end) {
            y[i] = (t / ((1 / frequency) * end)) * max;
            break;
          }
        } else if (j % 2 !== 0) {
          if ((j / frequency) * end < t && t <= ((j + 1) / frequency) * end) {
            y[i] = max - ((t - (j / frequency) * end) / ((1 / frequency) * end)) * (max - min);
            break;
          }
        } else {
          if ((j / frequency) * end < t && t <= ((j + 1) / frequency) * end) {
            y[i] = min + ((t - (j / frequency) * end) / ((1 / frequency) * end)) * (max - min);
            break;
          }
        }
      }
    }
    plotData = [{ ...plotData[0], x, y }];
    valueOutput =
      `double max = ${max};\n` +
      `double min = ${min};\n` +
      `double frequency = ${frequency};\n` +
      `double end = ${end};\n` +
      'int idx = 0;\n' +
      'while (idx < frequency) {\n' +
      ' if (idx == 0) {\n' +
      '   if (t <= 1 / frequency *end) {\n' +
      '     value = (t / ((1 / frequency) * end)) * max;\n' +
      '   }\n' +
      ' }\n' +
      ' else if (idx % 2 != 0) {\n' +
      '   if ((idx / frequency *end < t) && (t <= (idx + 1) / frequency *end)) {\n' +
      '     value = max - ((t - (idx / frequency) * end) / ((1 / frequency) * end)) * (max - min);\n' +
      '   }\n' +
      ' }\n' +
      ' else if (idx % 2 == 0) {\n' +
      '   if ((idx / frequency *end < t) && (t <= (idx + 1) / frequency *end)) {\n' +
      '     value = min + ((t - (idx / frequency) * end) / ((1 / frequency) * end)) * (max - min);\n' +
      '   }\n' +
      ' }\n' +
      ' idx = idx + 1;\n' +
      '}\n';
  }

  function plotType2() {
    const { max, frequency, end } = amplitude;
    const n = 1000;
    const x: number[] = [];
    const y: number[] = [];
    for (let i = 0; i < n; i++) {
      const t = (i / (n - 1)) * end;
      x[i] = t;
      for (let j = 0; j < frequency; j++) {
        if (j === 0) {
          if (t <= (1 / frequency) * end) {
            y[i] = (t / end) * max * 2;
            break;
          }
        } else if (j % 2 !== 0) {
          if ((j / frequency) * end < t && t <= ((j + 1) / frequency) * end) {
            y[i] = (j / frequency) * max * 2 - ((j - 1) / frequency) * max;
            break;
          }
        } else {
          if ((j / frequency) * end < t && t <= ((j + 1) / frequency) * end) {
            y[i] = ((t - ((j / 2) * end) / frequency) / end) * max * 2;
            break;
          }
        }
      }
    }
    plotData = [{ ...plotData[0], x, y }];
    valueOutput =
      `double max = ${max};\n` +
      `double frequency = ${frequency};\n` +
      `double end = ${end};\n` +
      'int idx = 0;\n' +
      'while (idx < frequency) {\n' +
      ' if (idx == 0) {\n' +
      '   if (t <= 1 / frequency *end) {\n' +
      '     value = (t / end) * max * 2;\n' +
      '   }\n' +
      ' }\n' +
      ' else if (idx % 2 != 0) {\n' +
      '   if ((idx / frequency *end < t) && (t <= (idx + 1) / frequency *end)) {\n' +
      '     value = (idx / frequency) * max * 2 - ((idx - 1) / frequency) * max;\n' +
      '   }\n' +
      ' }\n' +
      ' else if (idx % 2 == 0) {\n' +
      '   if ((idx / frequency *end < t) && (t <= (idx + 1) / frequency *end)) {\n' +
      '     value = ((t - ((idx / 2) * end) / frequency) / end) * max * 2;\n' +
      '   }\n' +
      ' }\n' +
      ' idx = idx + 1;\n' +
      '}\n';
  }

  function plotSin() {
    const { max, min, frequency, end } = amplitude;
    const n = 100 * frequency;
    const offset = (max + min) / 2;
    const R = (max - min) / 2;
    const x: number[] = [];
    const y: number[] = [];
    for (let i = 0; i < n; i++) {
      const t = (i / (n - 1)) * end;
      x[i] = t;
      y[i] = R * Math.sin(2 * Math.PI * frequency * t - Math.PI / 2) + offset;
    }
    plotData = [{ ...plotData[0], x, y }];
    valueOutput = `${R} * sin(2 * pi * ${frequency} * t - pi / 2) + ${offset}`;
  }

  function replot() {
    if (amplitude.type === 'Type 1') plotType1();
    else if (amplitude.type === 'Type 2') plotType2();
    else plotSin();

    if (typeof window !== 'undefined') {
      localStorage.setItem('amplitude', JSON.stringify(amplitude));
    }
  }

  $effect(() => {
    // re-run whenever any amplitude field changes
    void amplitude.max;
    void amplitude.min;
    void amplitude.frequency;
    void amplitude.end;
    void amplitude.type;
    replot();
  });

  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('amplitude');
    if (stored) {
      try {
        amplitude = { ...amplitude, ...JSON.parse(stored) };
      } catch {
        /* ignore malformed cache */
      }
    }
  }
</script>

<Card class="w-full max-w-4xl p-5">
  <h2 class="text-lg font-semibold">Amplitude Generator</h2>

  <div class="my-4 border-t border-border"></div>

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,16rem)_1fr]">
    <div class="space-y-3">
      <div class="space-y-1">
        <Label for="amp-max">Max</Label>
        <Input id="amp-max" type="number" bind:value={amplitude.max} />
      </div>
      {#if amplitude.type !== 'Type 2'}
        <div class="space-y-1">
          <Label for="amp-min">Min</Label>
          <Input id="amp-min" type="number" bind:value={amplitude.min} />
        </div>
      {/if}
      <div class="space-y-1">
        <Label for="amp-freq">Frequency</Label>
        <Input id="amp-freq" type="number" bind:value={amplitude.frequency} />
      </div>
      <div class="space-y-1">
        <Label for="amp-end">Time</Label>
        <Input id="amp-end" type="number" bind:value={amplitude.end} />
      </div>
      <div class="space-y-1">
        <Label for="amp-type">Type of Amplitude</Label>
        <Select id="amp-type" bind:value={amplitude.type}>
          {#each amplitudeTypes as type (type)}
            <option value={type}>{type}</option>
          {/each}
        </Select>
      </div>
    </div>

    <Tabs.Root bind:value={tab}>
      <Tabs.List class="flex gap-1 border-b border-border">
        <Tabs.Trigger
          value="plotly"
          class="rounded-t-md px-3 py-2 text-sm font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground"
        >
          Plot
        </Tabs.Trigger>
        <Tabs.Trigger
          value="output"
          class="rounded-t-md px-3 py-2 text-sm font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground"
        >
          Output
        </Tabs.Trigger>
      </Tabs.List>
      <Tabs.Content value="plotly" class="pt-3">
        <SeriesLineChart series={plotData} />
      </Tabs.Content>
      <Tabs.Content value="output" class="pt-3">
        <CodeBlock bind:value={valueOutput} editable={false} />
      </Tabs.Content>
    </Tabs.Root>
  </div>
</Card>
