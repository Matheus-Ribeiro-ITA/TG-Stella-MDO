from _collections import OrderedDict

import os
import pickle
import json
import avl
from aircraftInfo import AircraftInfo
import MDO
from MDO import aerodynamics as aero
import numpy as np

pathSave = "resultsUntrimmed"

def _saveAll(Xstates0):
    result, aircraftInfo = objectiveFunction(Xstates0)

    with open(f'{pathSave}/aircraft{i}.pickle', 'wb') as file:
        pickle.dump(aircraftInfo, file)
        file.close()
    with open(f"{pathSave}/results{i}.json", "wt") as file:
        file.write(json.dumps(result, indent=4))
        file.close()


# ----------------------------------------------
# Debug bool
DEBUG = False
PLOT = False
# Xstates0 = [6, 0.5, 0.8, 0.7, 0.6,
#             1.5, 0.5, 0.5, 2,
#             0.8, 0.375, 0.375]

Xstates0 = [7.8, 0.7, 0.78, 0.5, 0.35,
            1.5, 0.5, 0.5, 2,
            0.8, 0.375, 0.375]

# bounds = Bounds([3/10, 0.1, 0.1, 0.1, 0.1,
#                  0.2/5, 0.1, 0.1, 0.5/5,
#                  0.2/5, 0.1, 0.1],
#                 [10/10, 0.95, 1.5, 1.5, 1.0,
#                  4 / 5, 1.5, 1.5, 5 / 5,
#                  4 / 5, 1.5, 1.5])
allList = os.listdir(os.path.join(os.getcwd(), pathSave))
pickleList = [name for name in allList if ".pickle" in name]
jsonList = [name for name in allList if ".json" in name]

if len(pickleList) == len(jsonList):
    i = len(pickleList)
    print("Aircraft: ", i)

def objectiveFunction(Xstates):
    verticalType = "h"

    # Variables Optimizer
    wingSpan = Xstates[0]
    wingSecPercentage = Xstates[1]
    wingRootChord = Xstates[2]
    wingSecChord = Xstates[3]
    wingTipChord = Xstates[4]

    horizontalSpan = Xstates[5]
    horizontalRootChord = Xstates[6]
    horizontalTipChord = Xstates[7]
    horizontalXPosition = Xstates[8]

    verticalSpan = Xstates[9] # Remember that is H vertical
    verticalRootChord = Xstates[10]
    verticalTipChord = Xstates[11]

    wingSecPosition = wingSpan / 2 * wingSecPercentage
    wingPosSec = wingSpan / 2 * (1 - wingSecPercentage)
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
                "sweepLE": np.arctan((wingRootChord - wingSecChord) / 4 / wingSecPosition),
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData("goe498")
            },
            "tip": {
                "chord": wingTipChord,
                "b": wingPosSec,
                "sweepLE": np.arctan((wingSecChord - wingTipChord) / 4 / wingPosSec),
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
                "b": horizontalSpan / 2,
                "sweepLE": np.arctan((horizontalRootChord - horizontalTipChord) / 4 / horizontalSpan / 2),
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData("n0012")
            }
        }),
        "vertical": OrderedDict({
            "root": {
                "chord": verticalRootChord,
                "aoa": 0,
                "x": horizontalXPosition,
                "y": 0.75,
                "z": 0.5,
                "airfoil": MDO.airfoils.AirfoilData("n0012")
            },
            "tip": {
                "chord": verticalTipChord,
                "b": verticalSpan / 2,
                "sweepLE": np.arctan((verticalRootChord - verticalTipChord) / 4 / verticalSpan / 2),
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
        "untrimmed_polar": {
            "cLPoints": [0.2, 0.44, 0.8]
        }
    }  # 6 trimagem

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
    # Polar
    [aircraftInfo.cD0, aircraftInfo.cD1,
     aircraftInfo.k, aircraftInfo.dataPolar] = aero.polar(results, aircraftInfo)
    aero.stall(results, aircraftInfo)

    # ------------------ Take Off ---------------------------------
    [aircraftInfo.thrustV0, aircraftInfo.thrustV1,
     aircraftInfo.thrustV2] = MDO.performance.dynamicThrustCurve(
        engineInfo, method="actuatorDisk")

    # aircraftInfo.cLRun = 0.40
    aircraftInfo.cD0Run = aircraftInfo.cD0
    aircraftInfo.cD1Run = aircraftInfo.cD1
    aircraftInfo.kRun = aircraftInfo.k

    [aircraftInfo.runway, aircraftInfo.speedTakeOff] = MDO.performance.takeOffRoll(aircraftInfo, dt=0.01, nsteps=15000)

    return results, aircraftInfo


lowPer = 0.95
upperPer = 1.3
nSteps = 2
# indexState = 2
totalStepes = nSteps**5 + i


# indexState = 3
# for x in np.linspace(Xstates0[indexState]*lowPer, Xstates0[indexState]*upperPer, nSteps):
#     Xstates0[indexState] = x
#     _saveAll(Xstates0)
#     i += 1


Xstates = Xstates0.copy()
for wingSpan in np.linspace(Xstates0[0]*lowPer, Xstates0[0]*upperPer, nSteps):
    for secPer in np.linspace(Xstates0[1] * lowPer, Xstates0[1] * upperPer, nSteps):
        for root in np.linspace(Xstates0[2] * lowPer, Xstates0[2] * upperPer, nSteps):
            for middle in np.linspace(Xstates0[3] * lowPer, Xstates0[3] * upperPer, nSteps):
                for tip in np.linspace(Xstates0[4] * lowPer, Xstates0[4] * upperPer, nSteps):
                    Xstates[0] = wingSpan
                    Xstates[1] = secPer
                    Xstates[2] = root
                    Xstates[3] = middle
                    Xstates[4] = tip
                    _saveAll(Xstates)
                    i += 1
                    print(f" {i} of {totalStepes}")

# indexState = 2
# for x in np.linspace(Xstates0[indexState]*lowPer, Xstates0[indexState]*upperPer, nSteps):  # Wingspan
#     indexState = 2
#     Xstates0[indexState] = x
#     # _saveAll(Xstates0)
#     # i += 1
#     indexState = 3
#     for x in np.linspace(Xstates0[indexState]*lowPer, Xstates0[indexState]*upperPer, nSteps):  # Wingspan
#         indexState = 3
#         Xstates0[indexState] = x
#         # _saveAll(Xstates0)
#         # i += 1
#
#         indexState = 4
#         for x in np.linspace(Xstates0[indexState] * lowPer, Xstates0[indexState] * upperPer, nSteps):  # Wingspan
#             indexState = 4
#             Xstates0[indexState] = x
#             # _saveAll(Xstates0)
#             # i += 1
#
#             indexState = 0
#             for x in np.linspace(Xstates0[indexState] * lowPer, Xstates0[indexState] * upperPer, nSteps):  # Wingspan
#                 indexState = 0
#                 Xstates0[indexState] = x
#                 # _saveAll(Xstates0)
#                 # i += 1
#
#                 indexState = 1
#                 for x in np.linspace(Xstates0[indexState] * lowPer, Xstates0[indexState] * upperPer,
#                                      nSteps):
#                     indexState = 1
#                     Xstates0[indexState] = x
#                     _saveAll(Xstates0)
#                     i += 1




