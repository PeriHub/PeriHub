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
  import {
    getStatus,
    viewInputFile as viewInputFileApi,
    writeInputFile as writeInputFileApi,
    OpenAPI
  } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';

  const modelData = $derived(modelStore.modelData);

  let connection: WebSocket | null = null;
  let debug = $state(false);
  let lastLine = '';
  let intentionalClose = false;
  let reconnectAttempts = 0;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  const MAX_RECONNECT_ATTEMPTS = 5;

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
    return getStatus({
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

  function closeConnection() {
    intentionalClose = true;
    connection?.close();
    connection = null;
  }

  function scheduleReconnect() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      viewStore.logStatus = 'error';
      viewStore.logStatusMessage =
        'Lost connection to the log stream. Reopen the Log tab to retry.';
      notify.negative(viewStore.logStatusMessage);
      return;
    }
    reconnectAttempts += 1;
    viewStore.logStatusMessage = `Connection lost, retrying (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`;
    reconnectTimer = setTimeout(() => enableWebsocket({ force: true }), 2000 * reconnectAttempts);
  }

  function enableWebsocket(payload?: { force?: boolean }) {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    closeConnection();

    // A plain call (mount, switching to the Log tab, a reconnect retry)
    // only opens the socket if a job is actually running for this model -
    // otherwise there is nothing to stream and we'd just sit in "waiting"
    // for minutes before reporting a misleading error. `force` is passed
    // right after a fresh submit, when the pid/log file may not exist on
    // disk quite yet but a job genuinely was just started.
    if (!payload?.force && !defaultStore.status.submitted) {
      viewStore.logStatus = 'idle';
      viewStore.logStatusMessage = '';
      return;
    }

    // Reset the log view for the new run: the backend now reports
    // "waiting for the log file" / "connected" / "log" / "error" states
    // itself, so the frontend just reflects whatever it's told instead of
    // guessing how long a job takes to start.
    viewStore.logOutput = '';
    viewStore.logStatus = 'waiting';
    viewStore.logStatusMessage = 'Connecting to the log stream...';
    lastLine = '';

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

    intentionalClose = false;
    connection = new WebSocket(socketPath);

    connection.onmessage = (event) => {
      reconnectAttempts = 0;

      let data: { status?: string; message?: string; content?: string };
      try {
        data = JSON.parse(event.data);
      } catch {
        // Defensive fallback in case anything ever sends a raw log payload.
        data = { status: 'log', content: event.data };
      }

      if (data.status === 'waiting') {
        viewStore.logStatus = 'waiting';
        viewStore.logStatusMessage = data.message ?? 'Waiting for the simulation to start...';
        return;
      }

      if (data.status === 'error') {
        viewStore.logStatus = 'error';
        viewStore.logStatusMessage =
          data.message ?? 'Something went wrong while streaming the log.';
        notify.negative(viewStore.logStatusMessage);
        closeConnection();
        return;
      }

      if (data.status === 'connected') {
        viewStore.logStatus = 'streaming';
        return;
      }

      // data.status === 'log'
      viewStore.logStatus = 'streaming';
      viewStore.logOutput = data.content ?? '';
      const lines = viewStore.logOutput.split('\n');
      const currentLastLine = lines[lines.length - 2];
      if (currentLastLine !== lastLine) {
        if (currentLastLine?.includes('[Info] Run ')) {
          viewStore.viewId = 'results';
        }
        if (currentLastLine?.includes('[Info] PeriLab finished') && connection) {
          closeConnection();
          _getStatus();
          bus.emit('getJobs' as never);
          if (defaultStore.status.submitted) notify.positive('PeriLab finished');
        }
        if (currentLastLine?.includes('[Error]') && connection) {
          closeConnection();
          _getStatus();
          bus.emit('getJobs' as never);
          if (defaultStore.status.submitted) notify.negative(currentLastLine);
        }
        lastLine = currentLastLine ?? '';
      }
    };
    connection.onerror = (event) => {
      console.error(event);
    };
    connection.onclose = () => {
      connection = null;
      if (intentionalClose) return;
      if (viewStore.logStatus === 'error') return;
      scheduleReconnect();
    };
    viewStore.textLoading = false;
  }

  function stopWebsocket() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    reconnectAttempts = 0;
    closeConnection();
    viewStore.logStatus = 'idle';
    viewStore.logStatusMessage = '';
  }

  onMount(() => {
    // On first load (or a page refresh mid-run), only reconnect the log
    // stream if a job actually turns out to be running for this model -
    // otherwise leave the Log tab idle instead of opening a socket with
    // nothing to show.
    _getStatus()?.then(() => {
      if (defaultStore.status.submitted) enableWebsocket({ force: true });
    });

    bus.on('enableWebsocket' as never, enableWebsocket);
    bus.on('stopWebsocket' as never, stopWebsocket);
    bus.on('viewInputFile' as never, viewInputFile);
    bus.on('getStatus' as never, _getStatus);

    return () => {
      bus.off('enableWebsocket' as never, enableWebsocket);
      bus.off('stopWebsocket' as never, stopWebsocket);
      bus.off('viewInputFile' as never, viewInputFile);
      bus.off('getStatus' as never, _getStatus);
      if (reconnectTimer) clearTimeout(reconnectTimer);
      closeConnection();
    };
  });

  onDestroy(() => {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    closeConnection();
  });
</script>

<div class="border-border bg-muted/30 flex items-center gap-1 border-b px-2 py-1">
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
