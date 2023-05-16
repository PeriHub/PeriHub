# pylint: disable=no-name-in-module
import json
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel


class Status:
    def __init__(self, created, submitted, results):
        self.created = created
        self.submitted = submitted
        self.results = results


class Jobs:
    def __init__(self, id, name, sub_name, cluster, created, submitted, results, model):
        self.id = id
        self.name = name
        self.sub_name = sub_name
        self.cluster = cluster
        self.created = created
        self.submitted = submitted
        self.results = results
        self.model = model


class Model(BaseModel):
    modelNameSelected: str
    modelFolderName: Optional[str] = "Default"
    ownModel: bool
    ownMesh: Optional[bool] = None
    translated: bool
    length: float
    cracklength: Optional[float] = None
    notchEnabled: Optional[bool] = True
    width: Optional[float] = None
    height: Optional[float] = None
    height2: Optional[float] = None
    radius: Optional[float] = None
    structured: Optional[bool] = None
    discretization: int
    horizon: Optional[float] = None
    twoDimensional: bool
    rotatedAngles: bool
    angles: List[float]
    amplitudeFactor: Optional[float] = None
    wavelength: Optional[float] = None
    mesh_file: Optional[str] = None


class properties(BaseModel):
    id: Optional[int]
    name: str
    value: Optional[float] = None


class Parameter(BaseModel):
    name: str
    value: Optional[float] = None


class Material(BaseModel):
    id: Optional[int]
    name: str
    matType: str
    density: float
    bulkModulus: Optional[float] = None
    shearModulus: Optional[float] = None
    youngsModulus: Optional[float] = None
    poissonsRatio: Optional[float] = None
    tensionSeparation: bool
    nonLinear: bool
    planeStress: bool
    materialSymmetry: str
    stabilizationType: str
    thickness: float
    hourglassCoefficient: float
    actualHorizon: Optional[float] = None
    yieldStress: Optional[float] = None
    Parameter: Union[List[Parameter], None]
    properties: Union[List[properties], None]
    numStateVars: Optional[int] = None
    computePartialStress: Optional[bool] = None
    useCollocationNodes: Optional[bool] = None

    # Thermal
    enableThermal: Optional[bool] = None
    specificHeatCapacity: Optional[float] = None
    thermalConductivity: Optional[float] = None
    heatTransferCoefficient: Optional[float] = None
    applyThermalFlow: Optional[bool] = None
    applyThermalStrain: Optional[bool] = None
    applyHeatTransfer: Optional[bool] = None
    thermalBondBased: Optional[bool] = True
    thermalExpansionCoefficient: Optional[float] = None
    environmentalTemperature: Optional[float] = None

    # 3dPrint
    printBedTemperature: Optional[float] = None
    printBedThermalConductivity: Optional[float] = None
    volumeFactor: Optional[float] = None
    volumeLimit: Optional[float] = None
    surfaceCorrection: Optional[float] = None


class AdditiveModel(BaseModel):
    id: Optional[int]
    name: str
    additiveType: str
    printTemp: float
    timeFactor: float


class Additive(BaseModel):
    enabled: bool
    additiveModels: Union[List[AdditiveModel], None]


class InterBlock(BaseModel):
    id: Optional[int]
    firstBlockId: int
    secondBlockId: int
    value: float


class CriticalEnergyCalc(BaseModel):
    calculateCriticalEnergy: Optional[bool] = None
    k1c: Optional[float] = None


class Damage(BaseModel):
    id: Optional[int]
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
    planeStress: bool
    onlyTension: bool
    detachedNodesCheck: bool
    thickness: float
    hourglassCoefficient: float
    stabilizationType: str


class Block(BaseModel):
    id: Optional[int]
    name: str
    material: str
    damageModel: Optional[str] = None
    additiveModel: Optional[str] = None
    horizon: Optional[float] = None
    show: Optional[bool] = None


