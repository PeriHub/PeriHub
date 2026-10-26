<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { ContactGroup, ContactModel, Contact } from '$lib/client';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import ParamLabel from '$lib/components/ParamLabel.svelte';
  import SchemaParams from '$lib/components/SchemaParams.svelte';
  import { sections, node, modelNames, pick, CUSTOM_KEYS } from '$lib/perilab/schema';

  const contact = $derived(modelStore.modelData.contact ?? ({} as Contact));
  const blocks = $derived(modelStore.modelData.blocks ?? []);
  const contactModels = $derived(contact.contactModels ?? []);

  function addContactModel() {
    if (!contact.contactModels) contact.contactModels = [];
    const list = contact.contactModels;
    const len = list.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(list[len - 1])) as ContactModel)
        : ({ params: { Type: 'Penalty Contact' }, contactGroups: [] } as unknown as ContactModel);
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
      len > 0
        ? (structuredClone($state.snapshot(list[len - 1])) as ContactGroup)
        : ({ params: {} } as unknown as ContactGroup);
    newItem.contactGroupId = len + 1;
    newItem.name = `Contact Group ${len + 1}`;
    list.push(newItem);
  }

  function removeContactGroup(index: number, subindex: number) {
    contactModels[index]!.contactGroups?.splice(subindex, 1);
  }
</script>

<div class="space-y-3 p-3">
  <SchemaParams entry={sections.contactGlobals} values={contact.params!} idPrefix="contact" />

  {#each contactModels as model, index (index)}
    <div class="border-border space-y-2 border-t pt-3">
      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`cm-name-${index}`}>Name</Label>
          <Input id={`cm-name-${index}`} bind:value={model.name} />
        </div>
        <div class="space-y-1">
          <ParamLabel
            key="Type"
            for={`cm-type-${index}`}
            required
            prop={sections.contact?.properties?.Type}
          />
          <Select id={`cm-type-${index}`} bind:value={model.params!['Type']}>
            {#each pick(modelNames(sections.contact), ['Penalty Contact'], String(model.params?.Type ?? '')) as type (type)}
              <option value={type}>{type}</option>
            {/each}
          </Select>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onclick={() => removeContactModel(index)}
          title="Remove Contact Model"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      {#each model.contactGroups ?? [] as group, subindex (subindex)}
        <div class="border-border ml-4 flex flex-wrap items-end gap-3 border-t pt-2">
          <div class="space-y-1">
            <Label for={`cg-name-${index}-${subindex}`}>Name</Label>
            <Input id={`cg-name-${index}-${subindex}`} bind:value={group.name} />
          </div>
          <div class="space-y-1">
            <ParamLabel
              key="Master Block ID"
              for={`cg-master-${index}-${subindex}`}
              required
              prop={node(['Contact Groups', '*'], sections.contact)?.properties?.[
                'Master Block ID'
              ]}
            />
            <Select
              id={`cg-master-${index}-${subindex}`}
              bind:value={group.params!['Master Block ID']}
            >
              {#each blocks as block, blockIdx (blockIdx)}
                <option value={block.blocksId}>{block.blocksId}</option>
              {/each}
            </Select>
          </div>
          <div class="space-y-1">
            <ParamLabel
              key="Slave Block ID"
              for={`cg-slave-${index}-${subindex}`}
              required
              prop={node(['Contact Groups', '*'], sections.contact)?.properties?.['Slave Block ID']}
            />
            <Select
              id={`cg-slave-${index}-${subindex}`}
              bind:value={group.params!['Slave Block ID']}
            >
              {#each blocks as block, blockIdx (blockIdx)}
                <option value={block.blocksId}>{block.blocksId}</option>
              {/each}
            </Select>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onclick={() => removeContactGroup(index, subindex)}
            title="Remove Contact Group"
          >
            <Trash2 class="h-4 w-4" />
          </Button>
          <div class="basis-full">
            <SchemaParams
              entry={node(['Contact Groups', '*'], sections.contact)}
              values={group.params!}
              custom={CUSTOM_KEYS.contactGroup}
              idPrefix={`cg-${index}-${subindex}`}
            />
          </div>
        </div>
      {/each}

      <AddButton
        noun="contact group"
        items={model.contactGroups}
        class="ml-4"
        onclick={() => addContactGroup(index)}
      />

      <SchemaParams
        entry={sections.contact}
        values={model.params!}
        names={[String(model.params?.Type ?? '')]}
        custom={CUSTOM_KEYS.contact}
        idPrefix={`ct-${index}`}
      />
    </div>
  {/each}

  <AddButton noun="contact model" items={contactModels} onclick={addContactModel} />
</div>
