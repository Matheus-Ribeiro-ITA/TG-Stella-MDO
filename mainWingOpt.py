from _collections import OrderedDict

import os
import pickle
import avl
from aircraftInfo import AircraftInfo
import MDO
from MDO import aerodynamics as aero
import numpy as np

pathSave = "resultsWing120"

def _saveAll(Xstates0):
    result, aircraftInfo = objectiveFunction(Xstates0)

    with open(f'{pathSave}/aircraft{i}.pickle', 'wb') as file:
        pickle.dump(aircraftInfo, file)
        file.close()
    # with open(f"{pathSave}/results{i}.json", "wt") as file:
    #     file.write(json.dumps(result, indent=4))
    #     file.close()


# ----------------------------------------------
# Debug bool
DEBUG = False
PLOT = False

verticalType = "v"

wingAirfoil = "ls417mod_cruise"
stabAirfoil = "naca0012_cruise"

# Xstates0 = [6, 0.5, 0.8, 0.7, 0.6,
#             1.5, 0.5, 0.5, 2,
#             0.8, 0.375, 0.375]

Xstates0 = [6, 0.7, 0.6, 0.5, 0.4,
            1.5, 0.5, 0.5, 2,
            0.8, 0.375, 0.375]

cgCalc = 0.25

allList = os.listdir(os.path.join(os.getcwd(), pathSave))
pickleList = [name for name in allList if ".pickle" in name]
jsonList = [name for name in allList if ".json" in name]

i = len(pickleList)
print("Aircraft: ", i)

def objectiveFunction(Xstates):
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

    verticalSpan = Xstates[9]  # Remember that is H vertical
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
                "airfoil": MDO.airfoils.AirfoilData(wingAirfoil)
            },
            "middle": {
                "chord": wingSecChord,
                "b": wingSecPosition,
                "sweepLE": np.arctan((wingRootChord - wingSecChord) / 4 / wingSecPosition),
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData(wingAirfoil)
            },
            "tip": {
                "chord": wingTipChord,
                "b": wingPosSec,
                "sweepLE": np.arctan((wingSecChord - wingTipChord) / 4 / wingPosSec),
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData(wingAirfoil)
            },
        }),
        "horizontal": OrderedDict({
            "root": {
                "chord": horizontalRootChord,
                "aoa": 0,
                "x": horizontalXPosition,
                "y": 0,
                "z": 0.5,
                "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
            },
            "tip": {
                "chord": horizontalTipChord,
                "b": horizontalSpan / 2,
                "sweepLE": np.arctan((horizontalRootChord - horizontalTipChord) / 4 / horizontalSpan / 2),
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
            }
        }),
        "vertical": OrderedDict({
            "root": {
                "chord": verticalRootChord,
                "aoa": 0,
                "x": horizontalXPosition,
                "y": 0,
                "z": 0.5,
                "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
            },
            "tip": {
                "chord": verticalTipChord,
                "b": verticalSpan,
                "sweepLE": np.arctan((verticalRootChord - verticalTipChord) / 4 / verticalSpan / 2),
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
            }
        }),
        "endPlate": OrderedDict({
            "root": {
                "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
            },
            "tip": {
                "chord": 0,
                "b": 0.4,
                "sweepLE": 0,
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
            }
        })
    }

    # ----------------------------------------------
    # Control Surfaces definition
    controlVariables = {
        # "aileron": {
        #     "spanStartPercentage": 0.8,
        #     "cHinge": 0.8,
        #     "gain": 1,
        #     "duplicateSign": 1
        # },
        "elevator": {
            "spanStartPercentage": 0.2,
            "cHinge": 0.5,
            "gain": 1,
            "duplicateSign": 1
        },
        # "rudder": {
        #     "spanStartPercentage": 0.4,
        #     "cHinge": 0.8,
        #     "gain": 1,
        #     "duplicateSign": 1
        # },
        "flap": {
            "spanStartPercentage": 0.0,
            "cHinge": 0.7,  # From Leading Edge
            "gain": 1,
            "duplicateSign": 1
        },
    }

    # ----------------------------------------------
    # Avl Cases to analyse
    mission = {
        "cruise": {
            "altitude": 1500,
            "vCruise": 120 / 3.6,
        },  # Cruise trimmed (W/L = 1), change
        "polar": {
            "cLPoints": [0.44, 0.8, 1.2]
        },
        "takeOffRun": {
            'alpha': 3,
            'flap': 0,
        }
}

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
    aircraftInfo.cgCalc = cgCalc
    # ----------------------------------------------
    # Avl Geo
    aircraftAvl = avl.avlGeoBuild(stateVariables, controlVariables, verticalType=verticalType)

    # ----------------------------------------------
    # Avl cases

    cases = avl.avlRunBuild(mission, aircraftInfo)

    # ----------------------------------------------
    # Avl Run
    results = avl.avlRun(aircraftAvl, cases)

    # ----------------------------------------------
    # Polar
    [aircraftInfo.cD0, aircraftInfo.cD1,
     aircraftInfo.k, aircraftInfo.dataPolar] = aero.polar(results, aircraftInfo)
    aero.stall(results, aircraftInfo)

    # ------------------ Neutral Point ---------------------------------
    MDO.stability.getNeutralPoint(results, aircraftInfo)

    # ------------------ Take Off ---------------------------------
    [aircraftInfo.thrustV0, aircraftInfo.thrustV1,
     aircraftInfo.thrustV2] = MDO.performance.dynamicThrustCurve(
        engineInfo, method="actuatorDisk")

    # aircraftInfo.cLRun = 0.40
    aircraftInfo.cD0Run = aircraftInfo.cD0
    aircraftInfo.cD1Run = aircraftInfo.cD1
    aircraftInfo.kRun = aircraftInfo.k

    aircraftInfo.cDCruise = results["trimmed"]["Totals"]["CDtot"]
    aircraftInfo.dragCruise = 1/2*1.2*aircraftInfo.cDCruise*mission['cruise']['vCruise']**2*aircraftInfo.wingArea
    aircraftInfo.alphaRun = results["trimmed"]["Totals"]["Alpha"]
    mission['takeOffRun']["alpha"] = aircraftInfo.alphaRun

    [aircraftInfo.runway, aircraftInfo.speedTakeOff] = MDO.performance.takeOffRoll(aircraftInfo, dt=0.01, nsteps=15000)

    return results, aircraftInfo

nSteps = 20
# indexState = 2
totalStepes = nSteps**2 + i

Xstates = Xstates0.copy()
Xstates[1] = 0.5

for root in np.linspace(0.5, 0.7, nSteps):
    for tip in np.linspace(0.2, root, nSteps):
        Xstates[2] = root
        Xstates[3] = (root + tip)/2
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




