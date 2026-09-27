# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
from datetime import datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel

from .yaml_field import yaml_field


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


class PointDataResults(BaseModel):
    nodes: List[float]
    value: List[float]
    variables: List[str]
    number_of_steps: int
    min_value: float
    max_value: float
    time: float


class PointData(BaseModel):
    points: List[float]
    block_ids: List[float]
    dx_value: float


class Parameter(BaseModel):
    parameterId: Optional[int] = None
    id: List[str]
    std: float


class OldParameter(BaseModel):
    parameterId: Optional[int] = None
    id: List[str]
    factor: float


class Deviations(BaseModel):
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
    "analysisValves": [],
}


class Valves(BaseModel):
    valves: List[Valve]
    analysisValves: List[Valve]

    class Config:
        json_schema_extra = {"example": default_valves}


class Status(BaseModel):
    """Folder-level summary: model-config existence plus a snapshot of the
    *most recently submitted* run for this model_name/model_folder_name.
    A folder can have more than one run over time (re-submissions) - use
    `run_id` with GET /jobs/{run_id} for authoritative detail on that
    specific run, or GET /jobs/{model_name}/{model_folder_name}/runs for
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


class RunStatus(BaseModel):
    """Full status of a single run, keyed by its own id (JobQueueEntry.id -
    stable for the life of the run, independent of how many times its
    model_name/model_folder_name has been resubmitted before or since).
    This is the authoritative per-run detail; Status/Jobs only carry a
    same-shaped snapshot of the latest run for quick folder-level display."""

    id: str
    model_name: str
    model_folder_name: str
    status: str
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
    # Saved input deck (ModelData) of the run's model folder - only filled
    # by GET /jobs/runs, so the job list can load a run back into the editor.
    model: Optional[dict] = None


class Model(BaseModel):
    modelFolderName: str
    ownModel: bool
    twoDimensional: bool
    ownMesh: Optional[bool] = None
    horizon: Optional[float] = None
    meshFile: Optional[str] = None


class Jobs(BaseModel):
    """Folder-level summary row (one per model_folder_name variant that
    exists on disk). `run_id`/`run_count` describe the folder's run
    history at a glance; submitted/results/progress reflect only the
    *latest* run - see GET /jobs/{model_name}/{model_folder_name}/runs
    for the full history and GET /jobs/{run_id} for a specific run."""

    id: int
    name: str
    sub_name: str
    created: bool
    submitted: bool
    results: bool
    model: Optional[dict] = None
    progress: Optional[float] = None
    currentStep: Optional[int] = None
    totalSteps: Optional[int] = None
    run_id: Optional[str] = None
    run_count: int = 0


class properties(BaseModel):
    materialsPropId: Optional[int] = None
    name: str
    value: Optional[float] = None


class EngineeringConstants(BaseModel):
    E1: Optional[float] = None
    E2: Optional[float] = None
    E3: Optional[float] = None
    G12: Optional[float] = None
    G13: Optional[float] = None
    G23: Optional[float] = None
    nu12: Optional[float] = None
    nu13: Optional[float] = None
    nu23: Optional[float] = None


class Matrix(BaseModel):
    C11: Optional[float] = None
    C12: Optional[float] = None
    C13: Optional[float] = None
    C14: Optional[float] = None
    C15: Optional[float] = None
    C16: Optional[float] = None
    C22: Optional[float] = None
    C23: Optional[float] = None
    C24: Optional[float] = None
    C25: Optional[float] = None
    C26: Optional[float] = None
    C33: Optional[float] = None
    C34: Optional[float] = None
    C35: Optional[float] = None
    C36: Optional[float] = None
    C44: Optional[float] = None
    C45: Optional[float] = None
    C46: Optional[float] = None
    C55: Optional[float] = None
    C56: Optional[float] = None
    C66: Optional[float] = None


class StiffnessMatrix(BaseModel):
    calculateStiffnessMatrix: Optional[bool] = None
    engineeringConstants: EngineeringConstants
    matrix: Matrix


class Material(BaseModel):
    materialsId: Optional[int] = None
    name: str
    matType: List[str]
    bulkModulus: Optional[float] = None
    shearModulus: Optional[float] = None
    shearModulusXY: Optional[float] = None
    shearModulusYZ: Optional[float] = None
    shearModulusXZ: Optional[float] = None
    youngsModulus: Optional[float] = None
    youngsModulusX: Optional[float] = None
    youngsModulusY: Optional[float] = None
    youngsModulusZ: Optional[float] = None
    poissonsRatio: Optional[float] = None
    poissonsRatioXY: Optional[float] = None
    poissonsRatioYZ: Optional[float] = None
    poissonsRatioXZ: Optional[float] = None
    planeStress: bool
    planeStrain: bool
    materialSymmetry: str
    stabilizationType: str
    hourglassCoefficient: float
    actualHorizon: Optional[float] = None
    yieldStress: Optional[float] = None
    stiffnessMatrix: Optional[StiffnessMatrix] = None
    properties: Union[List[properties], None]
    numStateVars: Optional[int] = None
    computePartialStress: Optional[bool] = None
    useCollocationNodes: Optional[bool] = None


class ContactGroup(BaseModel):
    contactGroupId: Optional[int] = None
    name: str
    masterBlockId: int
    slaveBlockId: int
    searchRadius: float


class ContactModel(BaseModel):
    contactModelId: Optional[int] = None
    name: str
    contactType: str
    contactRadius: float
    contactStiffness: float
    contactGroups: List[ContactGroup]


class Contact(BaseModel):
    enabled: bool
    contactModels: Optional[List[ContactModel]] = None
    searchFrequency: Optional[int] = None
    onlySurfaceContactNodes: Optional[bool] = None


class ThermalModel(BaseModel):
    thermalModelsId: Optional[int] = None
    name: str
    thermalModel: List[str]
    thermalType: str
    heatTransferCoefficient: Optional[float] = None
    environmentalTemperature: Optional[float] = None
    requiredSpecificVolume: Optional[float] = None
    thermalConductivity: Optional[float] = None
    thermalExpansionCoefficient: Optional[float] = None
    thermalConductivityPrintBed: Optional[float] = None
    printBedTemperature: Optional[float] = None
    printBedZCoord: Optional[float] = None
    file: Optional[str] = None
    numStateVars: Optional[int] = None
    predefinedFieldNames: Optional[str] = None


class Thermal(BaseModel):
    enabled: bool
    thermalModels: Optional[List[ThermalModel]] = None


class AdditiveModel(BaseModel):
    additiveModelId: Optional[int] = None
    name: str
    additiveType: str
    printTemp: float
    # timeFactor: float


class Additive(BaseModel):
    enabled: bool
    additiveModels: Optional[List[AdditiveModel]] = None


class InterBlock(BaseModel):
    interBlockid: Optional[int] = None
    firstBlockId: int
    secondBlockId: int
    value: float


class CriticalEnergyCalc(BaseModel):
    calculateCriticalEnergy: Optional[bool] = None
    k1c: Optional[float] = None


class Damage(BaseModel):
    damagesId: Optional[int] = None
    name: str
    damageModel: str
    criticalStretch: Optional[float] = None
    criticalVonMisesStress: Optional[float] = None
    criticalDamage: Optional[float] = None
    thresholdDamage: Optional[float] = None
    criticalDamageToNeglect: Optional[float] = None
    criticalEnergy: Optional[float] = None
    criticalEnergyCalc: Optional[CriticalEnergyCalc] = None
    interBlockDamage: Optional[bool] = None
    numberOfBlocks: Optional[int] = None
    interBlocks: Optional[List[InterBlock]] = None
    anistropicDamage: Optional[bool] = None
    anistropicDamageX: Optional[float] = None
    anistropicDamageY: Optional[float] = None
    anistropicDamageZ: Optional[float] = None
    onlyTension: Optional[bool] = None
    # detachedNodesCheck: Optional[bool] = None
    thickness: Optional[float] = None
    # hourglassCoefficient: float
    # stabilizationType: str


class Block(BaseModel):
    blocksId: int
    name: str
    material: str = None
    damageModel: Optional[str] = None
    thermalModel: Optional[str] = None
    additiveModel: Optional[str] = None
    horizon: Optional[float] = None
    density: Optional[float] = None
    specificHeatCapacity: Union[Optional[float], Optional[str]] = None
    show: Optional[bool] = None


class BlockFunction(BaseModel):
    id: int
    function: str


class Gcode(BaseModel):
    overwriteMesh: bool
    sampling: float
    width: float
    height: float
    scale: float
    blockFunctions: Optional[List[BlockFunction]] = None


class NodeSet(BaseModel):
    nodeSetId: Optional[int] = None
    file: str


class Discretization(BaseModel):
    distributionType: str
    discType: Optional[str] = "txt"
    gcode: Optional[Gcode] = None
    nodeSets: Optional[List[NodeSet]] = None


class BoundaryCondition(BaseModel):
    conditionsId: Optional[int] = None
    stepId: Optional[List[int]] = [1]
    name: str
    nodeSet: Optional[int] = None
    boundarytype: str
    variable: str
    blockId: Optional[int] = None
    coordinate: str
    value: str


class BoundaryConditions(BaseModel):
    conditions: List[BoundaryCondition]


class BondFilters(BaseModel):
    bondFiltersId: Optional[int] = None
    name: str
    type: str
    allow_contact: Optional[bool] = False
    normalX: float
    normalY: float
    normalZ: float
    lowerLeftCornerX: Optional[float] = None
    lowerLeftCornerY: Optional[float] = None
    lowerLeftCornerZ: Optional[float] = None
    bottomUnitVectorX: Optional[float] = None
    bottomUnitVectorY: Optional[float] = None
    bottomUnitVectorZ: Optional[float] = None
    bottomLength: Optional[float] = None
    sideLength: Optional[float] = None
    centerX: Optional[float] = None
    centerY: Optional[float] = None
    centerZ: Optional[float] = None
    radius: Optional[float] = None
    show: Optional[bool] = None


class Compute(BaseModel):
    computesId: Optional[int] = None
    computeClass: str
    name: str
    variable: str
    equation: Optional[str] = None
    calculationType: Optional[str] = None
    blockName: Optional[str] = None
    nodeSetId: Optional[int] = None
    xValue: Optional[float] = None
    yValue: Optional[float] = None
    zValue: Optional[float] = None


class PreCalculations(BaseModel):
    deformedBondGeometry: Optional[bool] = None
    deformationGradient: Optional[bool] = None
    shapeTensor: Optional[bool] = None
    bondAssociatedShapeTensor: Optional[bool] = None
    bondAssociateDeformationGradient: Optional[bool] = None


class Output(BaseModel):
    outputsId: Optional[int] = None
    name: str
    selectedFileType: Optional[str] = "Exodus"
    selectedOutputs: Optional[List[str]] = None

    Write_After_Damage: Optional[bool] = None
    Frequency: Optional[int] = 100
    numberOfOutputSteps: Optional[int] = 100
    useOutputFrequency: Optional[bool] = False
    InitStep: int


class Verlet(BaseModel):
    numericalDamping: Optional[float] = None
    outputFrequency: int = 1000


class Static(BaseModel):
    numberOfSteps: int
    maximumNumberOfIterations: Optional[int] = None
    NLsolver: Optional[bool] = None
    showSolverIteration: Optional[bool] = None
    residualTolerance: Optional[float] = None
    solutionTolerance: Optional[float] = None
    linearStartValue: Optional[List[float]] = None
    residualScaling: Optional[float] = None
    m: Optional[int] = None


class Adapt(BaseModel):
    stableStepDifference: int = 4
    maximumBondDifference: int = 10
    stableBondDifference: int = 4


class Solver(BaseModel):
    solverId: Optional[int] = None
    name: Optional[str] = None
    stepId: int = 1
    matEnabled: bool = yaml_field(
        True, yaml_key="Material Models", ui_label="Material Models", ui_widget="toggle", ui_group="Solver", ui_order=1
    )
    damEnabled: Optional[bool] = yaml_field(
        None, yaml_key="Damage Models", ui_label="Damage Models", ui_widget="toggle", ui_group="Solver", ui_order=2
    )
    dispEnabled: Optional[bool] = None
    tempEnabled: Optional[bool] = yaml_field(
        None, yaml_key="Thermal Models", ui_label="Thermal Models", ui_widget="toggle", ui_group="Solver", ui_order=3
    )
    addEnabled: Optional[bool] = yaml_field(
        None, yaml_key="Additive Models", ui_label="Additive Models", ui_widget="toggle", ui_group="Solver", ui_order=4
    )
    initialTime: Optional[float] = yaml_field(
        None,
        yaml_key="Initial Time",
        yaml_cast="float",
        ui_label="Initial Time",
        ui_widget="number",
        ui_group="Solver",
        ui_order=10,
    )
    finalTime: Optional[float] = yaml_field(
        None,
        yaml_key="Final Time",
        yaml_cast="float",
        ui_label="Final Time",
        ui_widget="number",
        ui_group="Solver",
        ui_order=11,
    )
    # additionalTime and initialTime/finalTime are mutually exclusive in the
    # written YAML (see yaml_writer_perilab.py's solver()) - that XOR is
    # structural logic, so additionalTime intentionally has no yaml_key here
    # even though it's a simple scalar; it's written by hand alongside the
    # branch that decides which of the two to emit.
    additionalTime: Optional[float] = None
    fixedDt: Optional[float] = yaml_field(None, ui_label="Fixed dt", ui_widget="number", ui_group="Verlet", ui_order=0)
    solvertype: str = yaml_field(
        ..., ui_label="Solvertype", ui_widget="select", ui_options=["Verlet", "Static"], ui_group="Solver", ui_order=0
    )
    safetyFactor: float = yaml_field(
        ..., yaml_cast="float", ui_label="Safety Factor", ui_widget="number", ui_group="Verlet", ui_order=1
    )
    verlet: Optional[Verlet] = None
    static: Optional[Static] = None
    stopAfterDamageInitation: Optional[bool] = None
    endStepAfterDamage: Optional[int] = None
    stopAfterCertainDamage: Optional[bool] = None
    maximumDamage: Optional[float] = yaml_field(
        None,
        yaml_key="Maximum Damage",
        yaml_cast="float",
        ui_label="Max. damage value",
        ui_widget="number",
        ui_group="Solver",
        ui_order=14,
    )
    stopBeforeDamageInitation: Optional[bool] = None
    adaptivetimeStepping: Optional[bool] = yaml_field(
        None, ui_label="Adaptive Time Stepping", ui_widget="toggle", ui_group="Verlet", ui_order=1
    )
    adapt: Optional[Adapt] = None
    calculateCauchy: Optional[bool] = yaml_field(
        None,
        yaml_key="Calculate Cauchy",
        ui_label="Calculate Cauchy",
        ui_widget="toggle",
        ui_group="Verlet",
        ui_order=2,
    )
    calculateVonMises: Optional[bool] = yaml_field(
        None,
        yaml_key="Calculate von Mises stress",
        ui_label="Calculate von Mises",
        ui_widget="toggle",
        ui_group="Verlet",
        ui_order=3,
    )
    calculateStrain: Optional[bool] = yaml_field(
        None,
        yaml_key="Calculate Strain",
        ui_label="Calculate Strain",
        ui_widget="toggle",
        ui_group="Verlet",
        ui_order=4,
    )


class Job(BaseModel):
    verbose: bool = yaml_field(..., ui_label="Verbose", ui_widget="toggle", ui_group="Job", ui_order=0)
    tasks: Optional[int] = 1


default_model = {
    "additive": {"additiveModels": None, "enabled": False},
    "blocks": [
        {
            "additiveModel": "",
            "blocksId": 1,
            "damageModel": "Damage",
            "density": 2.699e-09,
            "horizon": None,
            "material": "Aluminium",
            "name": "Part",
            "show": True,
            "specificHeatCapacity": None,
            "thermalModel": None,
        },
        {
            "additiveModel": "",
            "blocksId": 2,
            "damageModel": "",
            "density": 2.699e-09,
            "horizon": None,
            "material": "BC",
            "name": "Top_BC",
            "show": True,
            "specificHeatCapacity": None,
            "thermalModel": None,
        },
        {
            "additiveModel": "",
            "blocksId": 3,
            "damageModel": "",
            "density": 2.699e-09,
            "horizon": None,
            "material": "BC",
            "name": "Bottom_BC",
            "show": True,
            "specificHeatCapacity": None,
            "thermalModel": None,
        },
        {
            "additiveModel": "",
            "blocksId": 4,
            "damageModel": "",
            "density": 2.699e-09,
            "horizon": None,
            "material": "Aluminium",
            "name": "Top_Part",
            "show": True,
            "specificHeatCapacity": None,
            "thermalModel": None,
        },
        {
            "additiveModel": "",
            "blocksId": 5,
            "damageModel": "",
            "density": 2.699e-09,
            "horizon": None,
            "material": "Aluminium",
            "name": "Bottom_Part",
            "show": True,
            "specificHeatCapacity": None,
            "thermalModel": None,
        },
    ],
    "bondFilters": [
        {
            "allow_contact": False,
            "bottomLength": 56.75,
            "bottomUnitVectorX": 1.0,
            "bottomUnitVectorY": 0.0,
            "bottomUnitVectorZ": 0.0,
            "centerX": 0.0,
            "centerY": 1.0,
            "centerZ": 0.0,
            "id": None,
            "lowerLeftCornerX": -0.5,
            "lowerLeftCornerY": 0.0,
            "lowerLeftCornerZ": -2.0,
            "name": "bf_1",
            "normalX": 0.0,
            "normalY": 1.0,
            "normalZ": 0.0,
            "radius": 1.0,
            "show": True,
            "sideLength": 4.0,
            "type": "Rectangular_Plane",
        }
    ],
    "boundaryConditions": {
        "conditions": [
            {
                "blockId": 2,
                "boundarytype": "Dirichlet",
                "conditionsId": 1,
                "coordinate": "y",
                "name": "BC_1",
                "nodeSet": None,
                "stepId": [1],
                "value": "1000*t",
                "variable": "Displacements",
            },
            {
                "blockId": 3,
                "boundarytype": "Dirichlet",
                "conditionsId": 2,
                "coordinate": "y",
                "name": "BC_2",
                "nodeSet": None,
                "stepId": [1],
                "value": "-1000*t",
                "variable": "Displacements",
            },
        ]
    },
    "computes": [
        {
            "blockName": "Bottom_BC",
            "calculationType": "Sum",
            "computeClass": "Block_Data",
            "id": 1,
            "name": "External_Force",
            "nodeSetId": None,
            "variable": "Forces",
            "xValue": None,
            "yValue": None,
            "zValue": None,
        },
        {
            "blockName": "Top_BC",
            "calculationType": "Maximum",
            "computeClass": "Block_Data",
            "id": 2,
            "name": "External_Displacement",
            "nodeSetId": None,
            "variable": "Displacements",
            "xValue": None,
            "yValue": None,
            "zValue": None,
        },
    ],
    "contact": {"contactModels": None, "enabled": False, "onlySurfaceContactNodes": None, "searchFrequency": None},
    "damages": [
        {
            "anistropicDamage": False,
            "anistropicDamageX": None,
            "anistropicDamageY": None,
            "anistropicDamageZ": None,
            "criticalDamage": None,
            "criticalDamageToNeglect": None,
            "criticalEnergy": 5.714285714285715,
            "criticalEnergyCalc": {"calculateCriticalEnergy": True, "k1c": 632.4555320336759},
            "criticalStretch": None,
            "criticalVonMisesStress": None,
            "damageModel": "Critical Energy",
            "id": 1,
            "interBlockDamage": False,
            "interBlocks": [],
            "name": "Damage",
            "numberOfBlocks": None,
            "onlyTension": True,
            "thickness": 1.0,
            "thresholdDamage": None,
        }
    ],
    "deviations": {
        "enabled": False,
        "sampleSize": 10,
        "parameters": [{"id": ["materials[0].youngsModulus"], "std": 10}],
    },
    "discretization": {"discType": "txt", "distributionType": "Neighbor based", "gcode": None, "nodeSets": None},
    "job": {"tasks": 1, "verbose": False},
    "materials": [
        {
            "actualHorizon": None,
            "bulkModulus": None,
            "computePartialStress": None,
            "hourglassCoefficient": 1.0,
            "id": 1,
            "matType": ["PD Solid Elastic"],
            "materialSymmetry": "Isotropic",
            "name": "BC",
            "numStateVars": None,
            "planeStrain": False,
            "planeStress": True,
            "poissonsRatio": 0.35,
            "properties": [{"id": 1, "name": "Prop_1", "value": None}],
            "shearModulus": None,
            "stabilizationType": "Global Stiffness",
            "stiffnessMatrix": None,
            "useCollocationNodes": None,
            "yieldStress": None,
            "youngsModulus": 200000.0,
        },
        {
            "actualHorizon": None,
            "bulkModulus": None,
            "computePartialStress": None,
            "hourglassCoefficient": 1.0,
            "id": 1,
            "matType": ["Correspondence Elastic", "Correspondence Plastic"],
            "materialSymmetry": "Isotropic",
            "name": "Aluminium",
            "numStateVars": None,
            "planeStrain": False,
            "planeStress": True,
            "poissonsRatio": 0.35,
            "properties": [{"id": 1, "name": "Prop_1", "value": None}],
            "shearModulus": None,
            "stabilizationType": "Global Stiffness",
            "stiffnessMatrix": None,
            "useCollocationNodes": None,
            "yieldStress": 350.0,
            "youngsModulus": 70000.0,
        },
    ],
    "model": {
        "horizon": None,
        "meshFile": None,
        "modelFolderName": "Default",
        "ownMesh": None,
        "ownModel": False,
        "twoDimensional": True,
    },
    "outputs": [
        {
            "Frequency": 1,
            "InitStep": 0,
            "Write_After_Damage": False,
            "name": "Output1",
            "numberOfOutputSteps": 100,
            "outputsId": None,
            "selectedFileType": "Exodus",
            "selectedOutputs": ["Displacements", "Damage", "Cauchy Stress", "Strain", "Number of Neighbors"],
            "useOutputFrequency": False,
        },
        {
            "Frequency": 100,
            "InitStep": 0,
            "Write_After_Damage": False,
            "name": "Output2",
            "numberOfOutputSteps": 500,
            "outputsId": 2,
            "selectedFileType": "CSV",
            "selectedOutputs": ["External_Force", "External_Displacement"],
            "useOutputFrequency": False,
        },
    ],
    "preCalculations": None,
    "solvers": [
        {
            "adapt": {"maximumBondDifference": 4, "stableBondDifference": 1, "stableStepDifference": 4},
            "adaptivetimeStepping": False,
            "addEnabled": None,
            "additionalTime": None,
            "calculateCauchy": None,
            "calculateStrain": True,
            "calculateVonMises": True,
            "damEnabled": True,
            "dispEnabled": True,
            "endStepAfterDamage": 3,
            "finalTime": 0.0005,
            "fixedDt": None,
            "initialTime": 0.0,
            "matEnabled": True,
            "maxDamageValue": 0.3,
            "name": None,
            "safetyFactor": 0.95,
            "solverId": None,
            "solvertype": "Verlet",
            "static": None,
            "stepId": 1,
            "stopAfterCertainDamage": False,
            "stopAfterDamageInitation": False,
            "stopBeforeDamageInitation": False,
            "tempEnabled": False,
            "verlet": {"numericalDamping": 5e-06, "outputFrequency": 100, "safetyFactor": 0.95},
        }
    ],
    "thermal": {"enabled": False, "thermalModels": None},
}


class ModelData(BaseModel):
    additive: Optional[Additive] = None
    blocks: List[Block]
    bondFilters: Optional[List[BondFilters]] = None
    boundaryConditions: BoundaryConditions
    computes: Optional[List[Compute]] = None
    contact: Optional[Contact] = None
    damages: Optional[List[Damage]] = None
    discretization: Optional[Discretization] = None
    deviations: Optional[Deviations] = None
    job: Job
    materials: List[Material]
    model: Model
    outputs: List[Output]
    preCalculations: Optional[PreCalculations] = None
    solvers: List[Solver]
    thermal: Optional[Thermal] = None

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    class Config:
        json_schema_extra = {"example": default_model}
