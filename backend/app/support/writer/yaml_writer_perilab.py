# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Turns ModelData into the PeriLab input deck.

Every section entry carries its PeriLab keys verbatim in `params` (YAML key -> value, offered by the frontend from
PeriLab's schema, already typed), so this only adds what PeriHub derives itself: entry names, block ids, node sets,
interblock damage, user material properties, mesh files, output files/variables and the solver sub-section.
Derived keys are written after `params` and win. support/deck_guard.py still checks the result before submission.
"""

import numpy as np
import yaml
from fastapi import HTTPException

# Output variables PeriHub offers as one choice but PeriLab expects per component.
EXPANDED_OUTPUTS = {
    "Velocity_Gradient": ["Velocity_Gradient_X", "Velocity_Gradient_Y", "Velocity_Gradient_Z"],
    "PiolaStressTimesInvShapeTensor": [
        "PiolaStressTimesInvShapeTensorX",
        "PiolaStressTimesInvShapeTensorY",
        "PiolaStressTimesInvShapeTensorZ",
    ],
}
MESH_TYPES = {"txt": ("Text File", ".txt"), "e": ("Exodus", ".g"), "gcode": ("Gcode", ".gcode")}


def _clean(params: dict) -> dict:
    """Drops unset values (None, "") so PeriLab's defaults apply; nested sub-sections are cleaned too. numpy
    scalars (e.g. a generated Horizon, a deviations sample) are coerced to plain Python types, otherwise
    yaml.dump emits `!!python/object` tags that deck_guard.py's safe_load can't read back (a cryptic 422)."""
    out = {}
    for key, value in params.items():
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, dict):
            value = _clean(value)
        if value is None or value == "":
            continue
        out[key] = value
    return out


class YAMLcreatorPeriLab:
    def __init__(self, model_writer, block_def=None):
        self.filename = model_writer.filename
        self.ns_name = model_writer.ns_name
        self.node_set_ids = model_writer.node_set_ids
        self.block_def = block_def or []
        self.data = model_writer.model_data

    def discretization(self):
        disc = self.data.discretization
        mesh_type, suffix = MESH_TYPES[disc.discType]
        data = {
            **_clean(disc.params),
            "Type": mesh_type,
            "Input Mesh File": self.data.model.meshFile or self.filename + suffix,
        }
        if disc.discType != "e":
            if disc.nodeSets:
                data["Node Sets"] = {f"Node Set {ns.nodeSetId}": ns.file for ns in disc.nodeSets}
            elif disc.discType == "txt" and self.node_set_ids:
                data["Node Sets"] = {
                    f"Node Set {i + 1}": f"{self.ns_name}_{i + 1}.txt" for i in range(len(self.node_set_ids))
                }
        if disc.discType == "gcode" and disc.gcode is not None:
            gcode = _clean(disc.gcode.params)
            if disc.gcode.blockFunctions:
                gcode["Blocks"] = {block.id: block.function for block in disc.gcode.blockFunctions}
            data["Gcode"] = gcode
        if self.data.bondFilters:
            data["Bond Filters"] = {bf.name: _clean(bf.params) for bf in self.data.bondFilters}
        return data

    def materials(self):
        data = {}
        for mat in self.data.materials:
            material = _clean(mat.params)
            if mat.properties:
                material["Number of Properties"] = len(mat.properties)
                material.update({prop.name: prop.value for prop in mat.properties})
            data[mat.name] = material
        return data

    def _used(self, key):
        return {block.params.get(key) for block in self.block_def}

    def thermal(self):
        used = self._used("Thermal Model")
        return {t.name: _clean(t.params) for t in self.data.thermal if t.name in used}

    def additive(self):
        used = self._used("Additive Model")
        return {a.name: _clean(a.params) for a in self.data.additive if a.name in used}

    def blocks(self, max_block_id):
        return {
            block.name: {**_clean(block.params), "Block ID": block.blocksId}
            for block in self.block_def
            if block.blocksId <= max_block_id
        }

    def damage(self, max_block_id):
        data = {}
        for dam in self.data.damages:
            damage = _clean(dam.params)
            if any(ib.firstBlockId <= max_block_id and ib.secondBlockId <= max_block_id for ib in dam.interBlocks):
                damage["Interblock Damage"] = {
                    f"Interblock Critical Value {ib.firstBlockId}_{ib.secondBlockId}": float(ib.value)
                    for ib in dam.interBlocks
                }
            data[dam.name] = damage
        return data

    def solver(self, solver, multistep=False):
        if not solver.solvertype:
            raise HTTPException(status_code=400, detail="Solver not defined")
        data = _clean(solver.params)
        data[solver.solvertype] = _clean(solver.solverOptions)
        if multistep:
            data["Step ID"] = solver.stepId
        return data

    def multistep_solver(self):
        return {(s.name or f"Step {s.stepId}"): self.solver(s, True) for s in self.data.solvers}

    def boundary_conditions(self, multistep):
        data = {}
        for cond in self.data.boundaryConditions.conditions:
            bc = _clean(cond.params)
            node_set = cond.nodeSet or self.node_set_ids.index(cond.blockId) + 1
            bc["Node Set"] = f"Node Set {node_set}"
            if multistep and cond.stepId:
                bc["Step ID"] = ", ".join(str(step) for step in cond.stepId)
            data[cond.name] = bc
        return data

    def contact(self):
        contact = self.data.contact
        data = {"Globals": _clean(contact.params)}
        for model in contact.contactModels:
            data[model.name] = {
                **_clean(model.params),
                "Contact Groups": {group.name: _clean(group.params) for group in model.contactGroups},
            }
        return data

    def compute(self):
        data = {}
        for comp in self.data.computes:
            entry = _clean(comp.params)
            if comp.nodeSetId is not None:
                entry["Node Set"] = f"Node Set {comp.nodeSetId}"
            data[comp.name] = entry
        return data

    def output(self):
        computes = [comp.name for comp in self.data.computes]
        data = {}
        for idx, out in enumerate(self.data.outputs):
            variables = {v: True for name in out.selectedOutputs for v in EXPANDED_OUTPUTS.get(name, [name])}
            variables.update({name: True for name in computes})
            data[f"Output{idx + 1}"] = {
                **_clean(out.params),
                "Output Filename": f"{self.filename}_{out.name}",
                "Output Variables": variables,
            }
        return data

    def create_yaml(self, max_block_id):
        d = self.data
        multistep = len(d.solvers) > 1
        models = {}
        if d.materials:
            models["Material Models"] = self.materials()
        if thermal := self.thermal():
            models["Thermal Models"] = thermal
        if additive := self.additive():
            models["Additive Models"] = additive
        if d.damages:
            models["Damage Models"] = self.damage(max_block_id)

        deck = {"Models": models, "Discretization": self.discretization(), "Blocks": self.blocks(max_block_id)}
        if multistep:
            deck["Multistep Solver"] = self.multistep_solver()
        else:
            deck["Solver"] = self.solver(d.solvers[0])
        if d.boundaryConditions.conditions:
            deck["Boundary Conditions"] = self.boundary_conditions(multistep)
        if d.contact.contactModels:
            deck["Contact"] = self.contact()
        if d.computes:
            deck["Compute Class Parameters"] = self.compute()
        deck["Outputs"] = self.output()
        return yaml.dump({"PeriLab": deck}, default_flow_style=False)
