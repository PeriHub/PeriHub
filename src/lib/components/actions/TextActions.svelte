<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount, onDestroy, untrack } from 'svelte';
  import { Save } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import {
    getStatus,
    viewInputFile as viewInputFileApi,
    writeInputFile as writeInputFileApi,
    OpenAPI
  } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';

  const modelData = $derived(modelStore.modelData);

  let debug = $state(false);
  let lastLine = '';
  let abortController: AbortController | null = null;
  let retryTimer: ReturnType<typeof setTimeout> | null = null;
  let retryAttempts = 0;
  const MAX_RETRY_ATTEMPTS = 5;
  const RETRY_INTERVAL = 2000;

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
      meshfile: modelData.model.meshFile!
    })
      .then((response) => {
        // notify.positive('Status updated');
        defaultStore.status = response;
      })
      .catch((error) => notify.apiError(error));
  }

  function closeStream() {
    if (retryTimer) {
      clearTimeout(retryTimer);
      retryTimer = null;
    }
    abortController?.abort();
    abortController = null;
  }

  function stopStreaming() {
    closeStream();
    viewStore.logStatus = 'idle';
    viewStore.logStatusMessage = '';
  }

  function finishRun(message: string, ok: boolean) {
    const wasSubmitted = defaultStore.status.submitted;
    closeStream();
    _getStatus();
    bus.emit('getJobs' as never);
    if (wasSubmitted) {
      if (ok) notify.positive(message);
      else notify.negative(message);
    }
  }

  // Same end-of-run detection the old websocket used: the PeriLab API's
  // stream should close by itself when the job ends, but its job status can
  // lag (or stick at "running"), so don't wait on it.
  function checkLastLine() {
    const lines = viewStore.logOutput.split('\n');
    const currentLastLine = lines[lines.length - 2];
    if (currentLastLine === lastLine) return;
    lastLine = currentLastLine ?? '';

    if (currentLastLine?.includes('[Info] Run ')) {
      viewStore.viewId = 'results';
    }
    if (currentLastLine?.includes('[Info] PeriLab finished')) {
      finishRun('PeriLab finished', true);
    }
    if (currentLastLine?.includes('[Error]')) {
      finishRun(currentLastLine, false);
    }
  }

  function scheduleRetry(message: string) {
    if (retryAttempts >= MAX_RETRY_ATTEMPTS) {
      viewStore.logStatus = 'error';
      viewStore.logStatusMessage =
        'Lost connection to the log stream. Reopen the Log tab to retry.';
      notify.negative(viewStore.logStatusMessage);
      return;
    }
    retryAttempts += 1;
    viewStore.logStatus = 'waiting';
    viewStore.logStatusMessage = message;
    retryTimer = setTimeout(streamLog, RETRY_INTERVAL * retryAttempts);
  }

  // GET /jobs/{run_id}/log/stream proxies the PeriLab API's log stream: the
  // log so far, then new output as it is written. Read with fetch rather
  // than the generated client (axios can't hand out a response body
  // incrementally) or EventSource (can't send the Authorization header).
  async function streamLog() {
    retryTimer = null;
    const runId = defaultStore.status.run_id;
    if (!runId) {
      viewStore.logStatus = 'idle';
      viewStore.logStatusMessage = 'No active run';
      return;
    }

    closeStream();
    const controller = new AbortController();
    abortController = controller;

    try {
      const response = await fetch(
        `${OpenAPI.BASE}/jobs/${encodeURIComponent(runId)}/log/stream?debug=${debug}`,
        {
          headers: (OpenAPI.HEADERS ?? {}) as Record<string, string>,
          signal: controller.signal
        }
      );
      if (response.status === 404) {
        // No PeriLab job/log yet - the run is still starting.
        scheduleRetry('Waiting for the simulation to start...');
        return;
      }
      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Every (re)connect sends the whole log again, so start over.
      viewStore.logOutput = '';
      lastLine = '';
      viewStore.logStatus = 'streaming';
      viewStore.logStatusMessage = '';

      const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        retryAttempts = 0;
        viewStore.logOutput += value;
        checkLastLine();
      }

      // The API ended the stream: the job is over.
      if (abortController === controller) finishRun('PeriLab finished', true);
    } catch (error) {
      if (controller.signal.aborted) return; // closed on purpose
      console.error('Log stream error:', error);
      scheduleRetry('Connection lost, retrying...');
    }
  }

  // The [Debug] filter is applied server-side, so toggling it means
  // reconnecting (which resends the whole log) if a stream is open.
  $effect(() => {
    void debug;
    untrack(() => {
      if (abortController) streamLog();
    });
  });

  function startStreaming(payload?: { force?: boolean }) {
    closeStream();
    retryAttempts = 0;

    // Only stream if a job is actually running for this model
    if (!payload?.force && !defaultStore.status.submitted) {
      viewStore.logStatus = 'idle';
      viewStore.logStatusMessage = '';
      return;
    }

    viewStore.logOutput = '';
    viewStore.logStatus = 'waiting';
    viewStore.logStatusMessage = 'Connecting to the log stream...';
    lastLine = '';

    streamLog();
  }

  onMount(() => {
    // On first load (or a page refresh mid-run), only start streaming
    // if a job actually turns out to be running for this model
    _getStatus()?.then(() => {
      if (defaultStore.status.submitted) startStreaming({ force: true });
    });

    bus.on('enableWebsocket' as never, startStreaming);
    bus.on('stopWebsocket' as never, stopStreaming);
    bus.on('viewInputFile' as never, viewInputFile);
    bus.on('getStatus' as never, _getStatus);

    return () => {
      bus.off('enableWebsocket' as never, startStreaming);
      bus.off('stopWebsocket' as never, stopStreaming);
      bus.off('viewInputFile' as never, viewInputFile);
      bus.off('getStatus' as never, _getStatus);
      closeStream();
    };
  });

  onDestroy(closeStream);
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
