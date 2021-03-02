import time
from _collections import OrderedDict

from aircraftInfo import AircraftInfo

startTime = time.time()

# Declarations
stateVariables = {
    "wing": OrderedDict({
        "root": {
            "chord": 0.9,
            "aoa": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "airfoil": "2414"
        },
        "middle": {
            "chord": 0.7,
            "b": 3.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "2414"
        },
        "tip": {
            "chord": 0.675,
            "b": 1.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "2414"
        },
    }),
    "horizontal": OrderedDict({
        "root": {
            "chord": 0.675,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0,
            "airfoil": "0012"
        },
        "tip": {
            "chord": 0.675,
            "b": 1.85,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "0012"
        }
    }),
    "vertical": OrderedDict({
        "root": {
            "chord": 0.5,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0.5,
            "airfoil": "0012"
        },
        "tip": {
            "chord": 0.5,
            "b": 0.8,
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
    "cruise": {
        "altitude": 1000,
        "vCruise": 120/3.6,
    }, # Cruise trimmed (W/L = 1), change
    "roll": {
        "altitude": 1000,
        "vCruise": 20,
        "rollRate": 1,
    },  # save for later
    "dive": {
        "altitude": 1000,
        "vDive": 30,
        "loadFactor": 1.5
    },  # Change to Clmax
    "Clmax":{

    },
    "polar": {
        "cLPoints": [-0.4, 0, 0.4]
    }
} # 6 trimagem

engineFC = {
    "fuelFrac": {
        'engineValue': 0.998,
        'taxi': 0.998,
        'takeOff': 0.998,
        'climb': 0.995,
        "descent": 0.990,
        "landing": 0.992
    },
    "cCruise": 0.03794037940379404,  # 0.068 standard value
    "consumptionMaxLperH": 12,  # liters/hour
    "consumptionCruiseLperH": 7,  # liters/hour
    "fuelDensityGperL": 0.8,  # gram/liter
}  # Check figure 2.1 for correct value. Slide 248

# Calculation

aircraftInfo = AircraftInfo(stateVariables, controlVariables)

print("Weight is:")
print(aircraftInfo.weightEmpty)