class ContactModel(BaseModel):
    id: Optional[int]
    name: str
    contactType: str
    contactRadius: float
    springConstant: float


class Interaction(BaseModel):
    id: Optional[int]
    firstBlockId: int
    secondBlockId: int
    contactModelId: int


class Contact(BaseModel):
    enabled: bool
    searchRadius: float
    searchFrequency: int
    contactModels: Union[List[ContactModel], None]
    interactions: Union[List[Interaction], None]


class BoundaryCondition(BaseModel):
    conditionsId: Optional[int]
    name: str
    nodeSet: Optional[str] = None
    boundarytype: str
    blockId: Optional[int] = None
    coordinate: str
    value: str


class NodeSet(BaseModel):
    nodeSetId: Optional[int]
    file: str


class BoundaryConditions(BaseModel):
    conditions: List[BoundaryCondition]
    nodeSets: Optional[List[NodeSet]]


class BondFilters(BaseModel):
    id: Optional[int]
    name: str
    type: str
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
    id: Optional[int]
    computeClass: str
    name: str
    variable: str
    calculationType: Optional[str] = None
    blockName: Optional[str] = None
    xValue: Optional[float] = None
    yValue: Optional[float] = None
    zValue: Optional[float] = None


class Output(BaseModel):
    outputsId: Optional[int]
    name: str
    selectedOutputs: Optional[List[str]] = None

    Write_After_Damage: Optional[bool] = None
    Frequency: int
    InitStep: int


class Newton(BaseModel):
    jacobianOperator: str = "Matrix-Free"
    preconditioner: str = "None"


class Verlet(BaseModel):
    safetyFactor: float = 0.95
    numericalDamping: float = 0.000005
    outputFrequency: int = 1000


class Adapt(BaseModel):
    stableStepDifference: int = 4
    maximumBondDifference: int = 10
    stableBondDifference: int = 4


class FileType(str, Enum):
    YAML = "yaml"
    XML = "xml"


class Solver(BaseModel):
    dispEnabled: bool = True
    verbose: bool
    initialTime: float
    finalTime: float
    fixedDt: Optional[float] = None
    solvertype: str
    safetyFactor: float
    numericalDamping: float
    peridgimPreconditioner: Optional[str] = None
    nonlinearSolver: Optional[str] = None
    numberOfLoadSteps: Optional[int] = None
    maxSolverIterations: Optional[int] = None
    relativeTolerance: Optional[float] = None
    maxAgeOfPrec: Optional[int] = None
    directionMethod: Optional[str] = None
    newton: Optional[Newton] = None
    lineSearchMethod: Optional[str] = None
    verletSwitch: Optional[bool] = None
    verlet: Optional[Verlet] = None
    stopAfterDamageInitation: Optional[bool] = None
    endStepAfterDamage: Optional[int] = None
    stopBeforeDamageInitation: Optional[bool] = None
    adaptivetimeStepping: Optional[bool] = None
    adapt: Optional[Adapt] = None
    filetype: FileType


class Job(BaseModel):
    cluster: str
    nodes: Optional[int] = 1
    tasks: Optional[int] = 32
    tasksPerNode: Optional[int] = 32
    cpusPerTask: Optional[int] = 1
    multithread: Optional[bool] = False
    time: Optional[str] = None
    account: Optional[int] = None


