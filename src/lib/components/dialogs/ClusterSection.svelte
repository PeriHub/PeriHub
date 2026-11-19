<script lang="ts">
  import { Copy } from 'lucide-svelte';
  import {
    deleteClusterProfile,
    generateClusterKey,
    getClusterProfile,
    saveClusterProfile,
    testClusterConnection
  } from '$lib/client';
  import type { ClusterProfileIn, ClusterProfileOut, ClusterTestResult } from '$lib/client';
  import { publicConfig } from '$lib/config';
  import { notify } from '$lib/utils/notify';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';

  // Slurm cluster jobs with the user's own login (enterprise, backend ee/cluster.py).
  let saved = $state<ClusterProfileOut | null>(null);
  let form = $state<ClusterProfileIn>({
    host: publicConfig.clusterHosts[0] ?? '',
    port: 22,
    username: '',
    account: '',
    perilab_path: '$HOME/perilab',
    workdir: '~/perihub',
    partition: '',
    time_limit: '01:00:00',
    job_template: null
  });
  let template = $state('');
  let test = $state<ClusterTestResult | null>(null);
  let busy = $state(false);

  function fill(profile: ClusterProfileOut) {
    saved = profile;
    const { public_key, host_key_fingerprint, default_job_template, ...fields } = profile;
    void public_key;
    void host_key_fingerprint;
    form = fields;
    template = profile.job_template ?? default_job_template ?? '';
  }

  async function load() {
    try {
      fill(await getClusterProfile());
    } catch {
      saved = null; // 404: no profile yet
    }
  }

  async function run(action: () => Promise<void>) {
    busy = true;
    try {
      await action();
    } catch (error) {
      notify.apiError(error);
    } finally {
      busy = false;
    }
  }

  const save = () =>
    run(async () => {
      // Unchanged default stays null, so later fixes to the default template still apply.
      const custom = saved && template.trim() !== saved.default_job_template?.trim();
      fill(
        await saveClusterProfile({
          requestBody: { ...form, job_template: custom ? template : null }
        })
      );
      notify.positive('Cluster profile saved');
    });

  const newKey = () =>
    run(async () => {
      await generateClusterKey();
      test = null;
      await load();
    });

  const testConnection = () =>
    run(async () => {
      test = await testClusterConnection();
      await load();
    });

  const remove = () =>
    run(async () => {
      if (!confirm('Delete your cluster profile and its SSH key?')) return;
      await deleteClusterProfile();
      saved = null;
      test = null;
    });

  async function copyKey() {
    if (!saved?.public_key) return;
    await navigator.clipboard.writeText(saved.public_key);
    notify.positive('Public key copied');
  }

  load();
</script>

<section class="border-border mt-4 border-t pt-3">
  <h3 class="text-muted-foreground mb-2 text-xs font-semibold tracking-wide uppercase">Cluster</h3>
  <p class="text-muted-foreground mb-3 text-xs">
    Run jobs on a Slurm cluster with your own login and account. PeriHub connects over SSH with a
    key it generates for you.
  </p>

  <form
    class="grid grid-cols-2 gap-2 text-sm"
    onsubmit={(e) => {
      e.preventDefault();
      save();
    }}
  >
    <div class="col-span-2 grid gap-1">
      <Label for="cl-host">Host</Label>
      <Input id="cl-host" list="cl-hosts" bind:value={form.host} required />
      <datalist id="cl-hosts">
        {#each publicConfig.clusterHosts as host (host)}
          <option value={host}></option>
        {/each}
      </datalist>
    </div>
    <div class="grid gap-1">
      <Label for="cl-user">Username</Label>
      <Input id="cl-user" bind:value={form.username} required />
    </div>
    <div class="grid gap-1">
      <Label for="cl-account">Slurm account</Label>
      <Input id="cl-account" bind:value={form.account} required />
    </div>
    <div class="col-span-2 grid gap-1">
      <Label for="cl-perilab">PeriLab path (Julia project)</Label>
      <Input id="cl-perilab" bind:value={form.perilab_path} required />
    </div>
    <div class="col-span-2 grid gap-1">
      <Label for="cl-workdir">Work directory</Label>
      <Input id="cl-workdir" bind:value={form.workdir} />
    </div>
    <div class="grid gap-1">
      <Label for="cl-partition">Partition</Label>
      <Input id="cl-partition" placeholder="cluster default" bind:value={form.partition} />
    </div>
    <div class="grid gap-1">
      <Label for="cl-time">Time limit</Label>
      <Input id="cl-time" bind:value={form.time_limit} />
    </div>
    {#if saved}
      <div class="col-span-2 grid gap-1">
        <Label for="cl-template">Job script</Label>
        <textarea
          id="cl-template"
          class="border-input bg-background min-h-40 rounded-md border p-2 font-mono text-xs"
          bind:value={template}
        ></textarea>
        <button
          type="button"
          class="text-muted-foreground justify-self-start text-xs underline"
          onclick={() => (template = saved?.default_job_template ?? '')}
        >
          Reset to default
        </button>
      </div>
    {/if}
    <div class="col-span-2 flex gap-2">
      <Button type="submit" size="sm" disabled={busy}>Save</Button>
      {#if saved}
        <Button type="button" size="sm" variant="ghost" disabled={busy} onclick={remove}>
          Delete
        </Button>
      {/if}
    </div>
  </form>

  {#if saved}
    <div class="mt-3 space-y-2 text-sm">
      {#if saved.public_key}
        <p class="text-xs">Add this line to <code>~/.ssh/authorized_keys</code> on the cluster:</p>
        <div class="flex items-center gap-2">
          <code class="bg-muted min-w-0 flex-1 truncate rounded px-2 py-1 text-xs"
            >{saved.public_key}</code
          >
          <Button size="sm" variant="outline" onclick={copyKey} aria-label="Copy public key">
            <Copy class="h-4 w-4" />
          </Button>
        </div>
      {/if}
      <div class="flex gap-2">
        <Button size="sm" variant="outline" disabled={busy} onclick={newKey}>
          {saved.public_key ? 'New SSH key' : 'Generate SSH key'}
        </Button>
        {#if saved.public_key}
          <Button size="sm" variant="outline" disabled={busy} onclick={testConnection}>
            Test connection
          </Button>
        {/if}
      </div>
      {#if saved.host_key_fingerprint}
        <p class="text-muted-foreground text-xs">
          Host key: <code>{saved.host_key_fingerprint}</code>
        </p>
      {/if}
      {#if test}
        <p class="text-xs {test.ok ? 'text-success' : 'text-warning-foreground'}">
          {test.ok
            ? `Connected: ${test.sbatch}`
            : test.perilab_found
              ? `sbatch not available: ${test.sbatch}`
              : 'PeriLab path not found on the cluster'}
        </p>
      {/if}
    </div>
  {/if}
</section>
