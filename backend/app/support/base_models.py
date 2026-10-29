import json
from datetime import datetime
from pathlib import Path
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class VersionData(BaseModel):
    current: str
    latest: str
    perilab_current: str
    perilab_latest: str


class UsageSummary(BaseModel):
    """Aggregate usage stats - see routers/usage.py."""

    total_jobs_submitted: int = 0
    total_jobs_cancelled: int = 0
    jobs_per_user: dict[str, int] = {}
    jobs_per_model: dict[str, int] = {}


class LicenseStatus(BaseModel):
    """Current entitlement grant - see support/license_client.py and
    support/entitlements.py."""

    plan: str
    features: List[str]
    seats: Optional[int] = None
    expires_at: Optional[str] = None
    source: str  # "license_server" | "cache" | "default"
    license_server_configured: bool


class PointData(BaseModel):
    points: List[float]
    block_ids: List[float]
    dx_value: float


class Strict(BaseModel):
    """Unknown fields are errors: an old camelCase config must fail loudly instead of loading with values missing."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Parameter(Strict):
    parameterId: Optional[int] = None
    id: List[str]
    std: float


class OldParameter(Strict):
    parameterId: Optional[int] = None
    id: List[str]
    factor: float


class Deviations(Strict):
    enabled: bool
    fileInput: Optional[bool] = None
    sampleSize: int
    parameters: List[Parameter]
    oldParameters: Optional[List[OldParameter]] = []
    file: Optional[str] = None
    mean: Optional[float] = None
    std: Optional[float] = None


class Valve(BaseModel):
    name: str
    type: Literal["text", "number", "select", "checkbox", "data"]
    value: Union[int, float, bool, str]
    value_type: Literal["int", "float", "bool", "str"]
    label: str
    description: str
    options: Optional[Union[List[str], str]] = None
    depends: Optional[str] = None


default_valves = {
    "valves": [
        {
            "name": "DISCRETIZATION",
            "type": "number",
            "value": 21,
            "value_type": "float",
            "label": "Discretization",
            "description": "Discretization",
            "options": None,
            "depends": None,
        },
        {
            "name": "LENGTH",
            "type": "number",
            "value": 13,
            "value_type": "float",
            "label": "Length",
            "description": "Length",
            "options": None,
            "depends": None,
        },
        {
            "name": "HEIGHT1",
            "type": "number",
            "value": 1,
            "value_type": "float",
            "label": "Inner Height",
            "description": "Inner Height",
            "options": None,
            "depends": None,
        },
        {
            "name": "HEIGHT2",
            "type": "number",
            "value": 2,
            "value_type": "float",
            "label": "Outer Height",
            "description": "Outer Height",
            "options": None,
            "depends": None,
        },
        {
            "name": "WIDTH",
            "type": "number",
            "value": 0.1,
            "value_type": "float",
            "label": "Width",
            "description": "Width",
            "options": None,
            "depends": None,
        },
        {
            "name": "STRUCTURED",
            "type": "checkbox",
            "value": True,
            "value_type": "bool",
            "label": "Structured",
            "description": "Structured",
            "options": None,
            "depends": None,
        },
    ],
}


class Valves(BaseModel):
    valves: List[Valve]

    class Config:
        json_schema_extra = {"example": default_valves}


class AnalysisInfo(BaseModel):
    """One @analysis function of a model (GET /models/{name}/analyses)."""

    id: str
    label: str
    params: List[Valve]


class Status(BaseModel):
    """Folder-level summary: model-config existence plus a snapshot of the
    *most recently submitted* run for this model_name/model_folder_name.
    A folder can have more than one run over time (re-submissions) - use
    `run_id` with GET /jobs/{run_id} for authoritative detail on that
    specific run, or GET /jobs/runs for
    the full history, rather than assuming this is "the" run."""

    created: Optional[bool] = False
    submitted: Optional[bool] = False
    results: Optional[bool] = False
    csvResults: Optional[bool] = False
    meshfileExist: Optional[bool] = False
    progress: Optional[float] = None
    currentStep: Optional[int] = None
    totalSteps: Optional[int] = None
    run_id: Optional[str] = None


# JobQueueEntry.status values (db/models.py JOB_*): queued/running are active, the rest are final.
JobStatus = Literal["queued", "running", "done", "failed", "cancelled"]


class RunSubmitted(BaseModel):
    """A submitted run: poll GET /jobs/{run_id} (`get_run`) until its status is final."""

    run_id: str
    status: JobStatus
    perilab_job_id: Optional[str] = None


class RunCancelled(BaseModel):
    cancelled: str


class RunDeleted(BaseModel):
    deleted: str


class GenerateResult(BaseModel):
    """What generate_model wrote into the model folder; the folder can now be submitted with run_model."""

    model_name: str
    model_folder_name: str
    nodes: Optional[int] = None  # None for an uploaded mesh (its points aren't counted)
    blocks: int


class VariableRange(BaseModel):
    min: float
    max: float


class OutputSummary(BaseModel):
    """One Exodus output at its last written time step."""

    name: str = Field(description='Output name, e.g. "Output1"; deviation runs add their number ("Output1_2")')
    last_step: int = Field(description="Index of the last written time step (0 = initial state)")
    final_time: float
    variables: dict[str, VariableRange] = Field(
        description="Min/max of every point variable at that step, per component (`Displacementsx`); vectors "
        "also as magnitude under their base name (`Displacements`)"
    )
    globals: dict[str, float] = Field(description="Global variables at that step, e.g. External_Forcesx")


class ColumnSummary(BaseModel):
    final: float
    min: float
    max: float


class RunSummary(BaseModel):
    """Compact digest of a run's results, small enough to reason about. Heavy data stays behind get_results
    (Exodus download), get_plot (full CSV series) and run_analysis (PNG)."""

    run_id: str
    status: JobStatus
    outputs: list[OutputSummary]
    csv: dict[str, dict[str, ColumnSummary]] = Field(
        description="CSV outputs by name: final/min/max of every numeric column over all steps"
    )
    analyses: list[str] = Field(description="ids of the model's @analysis functions, usable with run_analysis")


class RunStatus(BaseModel):
    """Full status of a single run, keyed by its own id (JobQueueEntry.id -
    stable for the life of the run, independent of how many times its
    model_name/model_folder_name has been resubmitted before or since).
    This is the authoritative per-run detail; Status/Jobs only carry a
    same-shaped snapshot of the latest run for quick folder-level display.
    `status`: queued/running are active; done, failed and cancelled are final."""

    id: str
    model_name: str
    model_folder_name: str
    status: JobStatus
    perilab_job_id: Optional[str] = None
    submitted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None
    results: bool = False
    csvResults: bool = False
    progress: Optional[float] = None
    currentStep: Optional[int] = None
    totalSteps: Optional[int] = None
    # The run's model folder, or a finished run's output folder, is gone from the simulations volume (deleted or
    # moved by hand, cleaned up by PeriLab, or the volume was swapped) - its log, input deck or result files can't
    # be loaded any more.
    files_missing: bool = False
    # Saved input deck (ModelData) of the run's model folder - only filled
    # by GET /jobs/runs, so the job list can load a run back into the editor.
    model: Optional[dict] = None


class Entry(Strict):
    """One named entry of a PeriLab section. `params` holds its PeriLab keys verbatim (YAML key -> value, offered
    by the frontend from src/lib/perilab/schema.json); the other fields are PeriHub concepts the writer turns into
    PeriLab keys (support/writer/yaml_writer_perilab.py)."""

    name: str
    params: dict[str, Any] = {}


class Model(Strict):
    modelFolderName: str
    # "model": points come from the selected model's generator; "upload": the user uploads `meshFile`.
    meshSource: Literal["model", "upload"] = "model"
    twoDimensional: bool
    horizon: Optional[float] = None
    meshFile: Optional[str] = None


class MaterialProperty(Strict):
    materialsPropId: Optional[int] = None
    name: str
    value: Optional[float] = None


class EngineeringConstants(Strict):
    """Input of the frontend's stiffness-matrix calculator (writes C11..C66 into `params`); never written."""

    calculate: bool = False
    E1: Optional[float] = None
    E2: Optional[float] = None
    E3: Optional[float] = None
    G12: Optional[float] = None
    G13: Optional[float] = None
    G23: Optional[float] = None
    nu12: Optional[float] = None
    nu13: Optional[float] = None
    nu23: Optional[float] = None


