---
layout: default
title: Blocks
parent: Input
nav_order: 2
---

# Blocks

Most parts are easier to think of as a few distinct **regions** than as one blob.
A **block** is one such region, and here you decide which material and damage
rule apply to it.

The built-in models already split themselves into blocks and assign materials to
them. For a simple single-material part there is usually just one block.

| Setting      | What it controls                                                                    |
| ------------ | ----------------------------------------------------------------------------------- |
| Block name   | The name of the block.                                                              |
| Material     | The material to use in this block.                                                  |
| Damage model | The damage rule (see **[Damage Models](/input/DamageModels.html)**) for this block. |
| Show         | Toggle whether the block is visible in the 3-D view.                                |

When you change a block's material, PeriHub updates the whole part automatically.
If you add a new block, remember to give it a material and a damage model.
