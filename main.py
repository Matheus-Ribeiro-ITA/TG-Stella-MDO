import time
from _collections import OrderedDict

import json
import avl
from aircraftInfo import AircraftInfo
import MDO
from MDO import aerodynamics as aero

startTime = time.time()
# ----------------------------------------------
# Debug bool
DEBUG = True
PLOT = False

# ----------------------------------------------
# Vertical Stabilizer tips
# Options: "conventional", "h".
verticalType = "h"

# ----------------------------------------------
# Optimizer state Variables
stateVariables = {
    "wing": OrderedDict({
        "root": {
            "chord": 0.9,
            "aoa": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "airfoil": MDO.airfoils.AirfoilData("goe498")
        },
        "middle": {
            "chord": 0.7,
            "b": 3.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("goe498")
        },
        "tip": {
            "chord": 0.675,
            "b": 1.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("goe498")
        },
    }),
    "horizontal": OrderedDict({
        "root": {
            "chord": 0.675,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0,
            "airfoil": MDO.airfoils.AirfoilData("n0012")
        },
        "tip": {
            "chord": 0.675,
            "b": 1.85,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("n0012")
        }
    }),
    "vertical": OrderedDict({
        "root": {
            "chord": 0.5,
            "aoa": 0,
            "x": 2,
            "y": 1,
            "z": 0.5,
            "airfoil": MDO.airfoils.AirfoilData("n0012")
        },
        "tip": {
            "chord": 0.5,
            "b": 0.8,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("n0012")
        }
    })
}

# ----------------------------------------------
# Control Surfaces definition
controlVariables = {
    "aileron": {
        "spanStartPercentage": 0.8,
        "cHinge": 0.8,
        "gain": 1,
        "duplicateSign": 1
    },
    "elevator": {
        "spanStartPercentage": 0.2,
        "cHinge": 0.5,
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

# ----------------------------------------------
# Avl Cases to analyse
mission = {
    "cruise": {
        "altitude": 1000,
        "vCruise": 150 / 3.6,
    },  # Cruise trimmed (W/L = 1), change
    # "dive": {
    #     "altitude": 1000,
    #     "vDive": 30,
    #     "loadFactor": 1.5
    # },  # Change to Clmax
    "polar": {
        "cLPoints": [-0.4, 0, 0.4]
    }
}  # 6 trimagem

# ----------------------------------------------
# Engine Info
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

# ----------------------------------------------
# Aircraft Info Class
aircraftInfo = AircraftInfo(stateVariables, controlVariables)

# ----------------------------------------------
# Avl Geo
aircraftAvl = avl.avlGeoBuild(stateVariables, controlVariables, verticalType=verticalType)

# ----------------------------------------------
# Avl cases

cases = avl.avlRunBuild(mission, aircraftInfo)

# ----------------------------------------------
# Avl Run
results = avl.avlRun(aircraftAvl, cases, DEBUG=DEBUG)

# ----------------------------------------------
# Save results
if DEBUG:
    with open("aircraft/results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)
        file.close()

# with open("avl/results/resultExample.json", "wt") as file:
#     file.write(json.dumps(results, indent=4))

# ----------------------------------------------
# Deflections Check
deflections = MDO.checks.Deflections(results)

print(aircraftInfo.wingArea)
print(aircraftInfo.wingSpan)
print("------------------------------")
print("Max deflections:")
print(deflections.max)

# ----------------------------------------------
# Polar
aircraftInfo.cD0, aircraftInfo.k = aero.polar(results)
print("Polar:", aircraftInfo.cD0, aircraftInfo.k)

if PLOT:
    aero.plotPolar(aircraftInfo)

# ----------------------------------------------
# Stall
aero.stall(results, aircraftInfo)
print("Wing Stall: ", aircraftInfo.alphaStallWing, " at ", aircraftInfo.stallPositionWing, "m")
print("Horizontal Stall: ", aircraftInfo.alphaStallHorizontal, " at ", aircraftInfo.stallPositionHorizontal, "m")

if PLOT:
    aero.plotStall(aircraftInfo)
    aero.plotliftDistribution(aircraftInfo)

# ----------------------------------------------
# Range
rangeCruise = aero.rangeCruise(engineFC, mission, aircraftInfo)
print(f"Range: {rangeCruise}")

# ----------------------------------------------
# Process time
print("------------------------------")
print(f"Process Time: {(time.time() - startTime)} s")
