# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel


class Valve(BaseModel):
    name: str
    type: str
    label: str
    description: str
    value: Any
    options: Optional[List[str]]


class Valves(BaseModel):
    valves: List[Valve]


class Status(BaseModel):
    created: Optional[bool] = False
    submitted: Optional[bool] = False
    results: Optional[bool] = False


class Model(BaseModel):
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
    radius2: Optional[float] = None
    structured: Optional[bool] = None
    discretization: int
    horizon: Optional[float] = None
    twoDimensional: bool
    rotatedAngles: bool
    angles: List[float]
    amplitudeFactor: Optional[float] = None
    wavelength: Optional[float] = None
    mesh_file: Optional[str] = None


class Jobs(BaseModel):
    id: int
    name: str
    sub_name: str
    cluster: bool
    created: bool
    submitted: bool
    results: bool
    model: Optional[dict] = None


class properties(BaseModel):
    id: Optional[int] = None
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
    id: Optional[int] = None
    name: str
    matType: List[str]
    bulkModulus: Optional[float] = None
    shearModulus: Optional[float] = None
    youngsModulus: Optional[float] = None
    poissonsRatio: Optional[float] = None
    planeStress: bool
    planeStrain: bool
    materialSymmetry: str
    stabilizationType: str
    thickness: float
    hourglassCoefficient: float
    actualHorizon: Optional[float] = None
    yieldStress: Optional[float] = None
    stiffnessMatrix: Optional[StiffnessMatrix] = None
    properties: Union[List[properties], None]
    numStateVars: Optional[int] = None
    computePartialStress: Optional[bool] = None
    useCollocationNodes: Optional[bool] = None


class ThermalModel(BaseModel):
    thermalModelsId: Optional[int] = None
    name: str
    applyThermalFlow: bool
    applyThermalExpansion: bool
    applyHeatTransfer: bool
    thermalType: str
    thermalConductivity: Optional[float] = None
    heatTransferCoefficient: Optional[float] = None
    thermalExpansionCoefficient: Optional[float] = None
    environmentalTemperature: Optional[float] = None
    printTemp: Optional[float] = None
    timeFactor: Optional[float] = None


class Thermal(BaseModel):
    enabled: bool
    thermalModels: Union[List[ThermalModel], None]


class AdditiveModel(BaseModel):
    id: Optional[int] = None
    name: str
    additiveType: str
    printTemp: float
    timeFactor: float


class Additive(BaseModel):
    enabled: bool
    additiveModels: Union[List[AdditiveModel], None]


class InterBlock(BaseModel):
    id: Optional[int] = None
    firstBlockId: int
    secondBlockId: int
    value: float


class CriticalEnergyCalc(BaseModel):
    calculateCriticalEnergy: Optional[bool] = None
    k1c: Optional[float] = None


class Damage(BaseModel):
    id: Optional[int] = None
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
    planeStress: bool
    onlyTension: bool
    detachedNodesCheck: bool
    thickness: float
    hourglassCoefficient: float
    stabilizationType: str


class Block(BaseModel):
    blocksId: int
    name: str
    material: str
    damageModel: Optional[str] = None
    additiveModel: Optional[str] = None
    horizon: Optional[float] = None
    density: Optional[float] = None
    show: Optional[bool] = None


class ContactModel(BaseModel):
    id: Optional[int] = None
    name: str
    contactType: str
    contactRadius: float
    springConstant: float


class Interaction(BaseModel):
    id: Optional[int] = None
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
    conditionsId: Optional[int] = None
    name: str
    nodeSet: Optional[int] = None
    boundarytype: str
    variable: str
    blockId: Optional[int] = None
    coordinate: str
    value: str


class NodeSet(BaseModel):
    nodeSetId: Optional[int] = None
    file: str


class BoundaryConditions(BaseModel):
    conditions: List[BoundaryCondition]
    nodeSets: Optional[List[NodeSet]] = None


class BondFilters(BaseModel):
    id: Optional[int] = None
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
    id: Optional[int] = None
    computeClass: str
    name: str
    variable: str
    calculationType: Optional[str] = None
    blockName: Optional[str] = None
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
    safetyFactor: float = 0.95
    numericalDamping: float = 0.000005
    outputFrequency: int = 1000


class Adapt(BaseModel):
    stableStepDifference: int = 4
    maximumBondDifference: int = 10
    stableBondDifference: int = 4


