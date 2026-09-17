# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""One declaration per field, driving both the YAML writer and the frontend form.

The workflow this replaces: adding a simple new PeriLab input-deck variable used to mean
touching three places by hand - the Pydantic model (`support/base_models.py`), a new
`if field_is_set: data["Some Key"] = field` line in `support/writer/yaml_writer_perilab.py`,
and a matching input/toggle/select in the relevant `src/lib/components/expansions/*.svelte`
file. Those three were prone to drifting out of sync (a field renamed in one place but not
the others), and most of that writer/frontend code was mechanical repetition of the same
"take this value, maybe rename/cast it, write it out" pattern for straightforward scalar
fields.

`yaml_field()` lets a field declare that mapping once, at the point where the field itself is
defined:

    class Solver(BaseModel):
        damEnabled: Optional[bool] = yaml_field(
            None, yaml_key="Damage Models", ui_label="Damage Models", ui_widget="toggle", ui_group="Solver"
        )

Because Pydantic's `json_schema_extra` is emitted verbatim into the generated OpenAPI schema
(and from there into `src/lib/client/schemas.gen.ts` via `npm run client`), this same
declaration is what both:

  - `write_mapped_fields()` (below) reads on the backend to auto-populate the YAML writer's
    `data` dict for any field with a `yaml_key`, and
  - `SchemaForm.svelte` (frontend) reads to render an input/toggle/select for any field with
    a `ui_widget`, in `ui_group` order.

This intentionally only handles the common case: a scalar field that maps to one YAML key
with at most a type cast, and a UI control that's a plain input/toggle/select bound directly
to that field. Fields needing real structural logic - conditional branching (Solver's
Verlet-vs-Static block), nesting, computed/derived keys (Blocks' "Node Set N" naming), or
custom interactive UX (Material's stiffness-matrix calculator, BondFilters' 3D preview
geometry) - are NOT good candidates for this and should stay hand-written, same as before.
`write_mapped_fields()` is meant to run *first* in a writer method, with the hand-written
logic for the complex parts following it - see `yaml_writer_perilab.py`'s `solver()` for the
pattern.
"""

from typing import Any, Literal, Optional, Sequence

from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

UiWidget = Literal["text", "number", "toggle", "select", "hidden"]


def yaml_field(
    default: Any = ...,
    *,
    yaml_key: Optional[str] = None,
    yaml_cast: Optional[Literal["float", "int", "str"]] = None,
    ui_label: Optional[str] = None,
    ui_widget: Optional[UiWidget] = None,
    ui_group: Optional[str] = None,
    ui_order: int = 0,
    ui_options: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> FieldInfo:
    """Drop-in replacement for `pydantic.Field()` that additionally records the
    YAML-writer and frontend-form metadata described in this module's docstring.

    All the new parameters are optional - a field can declare only `yaml_key` (writer-only,
    no auto-rendered UI control), only `ui_widget`/`ui_group` (rendered in the UI but written
    out by hand-written writer logic), or both. Omitting all of them makes this behave exactly
    like a plain `Field()` call.
    """
    extra: dict[str, Any] = {}
    if yaml_key is not None:
        extra["yaml_key"] = yaml_key
    if yaml_cast is not None:
        extra["yaml_cast"] = yaml_cast
    if ui_label is not None:
        extra["ui_label"] = ui_label
    if ui_widget is not None:
        extra["ui_widget"] = ui_widget
    if ui_group is not None:
        extra["ui_group"] = ui_group
    if ui_order:
        extra["ui_order"] = ui_order
    if ui_options is not None:
        extra["ui_options"] = list(ui_options)

    return Field(default, json_schema_extra=extra or None, **kwargs)


def write_mapped_fields(model: BaseModel, data: dict) -> None:
    """Writes every field on `model` that declares a `yaml_key` (via `yaml_field()` above)
    into `data`, applying `yaml_cast` if present. Fields that are `None`/unset are skipped,
    same as the `check_if_defined()` guard the hand-written writer code already used
    everywhere - this is meant to be a drop-in replacement for that pattern for any field
    simple enough to not need custom logic.

    Note this does NOT skip `False` (unlike the old ad-hoc some `if self.solver_dict[id].x:`
    checks scattered through the original writer, which is a real hazard for boolean fields:
    a boolean set to `False` is a defined value, not an absence of one, and dropping it
    silently falls back to PeriLab's own default instead of explicitly disabling the option -
    that's the kind of subtle bug this consolidation is meant to prevent, not reproduce.
    """
    for name, field in type(model).model_fields.items():
        extra = field.json_schema_extra
        if not isinstance(extra, dict):
            continue
        yaml_key = extra.get("yaml_key")
        if not yaml_key:
            continue

        value = getattr(model, name)
        if value is None:
            continue

        cast = extra.get("yaml_cast")
        if cast == "float":
            value = float(value)
        elif cast == "int":
            value = int(value)
        elif cast == "str":
            value = str(value)

        data[yaml_key] = value
