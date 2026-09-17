<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { ContactGroup, ContactModel } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const contact = $derived(modelStore.modelData.contact);
  const blocks = $derived(modelStore.modelData.blocks ?? []);
  const contactModels = $derived(contact.contactModels ?? []);
  const contactTypes = ['Penalty Contact'];

  function addContactModel() {
    if (!contact.contactModels) contact.contactModels = [];
    const list = contact.contactModels;
    const len = list.length;
    const newItem =
      len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as ContactModel) : ({} as ContactModel);
    newItem.contactModelId = len + 1;
    newItem.name = `Contact Model ${len + 1}`;
    list.push(newItem);
  }

  function removeContactModel(index: number) {
    contactModels.splice(index, 1);
    contactModels.forEach((m, i) => (m.contactModelId = i + 1));
  }

  function addContactGroup(index: number) {
    const model = contactModels[index]!;
    if (!model.contactGroups) model.contactGroups = [];
    const list = model.contactGroups;
    const len = list.length;
    const newItem =
      len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as ContactGroup) : ({} as ContactGroup);
    newItem.contactGroupId = len + 1;
    newItem.name = `Contact Group ${len + 1}`;
    list.push(newItem);
  }

  function removeContactGroup(index: number, subindex: number) {
    contactModels[index]!.contactGroups.splice(subindex, 1);
  }
</script>

<div class="space-y-3 p-3">
  <Toggle bind:checked={contact.enabled} label="Enabled" />

  {#if contact.enabled}
    <div class="flex flex-wrap items-end gap-3 border-t border-border pt-3">
      <div class="w-40 space-y-1">
        <Label for="contact-freq">Search Frequency</Label>
        <Input id="contact-freq" type="number" bind:value={contact.searchFrequency} />
      </div>
      <Toggle bind:checked={contact.onlySurfaceContactNodes} label="Only Surface Contact Nodes" />
    </div>

    {#each contactModels as model, index (model.contactModelId ?? index)}
      <div class="space-y-2 border-t border-border pt-3">
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`cm-name-${index}`}>Name</Label>
            <Input id={`cm-name-${index}`} bind:value={model.name} />
          </div>
          <div class="space-y-1">
            <Label for={`cm-type-${index}`}>Type</Label>
            <Select id={`cm-type-${index}`} bind:value={model.contactType}>
              {#each contactTypes as type (type)}
                <option value={type}>{type}</option>
              {/each}
            </Select>
          </div>
          <div class="w-32 space-y-1">
            <Label for={`cm-radius-${index}`}>Contact Radius</Label>
            <Input id={`cm-radius-${index}`} type="number" bind:value={model.contactRadius} />
          </div>
          <div class="w-32 space-y-1">
            <Label for={`cm-stiff-${index}`}>Contact Stiffness</Label>
            <Input id={`cm-stiff-${index}`} type="number" bind:value={model.contactStiffness} />
          </div>
          <Button variant="ghost" size="icon" onclick={() => removeContactModel(index)} title="Remove Contact Model">
            <Trash2 class="h-4 w-4" />
          </Button>
        </div>

        {#each model.contactGroups ?? [] as group, subindex (group.contactGroupId ?? subindex)}
          <div class="ml-4 flex flex-wrap items-end gap-3 border-t border-border pt-2">
            <div class="space-y-1">
              <Label for={`cg-name-${index}-${subindex}`}>Name</Label>
              <Input id={`cg-name-${index}-${subindex}`} bind:value={group.name} />
            </div>
            <div class="space-y-1">
              <Label for={`cg-master-${index}-${subindex}`}>Master Block Id</Label>
              <Select id={`cg-master-${index}-${subindex}`} bind:value={group.masterBlockId}>
                {#each blocks as block, blockIdx (block.blocksId ?? blockIdx)}
                  <option value={block.blocksId}>{block.blocksId}</option>
                {/each}
              </Select>
            </div>
            <div class="space-y-1">
              <Label for={`cg-slave-${index}-${subindex}`}>Slave Block Id</Label>
              <Select id={`cg-slave-${index}-${subindex}`} bind:value={group.slaveBlockId}>
                {#each blocks as block, blockIdx (block.blocksId ?? blockIdx)}
                  <option value={block.blocksId}>{block.blocksId}</option>
                {/each}
              </Select>
            </div>
            <div class="w-32 space-y-1">
              <Label for={`cg-radius-${index}-${subindex}`}>Search Radius</Label>
              <Input id={`cg-radius-${index}-${subindex}`} type="number" bind:value={group.searchRadius} />
            </div>
            <Button
              variant="ghost"
              size="icon"
              onclick={() => removeContactGroup(index, subindex)}
              title="Remove Contact Group"
            >
              <Trash2 class="h-4 w-4" />
            </Button>
          </div>
        {/each}

        <Button variant="outline" size="sm" class="ml-4" onclick={() => addContactGroup(index)}>
          <Plus class="h-4 w-4" /> Add Contact Group
        </Button>
      </div>
    {/each}

    <Button variant="outline" size="sm" onclick={addContactModel}>
      <Plus class="h-4 w-4" /> Add Contact Model
    </Button>
  {/if}
</div>