class Solver(BaseModel):
    matEnabled: bool = True
    damEnabled: bool = True
    dispEnabled: bool = True
    tempEnabled: bool = True
    verbose: bool
    initialTime: float
    finalTime: float
    fixedDt: Optional[float] = None
    solvertype: str
    safetyFactor: float
    numericalDamping: float
    verlet: Optional[Verlet] = None
    stopAfterDamageInitation: Optional[bool] = None
    endStepAfterDamage: Optional[int] = None
    stopAfterCertainDamage: Optional[bool] = None
    maxDamageValue: Optional[float] = None
    stopBeforeDamageInitation: Optional[bool] = None
    adaptivetimeStepping: Optional[bool] = None
    adapt: Optional[Adapt] = None
    calculateCauchy: Optional[bool] = None
    calculateVonMises: Optional[bool] = None
    calculateStrain: Optional[bool] = None


class Job(BaseModel):
    cluster: bool
    sbatch: bool
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
        json_schema_extra = {
            "example": {
                "job": {
                    "cluster": False,
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
                        "youngsModulus": "2.997e9",
                        "poissonsRatio": 0.3,
                        "tensionSeparation": False,
                        "nonLinear": True,
                        "planeStress": True,
                        "materialSymmetry": "Isotropic",
                        "stabilizationType": "Global Stiffness",
                        "thickness": "0.01",
                        "hourglassCoefficient": 1,
                        "properties": [{"id": 1, "name": "Prop_1", "value": None}],
                    },
                    {
                        "id": 2,
                        "name": "PMMAElast",
                        "matType": "Linear Elastic Correspondence",
                        "density": "1.4e5",
                        "youngsModulus": "2.997e9",
                        "poissonsRatio": "0.3",
                        "tensionSeparation": False,
                        "nonLinear": True,
                        "planeStress": True,
                        "materialSymmetry": "Isotropic",
                        "stabilizationType": "Global Stiffness",
                        "thickness": "0.01",
                        "hourglassCoefficient": "1",
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
            "youngsModulus": "2.997e9",
            "poissonsRatio": 0.3,
            "tensionSeparation": False,
            "nonLinear": True,
            "planeStress": True,
            "materialSymmetry": "Isotropic",
            "stabilizationType": "Global Stiffness",
            "thickness": "0.01",
            "hourglassCoefficient": 1,
            "properties": [{"id": 1, "name": "Prop_1", "value": None}],
        },
        {
            "id": 2,
            "name": "PMMAElast",
            "matType": "Linear Elastic Correspondence",
            "density": "1.4e5",
            "youngsModulus": "2.997e9",
            "poissonsRatio": "0.3",
            "tensionSeparation": False,
            "nonLinear": True,
            "planeStress": True,
            "materialSymmetry": "Isotropic",
            "stabilizationType": "Global Stiffness",
            "thickness": "0.01",
            "hourglassCoefficient": "1",
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
            "density": "1.4e5",
            "show": True,
        },
        {
            "id": 2,
            "name": "block_2",
            "material": "PMMAElast",
            "damageModel": "",
            "density": "1.4e5",
            "show": True,
        },
        {
            "id": 3,
            "name": "block_3",
            "material": "PMMA",
            "damageModel": "",
            "density": "1.4e5",
            "show": True,
        },
        {
            "id": 4,
            "name": "block_4",
            "material": "PMMAElast",
            "damageModel": "",
            "density": "1.4e5",
            "show": True,
        },
        {
            "id": 5,
            "name": "block_5",
            "material": "PMMAElast",
            "damageModel": "",
            "density": "1.4e5",
            "show": True,
        },
    ],
    "boundaryConditions": {
        "conditions": [
            {
                "conditionsId": 1,
                "name": "BC_1",
                "nodeSet": 1,
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 1,
                "coordinate": "x",
                "value": "0*t",
            },
            {
                "conditionsId": 2,
                "name": "BC_2",
                "nodeSet": 2,
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
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
        "cluster": False,
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
    additive: Optional[Additive] = None
    damages: Optional[List[Damage]] = None
    blocks: List[Block]
    contact: Optional[Contact] = None
    boundaryConditions: BoundaryConditions
    bondFilters: Optional[List[BondFilters]] = None
    computes: Optional[List[Compute]] = None
    preCalculations: Optional[PreCalculations] = None
    outputs: List[Output]
    solver: Solver
    job: Job

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    class Config:
        json_schema_extra = {"example": default_model}


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
    data: Union[str, bool, dict, int, float, List[str], List[float], List[List[float]], Status, List[Jobs]]
    code: int = 200
    message: str
