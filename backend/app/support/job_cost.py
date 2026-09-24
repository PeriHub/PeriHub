# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Pre-submit cost/resource estimation (Phase 3).

Deliberately advisory, never blocking: this returns a tier + optional
warning string for the frontend to show before the user confirms, not a
reason to reject the submission server-side. `node_count` isn't populated
by ModelData yet (see routers/jobs.py's existing comment on
`getattr(model_data.discretization, "nodeCount", None)`), so this mostly
returns "unknown" until that field exists - the thresholds and tiering are
in place now so wiring it up later is a one-line change, not a new module.
"""

from dataclasses import dataclass

from .globals import job_cost_block_confirm_node_count, job_cost_warn_node_count


@dataclass
class CostEstimate:
    tier: str  # "unknown" | "small" | "medium" | "large"
    warning: str | None = None
    requires_confirmation: bool = False


def estimate_job_cost(node_count: int | None) -> CostEstimate:
    if node_count is None:
        return CostEstimate(tier="unknown")

    if node_count >= job_cost_block_confirm_node_count:
        return CostEstimate(
            tier="large",
            warning=(
                f"This mesh has {node_count:,} nodes, well above the usual size for a shared instance. "
                "It may run for a long time and use a large share of the shared local solver slot - "
                "consider a cluster/sbatch submission instead."
            ),
            requires_confirmation=True,
        )
    if node_count >= job_cost_warn_node_count:
        return CostEstimate(
            tier="medium",
            warning=f"This mesh has {node_count:,} nodes - expect a longer run than a typical small model.",
        )
    return CostEstimate(tier="small")