class RunData(BaseModel):
    job: Job
    materials: List[Material]
    outputs: List[Output]

    class Config:
        schema_extra = {
            "example": {
                "job": {
                    "cluster": "None",
                    "tasks": 1,
                    "time": "00:20:00",
                    "account": "2263032",
                },
                "materials": [
                    {
                        "id": 1,
                        "name": "PMMA",
                        "matType": "Linear Elastic Correspondence",
                        "density": "1.4e5",
                        "bulkModulus": None,
                        "shearModulus": None,
                        "youngsModulus": "2.997e9",
                        "poissonsRatio": 0.3,
                        "tensionSeparation": False,
                        "nonLinear": True,
                        "planeStress": True,
                        "materialSymmetry": "Isotropic",
                        "stabilizationType": "Global Stiffness",
                        "thickness": "0.01",
                        "hourglassCoefficient": 1,
                        "actualHorizon": None,
                        "yieldStress": None,
                        "Parameter": [
                            {"name": "C11", "value": None},
                            {"name": "C12", "value": None},
                            {"name": "C13", "value": None},
                            {"name": "C14", "value": None},
                            {"name": "C15", "value": None},
                            {"name": "C16", "value": None},
                            {"name": "C22", "value": None},
                            {"name": "C23", "value": None},
                            {"name": "C24", "value": None},
                            {"name": "C25", "value": None},
                            {"name": "C26", "value": None},
                            {"name": "C33", "value": None},
                            {"name": "C34", "value": None},
                            {"name": "C35", "value": None},
                            {"name": "C36", "value": None},
                            {"name": "C44", "value": None},
                            {"name": "C45", "value": None},
                            {"name": "C46", "value": None},
                            {"name": "C55", "value": None},
                            {"name": "C56", "value": None},
                            {"name": "C66", "value": None},
                        ],
                        "properties": [{"id": 1, "name": "Prop_1", "value": None}],
                    },
                    {
                        "id": 2,
                        "name": "PMMAElast",
                        "matType": "Linear Elastic Correspondence",
                        "density": "1.4e5",
                        "bulkModulus": None,
                        "shearModulus": None,
                        "youngsModulus": "2.997e9",
                        "poissonsRatio": "0.3",
                        "tensionSeparation": False,
                        "nonLinear": True,
                        "planeStress": True,
                        "materialSymmetry": "Isotropic",
                        "stabilizationType": "Global Stiffness",
                        "thickness": "0.01",
                        "hourglassCoefficient": "1",
                        "actualHorizon": None,
                        "yieldStress": None,
                        "Parameter": [
                            {"name": "C11", "value": None},
                            {"name": "C12", "value": None},
                            {"name": "C13", "value": None},
                            {"name": "C14", "value": None},
                            {"name": "C15", "value": None},
                            {"name": "C16", "value": None},
                            {"name": "C22", "value": None},
                            {"name": "C23", "value": None},
                            {"name": "C24", "value": None},
                            {"name": "C25", "value": None},
                            {"name": "C26", "value": None},
                            {"name": "C33", "value": None},
                            {"name": "C34", "value": None},
                            {"name": "C35", "value": None},
                            {"name": "C36", "value": None},
                            {"name": "C44", "value": None},
                            {"name": "C45", "value": None},
                            {"name": "C46", "value": None},
                            {"name": "C55", "value": None},
                            {"name": "C56", "value": None},
                            {"name": "C66", "value": None},
                        ],
                        "properties": [{"id": 1, "name": "Prop_1", "value": None}],
                    },
                ],
                "outputs": [
                    {
                        "id": 1,
                        "name": "Output1",
                        "Displacement": True,
                        "Force": True,
                        "Damage": True,
                        "Partial_Stress": True,
                        "Number_Of_Neighbors": False,
                        "Frequency": "100",
                        "InitStep": 0,
                    }
                ],
            }
        }


