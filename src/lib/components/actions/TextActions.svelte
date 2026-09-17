<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Save } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { config } from '$lib/config';
  import { getStatus, viewInputFile as viewInputFileApi, writeInputFile as writeInputFileApi, OpenAPI } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';

  const modelData = $derived(modelStore.modelData);

  let connection: WebSocket | null = null;
  let debug = $state(false);
  let lastLine = '';

  function viewInputFile() {
    viewInputFileApi({
      modelName: modelStore.selectedModel.file,
      modelFolderName: modelData.model.modelFolderName
    })
      .then((response) => {
        notify.positive('Inputfile loaded');
        viewStore.textOutput = response as unknown as string;
        viewStore.textId = 'input';
      })
      .catch((error) => notify.apiError(error));
  }

  function writeInputFile() {
    writeInputFileApi({
      modelName: modelStore.selectedModel.file,
      modelFolderName: modelData.model.modelFolderName,
      inputString: viewStore.textOutput
    })
      .then(() => notify.positive('Inputfile saved'))
      .catch((error) => notify.apiError(error));
  }

  function _getStatus() {
    getStatus({
      modelName: modelStore.selectedModel.file,
      modelFolderName: modelData.model.modelFolderName,
      meshfile: modelData.model.meshFile!,
      cluster: modelData.job.cluster,
      sbatch: modelData.job.sbatch
    })
      .then((response) => {
        notify.positive('Status updated');
        defaultStore.status = response;
      })
      .catch((error) => notify.apiError(error));
  }

  function enableWebsocket() {
    if (connection) {
      connection.close();
      connection = null;
    }
    const params = {
      model_name: modelStore.selectedModel.file,
      model_folder_name: modelData.model.modelFolderName,
      cluster: modelData.job.cluster,
      token: OpenAPI.TOKEN,
      user_name: defaultStore.username,
      debug
    };
    const queryString = Object.entries(params)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
      .join('&');

    let socketPath = `ws://${window.location.host}/ws?${queryString}`;
    if (window.location.protocol === 'https:') {
      socketPath = `wss://${window.location.host}/ws?${queryString}`;
    }
    if (config.dev) {
      socketPath = `ws://localhost:8000/ws?${queryString}`;
    }

    connection = new WebSocket(socketPath);
    connection.onmessage = (event) => {
      viewStore.logOutput = event.data;
      const lines = viewStore.logOutput.split('\n');
      const currentLastLine = lines[lines.length - 2];
      if (currentLastLine !== lastLine) {
        if (currentLastLine?.includes('[Info] Run ')) {
          viewStore.viewId = 'results';
        }
        if (currentLastLine?.includes('[Info] PeriLab finished') && connection) {
          connection.close();
          connection = null;
          _getStatus();
          bus.emit('getJobs' as never);
          if (defaultStore.status.submitted) notify.positive('PeriLab finished');
        }
        if (currentLastLine?.includes('[Error]') && connection) {
          connection.close();
          connection = null;
          _getStatus();
          bus.emit('getJobs' as never);
          if (defaultStore.status.submitted) notify.negative(currentLastLine);
        }
        lastLine = currentLastLine ?? '';
      }
    };
    connection.onerror = (event) => {
      console.error(event);
      notify.negative('Websocket error');
    };
    viewStore.textLoading = false;
  }

  onMount(() => {
    _getStatus();
    enableWebsocket();

    bus.on('enableWebsocket' as never, enableWebsocket);
    bus.on('viewInputFile' as never, viewInputFile);
    bus.on('getStatus' as never, _getStatus);

    return () => {
      bus.off('enableWebsocket' as never, enableWebsocket);
      bus.off('viewInputFile' as never, viewInputFile);
      bus.off('getStatus' as never, _getStatus);
      connection?.close();
    };
  });

  onDestroy(() => connection?.close());
</script>

<div class="flex items-center gap-1 border-b border-border bg-muted/30 px-2 py-1">
  <Button
    variant="ghost"
    size="icon"
    onclick={writeInputFile}
    disabled={!defaultStore.status.created || viewStore.textId !== 'input' || defaultStore.trial}
    title={defaultStore.trial ? 'Disabled in trial version' : 'Save Inputfile'}
  >
    <Save class="h-4 w-4" />
  </Button>
  <div class="flex-1"></div>
  <Toggle bind:checked={debug} label="Debug" />
</div>
