
import json
import time
from _collections import OrderedDict

import avl
from aircraftInfo import AircraftInfo
import checks
import aerodynamics as aero

startTime = time.time()

# Declarations
stateVariables = {
    "wing": OrderedDict({
        "root": {
            "chord": 0.3,
            "aoa": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "airfoil": "2414"
        },
        "middle": {
            "chord": 0.3,
            "b": 1,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "2414"
        },
        "tip": {
            "chord": 0.1,
            "b": 0.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "2414"
        },
    }),
    "horizontal": OrderedDict({
        "root": {
            "chord": 0.2,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0,
            "airfoil": "0012"
        },
        "tip": {
            "chord": 0.2,
            "b": 0.4,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "0012"
        }
    }),
    "vertical": OrderedDict({
        "root": {
            "chord": 0.2,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0.5,
            "airfoil": "0012"
        },
        "tip": {
            "chord": 0.2,
            "b": 0.4,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "0012"
        }
    })
}

controlVariables = {
    "aileron": {
        "spanStartPercentage": 0.8,
        "cHinge": 0.8,
        "gain": 1,
        "duplicateSign": 1
    },
    "elevator": {
        "spanStartPercentage": 0.4,
        "cHinge": 0.8,
        "gain": 1,
        "duplicateSign": 1
    },
    "rudder": {
        "spanStartPercentage": 0.4,
        "cHinge": 0.8,
        "gain": 1,
        "duplicateSign": 1
    },
}

mission = {
    "cruize": {
        "altitude": 1000,
        "vCruise": 20,
        "range": 230000
    },
    "roll": {
        "altitude": 1000,
        "vCruise": 20,
        "rollRate": 1,
    },
    "dive": {
        "altitude": 1000,
        "vDive": 30,
        "loadFactor": 1.5
    },
    "polar": {
        "cLPoints": [-0.4, 0, 0.4]
    }
}

engineFC = {
    'engineValue': 0.998,
    'taxi': 0.998,
    'takeOff': 0.998,
    'climb': 0.995,
}  # Check figure 2.1 for correct value. Slide 248

# Calculation

aircraftInfo = AircraftInfo(stateVariables)

aircraftAvl = avl.avlGeoBuild(stateVariables, controlVariables)

cases = avl.avlRunBuild(mission, aircraftInfo)

results = avl.avlRun(aircraftAvl, cases)

# Data View
# with open("avl/results/resultExample.json", "wt") as file:
#     file.write(json.dumps(results, indent=4))

deflections = checks.Deflections(results)
print(deflections.max)

cD0, k = aero.polar(results)
print("Polar:", cD0, k)
print(f"Tempo médio: {(time.time() - startTime)} s")
