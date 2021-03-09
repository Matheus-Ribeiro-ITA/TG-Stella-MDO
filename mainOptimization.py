import time
from _collections import OrderedDict
from scipy.optimize import Bounds, minimize

import json
import avl
from aircraftInfo import AircraftInfo
import MDO
from MDO import aerodynamics as aero
import numpy as np

DEBUG = False
PLOT = False


Xstates0 = [6 / 10, 0.5, 0.8, 0.7, 0.6,
            1.5/5, 0.5, 0.5, 2/5,
            0.8/5, 0.375, 0.375]

bounds = Bounds([3/10, 0.1, 0.1, 0.1, 0.1,
                 0.2/5, 0.1, 0.1, 0.5/5,
                 0.2/5, 0.1, 0.1],
                [10/10, 0.95, 1.5, 1.5, 1.0,
                 4 / 5, 1.5, 1.5, 5 / 5,
                 4 / 5, 1.5, 1.5])

def objectiveFunction(Xstates):
    verticalType = "h"

    # Variables Optimizer
    wingSpan = Xstates[0] * 10
    wingSecPercentage = Xstates[1]
    wingRootChord = Xstates[2]
    wingSecChord = Xstates[3]
    wingTipChord = Xstates[4]

    horizontalSpan = Xstates[5] * 5
    horizontalRootChord = Xstates[6]
    horizontalTipChord = Xstates[7]
    horizontalXPosition = Xstates[8] * 5

    verticalSpan = Xstates[9] * 5  # Remember that is H vertical
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
        "cruise": {
            "altitude": 1000,
            "vCruise": 150 / 3.6,
        },
        "polar": {
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

    # # ----------------------------------------------
    # # Save results
    # if DEBUG:
    #     with open("aircraft/results.json", "w", encoding="utf-8") as file:
    #         json.dump(results, file, indent=4)
    #         file.close()

    # with open("avl/results/resultExample.json", "wt") as file:
    #     file.write(json.dumps(results, indent=4))
    # ----------------------------------------------
    # Neutral Point
    MDO.stability.getNeutralPoint(results, aircraftInfo)

    # ----------------------------------------------
    # Polar
    [aircraftInfo.cD0, aircraftInfo.cD1,
     aircraftInfo.k, aircraftInfo.dataPolar] = aero.polar(results, aircraftInfo)
    aero.stall(results, aircraftInfo)

    # ------------------ Take Off ---------------------------------
    [aircraftInfo.thrustV0, aircraftInfo.thrustV1,
     aircraftInfo.thrustV2] = MDO.performance.dynamicThrustCurve(
        engineInfo, method="actuatorDisk")

    aircraftInfo.cLRun = 0.40
    aircraftInfo.cD0Run = aircraftInfo.cD0
    aircraftInfo.cD1Run = aircraftInfo.cD1
    aircraftInfo.kRun = aircraftInfo.k

    [runway, speedTakeOff] = MDO.performance.takeOffRoll(aircraftInfo, dt=0.01, nsteps=15000)

    return runway

res = minimize(objectiveFunction, Xstates0, method='trust-constr',
               options={'verbose': 1}, bounds=bounds)