class Material(Entry):
    materialsId: Optional[int] = None
    libraryId: Optional[str] = None  # library material (/library/material) this copy was loaded from
    # User material (UMAT/VUMAT) constants: written as "Number of Properties" plus one key per property.
    properties: List[MaterialProperty] = []
    engineeringConstants: Optional[EngineeringConstants] = None


class ContactGroup(Entry):
    contactGroupId: Optional[int] = None


class ContactModel(Entry):
    contactModelId: Optional[int] = None
    contactGroups: List[ContactGroup] = []


class Contact(Strict):
    params: dict[str, Any] = {}  # Contact.Globals
    contactModels: List[ContactModel] = []


class ThermalModel(Entry):
    thermalModelsId: Optional[int] = None


class AdditiveModel(Entry):
    additiveModelId: Optional[int] = None


class InterBlock(Strict):
    interBlockid: Optional[int] = None
    firstBlockId: int
    secondBlockId: int
    value: float


class CriticalEnergyCalc(Strict):
    """Input of the frontend's K1C calculator (writes Critical Value into `params`); never written."""

    calculateCriticalEnergy: bool = False
    k1c: Optional[float] = None


class Damage(Entry):
    damagesId: Optional[int] = None
    interBlocks: List[InterBlock] = []
    criticalEnergyCalc: Optional[CriticalEnergyCalc] = None