default_model = {
    "model": {
        "modelNameSelected": "Dogbone",
        "modelFolderName": "Default",
        "ownModel": False,
        "translated": False,
        "length": 13.0,
        "width": 0.1,
        "height": 2.0,
        "height2": 1.0,
        "structured": True,
        "discretization": 21,
        "horizon": 1.0,
        "twoDimensional": True,
        "rotatedAngles": False,
        "angles": [0, 0],
    },
    "materials": [
        {
            "id": 1,
            "name": "PMMA",
            "matType": "Linear Elastic Correspondence",
            "density": "1.4e5",
            "bulkModulus": None,
            "shearModulus": None,
            "youngsModulus": "2.997e9",
            "poissonsRatio": 0.3,
            "tensionSeparation": False,
            "nonLinear": True,
            "planeStress": True,
            "materialSymmetry": "Isotropic",
            "stabilizationType": "Global Stiffness",
            "thickness": "0.01",
            "hourglassCoefficient": 1,
            "actualHorizon": None,
            "yieldStress": None,
            "Parameter": [
                {"name": "C11", "value": None},
                {"name": "C12", "value": None},
                {"name": "C13", "value": None},
                {"name": "C14", "value": None},
                {"name": "C15", "value": None},
                {"name": "C16", "value": None},
                {"name": "C22", "value": None},
                {"name": "C23", "value": None},
                {"name": "C24", "value": None},
                {"name": "C25", "value": None},
                {"name": "C26", "value": None},
                {"name": "C33", "value": None},
                {"name": "C34", "value": None},
                {"name": "C35", "value": None},
                {"name": "C36", "value": None},
                {"name": "C44", "value": None},
                {"name": "C45", "value": None},
                {"name": "C46", "value": None},
                {"name": "C55", "value": None},
                {"name": "C56", "value": None},
                {"name": "C66", "value": None},
            ],
            "properties": [{"id": 1, "name": "Prop_1", "value": None}],
        },
        {
            "id": 2,
            "name": "PMMAElast",
            "matType": "Linear Elastic Correspondence",
            "density": "1.4e5",
            "bulkModulus": None,
            "shearModulus": None,
            "youngsModulus": "2.997e9",
            "poissonsRatio": "0.3",
            "tensionSeparation": False,
            "nonLinear": True,
            "planeStress": True,
            "materialSymmetry": "Isotropic",
            "stabilizationType": "Global Stiffness",
            "thickness": "0.01",
            "hourglassCoefficient": "1",
            "actualHorizon": None,
            "yieldStress": None,
            "Parameter": [
                {"name": "C11", "value": None},
                {"name": "C12", "value": None},
                {"name": "C13", "value": None},
                {"name": "C14", "value": None},
                {"name": "C15", "value": None},
                {"name": "C16", "value": None},
                {"name": "C22", "value": None},
                {"name": "C23", "value": None},
                {"name": "C24", "value": None},
                {"name": "C25", "value": None},
                {"name": "C26", "value": None},
                {"name": "C33", "value": None},
                {"name": "C34", "value": None},
                {"name": "C35", "value": None},
                {"name": "C36", "value": None},
                {"name": "C44", "value": None},
                {"name": "C45", "value": None},
                {"name": "C46", "value": None},
                {"name": "C55", "value": None},
                {"name": "C56", "value": None},
                {"name": "C66", "value": None},
            ],
            "properties": [{"id": 1, "name": "Prop_1", "value": None}],
        },
    ],
    "damages": [
        {
            "id": 1,
            "name": "PMMADamage",
            "damageModel": "Critical Energy Correspondence",
            "criticalStretch": 10,
            "criticalEnergy": "10.1",
            "interblockdamageEnergy": "0.01",
            "planeStress": True,
            "onlyTension": False,
            "detachedNodesCheck": True,
            "thickness": 10,
            "hourglassCoefficient": 1,
            "stabilizationType": "Global Stiffness",
            "criticalEnergyCalc": {
                "calculateCriticalEnergy": False,
                "k1c": None,
                "youngsModulus": None,
            },
        }
    ],
    "blocks": [
        {
            "id": 1,
            "name": "block_1",
            "material": "PMMAElast",
            "damageModel": "",
            "show": True,
        },
        {
            "id": 2,
            "name": "block_2",
            "material": "PMMAElast",
            "damageModel": "",
            "show": True,
        },
        {
            "id": 3,
            "name": "block_3",
            "material": "PMMA",
            "damageModel": "",
            "show": True,
        },
        {
            "id": 4,
            "name": "block_4",
            "material": "PMMAElast",
            "damageModel": "",
            "show": True,
        },
        {
            "id": 5,
            "name": "block_5",
            "material": "PMMAElast",
            "damageModel": "",
            "show": True,
        },
    ],
    "boundaryConditions": {
        "conditions": [
            {
                "conditionsId": 1,
                "name": "BC_1",
                "nodeSet": 1,
                "boundarytype": "Prescribed Displacement",
                "blockId": 1,
                "coordinate": "x",
                "value": "0*t",
            },
            {
                "conditionsId": 2,
                "name": "BC_2",
                "nodeSet": 2,
                "boundarytype": "Prescribed Displacement",
                "blockId": 5,
                "coordinate": "x",
                "value": "0.05*t",
            },
        ],
        "nodeSets": [
            {"nodeSetId": 1, "file": "ns_Dogbone_1.txt"},
            {"nodeSetId": 2, "file": "ns_Dogbone_2.txt"},
        ],
    },
    "bondFilters": [],
    "computes": [
        {
            "id": 1,
            "computeClass": "Block_Data",
            "name": "External_Displacement",
            "variable": "Displacement",
            "calculationType": "Maximum",
            "blockName": "block_5",
        },
        {
            "id": 2,
            "computeClass": "Block_Data",
            "name": "External_Force",
            "variable": "Force",
            "calculationType": "Sum",
            "blockName": "block_5",
        },
    ],
    "outputs": [
        {
            "id": 1,
            "name": "Output1",
            "selectedOutputs": [
                "Displacement",
                "Force",
                "Damage",
                "Velocity",
                "Partial_Stress",
            ],
            "Frequency": "100",
            "InitStep": 0,
        }
    ],
    "solver": {
        "verbose": False,
        "initialTime": 0,
        "finalTime": "0.0075",
        "solvertype": "Verlet",
        "safetyFactor": "0.9",
        "numericalDamping": "0.0005",
        "peridgimPreconditioner": "None",
        "nonlinearSolver": "Line Search Based",
        "numberOfLoadSteps": 100,
        "maxSolverIterations": 50,
        "relativeTolerance": 1e-8,
        "maxAgeOfPrec": 100,
        "directionMethod": "Newton",
        "newton": {"jacobianOperator": "Matrix-Free", "preconditioner": "None"},
        "lineSearchMethod": "Polynomial",
        "verletSwitch": True,
        "verlet": {
            "safetyFactor": 0.95,
            "numericalDamping": 0.000005,
            "outputFrequency": 7500,
        },
        "stopAfterDamageInitation": False,
        "stopBeforeDamageInitation": False,
        "adaptivetimeStepping": False,
        "adapt": {
            "stableStepDifference": 4,
            "maximumBondDifference": 4,
            "stableBondDifference": 1,
        },
        "filetype": "yaml",
    },
    "job": {
        "cluster": "None",
        "nodes": 1,
        "tasks": 32,
        "tasksPerNode": 32,
        "cpusPerTask": 1,
        "multithread": False,
        "time": "00:20:00",
        "account": 2263032,
    },
}


class ModelData(BaseModel):
    model: Model
    materials: List[Material]
    additive: Optional[Additive]
    damages: Optional[List[Damage]]
    blocks: List[Block]
    contact: Optional[Contact]
    boundaryConditions: BoundaryConditions
    bondFilters: Optional[List[BondFilters]]
    computes: Optional[List[Compute]]
    outputs: List[Output]
    solver: Solver
    job: Job

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    class Config:
        schema_extra = {"example": default_model}


class SmetanaData(BaseModel):
    dx_value: List[float]
    angleList: List[float]
    damage: Optional[List[Damage]]
    contact: Optional[Contact]
    boundary_condition: BoundaryConditions
    compute: Optional[List[Compute]]
    output: List[Output]
    solver: Solver


class ResponseModel(BaseModel):
    data: Any
    code = 200
    message: str
