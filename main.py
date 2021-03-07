import time
from _collections import OrderedDict

import json
import avl
from aircraftInfo import AircraftInfo
import MDO
from MDO import aerodynamics as aero
import numpy as np

startTime = time.time()
# ----------------------------------------------
# Debug bool
DEBUG = False
PLOT = False

# ----------------------------------------------
# Vertical Stabilizer tips
# Options: "conventional", "h".
verticalType = "h"

# Variables Optimizer
wingSpan = 3.75
wingSecPercentage = 0.5
wingRootChord = 0.8
wingSecChord = 0.7
wingTipChord = 0.6

horizontalSpan = 1.5
horizontalRootChord = 0.5
horizontalTipChord = 0.5
horizontalXPosition = 2

verticalSpan = 0.8  # Remember that is H vertical
verticalRootChord = 0.375
verticalTipChord = 0.375
verticalXPosition = 2

wingSecPosition = wingSpan/2*wingSecPercentage
wingPosSec = wingSpan/2*(1-wingSecPercentage)


# ----------------------------------------------
# Optimizer state Variables
stateVariables = {
    "wing": OrderedDict({
        "root": {
            "chord": wingRootChord,
            "aoa": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "airfoil": MDO.airfoils.AirfoilData("goe498")
        },
        "middle": {
            "chord": wingSecChord,
            "b": wingSecPosition,
            "sweepLE": np.arctan((wingRootChord-wingSecChord)/4/wingSecPosition),
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("goe498")
        },
        "tip": {
            "chord": wingTipChord,
            "b": wingPosSec,
            "sweepLE": np.arctan((wingSecChord-wingTipChord)/4/wingPosSec),
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("goe498")
        },
    }),
    "horizontal": OrderedDict({
        "root": {
            "chord": horizontalRootChord,
            "aoa": 0,
            "x": horizontalXPosition,
            "y": 0,
            "z": 0.5,
            "airfoil": MDO.airfoils.AirfoilData("n0012")
        },
        "tip": {
            "chord": horizontalTipChord,
            "b": horizontalSpan/2,
            "sweepLE": np.arctan((horizontalRootChord-horizontalTipChord)/4/horizontalSpan/2),
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("n0012")
        }
    }),
    "vertical": OrderedDict({
        "root": {
            "chord": verticalRootChord,
            "aoa": 0,
            "x": 2,
            "y": 0.75,
            "z": 0.5,
            "airfoil": MDO.airfoils.AirfoilData("n0012")
        },
        "tip": {
            "chord": verticalTipChord,
            "b": verticalSpan/2,
            "sweepLE": np.arctan((verticalRootChord-verticalTipChord)/4/verticalSpan/2),
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
        "cLPoints": [0.2, 0.44, 0.8]
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

engineInfo = {
    "name": "DLE 170",
    "maxPowerHp": 17.5,
    "maxThrust": 343,
    "propellerInches": [30, 12],
    "RPM": 7500
}
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
# Neutral Point
MDO.stability.getNeutralPoint(results, aircraftInfo)
print("------------------------------")
print("Neutral Point: ", aircraftInfo.xNeutralPoint)
print(f"EM: {round(aircraftInfo.staticMargin, 2)} %")


# ----------------------------------------------
# Deflections Check
deflections = MDO.checks.Deflections(results)


print("Deflections:", deflections.cruise)

# ----------------------------------------------
# Polar
[aircraftInfo.cD0, aircraftInfo.cD1, aircraftInfo.k, aircraftInfo.dataPolar] = aero.polar(results, aircraftInfo)
print("Polar:", aircraftInfo.cD0, aircraftInfo.cD1, aircraftInfo.k)

if PLOT:
    aero.plotPolar(aircraftInfo)

# ----------------------------------------------
# Stall
aero.stall(results, aircraftInfo)
print("Wing Stall: ", aircraftInfo.alphaStallWing, " at ", round(2*aircraftInfo.stallPositionWing/aircraftInfo.wingSpan,2), "%")
# print("Horizontal Stall: ", aircraftInfo.alphaStallHorizontal, " at ", aircraftInfo.stallPositionHorizontal, "m")

if PLOT:
    aero.plotStall(aircraftInfo)
    aero.plotliftDistribution(aircraftInfo)

# Range ----------------------------------------------
rangeCruise = aero.rangeCruise(engineFC, mission, aircraftInfo)
print(f"Range: {rangeCruise}")

# ------------------ Take Off ---------------------------------
[aircraftInfo.thrustV0, aircraftInfo.thrustV1, aircraftInfo.thrustV2] = MDO.performance.dynamicThrustCurve(engineInfo, method="actuatorDisk")

aircraftInfo.cLRun = 0.44
aircraftInfo.cD0Run = aircraftInfo.cD0
aircraftInfo.cD1Run = aircraftInfo.cD1
aircraftInfo.kRun = aircraftInfo.k

[runway, speedTakeOff] = MDO.performance.takeOffRoll(aircraftInfo)
print("------------------------------")
print(f"Runway Length: {runway} m")
print(f"Take Off Speed: {speedTakeOff} m/s")
# ----------------------------------------------
# Process time
print("------------------------------")
print(f"Process Time: {(time.time() - startTime)} s")