class Block(Entry):
    blocksId: int
    show: Optional[bool] = None


class BlockFunction(Strict):
    id: int
    function: str


class Gcode(Strict):
    params: dict[str, Any] = {}
    blockFunctions: List[BlockFunction] = []


class NodeSet(Strict):
    nodeSetId: Optional[int] = None
    file: str


class Discretization(Strict):
    discType: str = "txt"  # "txt" | "e" | "gcode": mesh file format, set by the model/mesh upload
    params: dict[str, Any] = {}
    gcode: Optional[Gcode] = None
    nodeSets: List[NodeSet] = []


class BoundaryCondition(Entry):
    conditionsId: Optional[int] = None
    stepId: List[int] = [1]
    nodeSet: Optional[int] = None
    blockId: Optional[int] = None


class BoundaryConditions(Strict):
    conditions: List[BoundaryCondition]


class BondFilters(Entry):
    bondFiltersId: Optional[int] = None
    show: Optional[bool] = None


class Compute(Entry):
    computesId: Optional[int] = None
    nodeSetId: Optional[int] = None


class Output(Entry):
    outputsId: Optional[int] = None
    selectedOutputs: List[str] = []


class Solver(Strict):
    solverId: Optional[int] = None
    name: Optional[str] = None  # step name in a Multistep Solver
    stepId: int = 1
    solvertype: str  # the solver sub-section, e.g. "Verlet"; its keys are in solverOptions
    params: dict[str, Any] = {}
    solverOptions: dict[str, Any] = {}


class Job(Strict):
    verbose: bool
    tasks: Optional[int] = 1


# Frontend imports the same file as its initial model
default_model = json.loads(
    (Path(__file__).resolve().parent.parent / "assets" / "default_model.json").read_text(encoding="UTF-8")
)


class ModelData(Strict):
    additive: List[AdditiveModel] = []
    blocks: List[Block]
    bondFilters: List[BondFilters] = []
    boundaryConditions: BoundaryConditions
    computes: List[Compute] = []
    contact: Contact = Contact()
    damages: List[Damage] = []
    discretization: Discretization = Discretization()
    deviations: Optional[Deviations] = None
    job: Job
    materials: List[Material] = []
    model: Model
    outputs: List[Output]
    solvers: List[Solver]
    thermal: List[ThermalModel] = []

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class AnalysisRequest(BaseModel):
    data: ModelData
    valves: Valves
    analysis_params: dict[str, Union[int, float, bool, str]] = {}
