from _collections import OrderedDict
from scipy.optimize import Bounds, minimize

import avl
from aircraftInfo import AircraftInfo
import MDO
from MDO import aerodynamics as aero
import numpy as np

DEBUG = False
PLOT = False

verticalType = "v"

wingAirfoil = "ls417mod_cruise"
stabAirfoil = "naca0012_cruise"
cgCalc = 0.25

Xstates0 = np.array([0.67, 0.24, 0.12, 0.12])

bounds = Bounds([0.5, 0.2, 0.1, 0.1],
                [0.7, 0.5, 0.5, 0.5])




def objectiveFunction(Xstates):
    # Variables Optimizer

    wingSpan = 6
    wingSecPercentage = 0.5
    wingRootChord = Xstates[0]
    wingSecChord = (Xstates[0] + Xstates[1])/2
    wingTipChord = Xstates[1]

    endPlateChord = Xstates[2]
    endPlateSpan = Xstates[3]

    horizontalSpan = 1.5
    horizontalRootChord = 0.5
    horizontalTipChord = 0.5
    horizontalXPosition = 2

    verticalSpan = 0.8
    verticalRootChord = 0.375
    verticalTipChord = 0.375

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
                "chord": endPlateChord,
                "b": endPlateSpan,
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
            "cHinge": 0.7,
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
    aircraftInfo.dragCruise = 1 / 2 * 1.2 * aircraftInfo.cDCruise * mission['cruise'][
        'vCruise'] ** 2 * aircraftInfo.wingArea
    aircraftInfo.alphaRun = results["trimmed"]["Totals"]["Alpha"]
    mission['takeOffRun']["alpha"] = aircraftInfo.alphaRun

    [aircraftInfo.runway, aircraftInfo.speedTakeOff] = MDO.performance.takeOffRoll(aircraftInfo, dt=0.01, nsteps=15000)

    return aircraftInfo.dragCruise/100


def callbackfun(Xstates, *_):
    global Nfeval, Xstates_history, fb_history, outputs_history, time_history
    dragCruise = objectiveFunction(Xstates)
    print('{0:4d} | {1: 3.3f} {2:3.3f} {3:3.3f} {4:3.3f} {5:3.3f} |'.format(Nfeval,
                                                                          dragCruise,
                                                                          Xstates[0],
                                                                          Xstates[1],
                                                                          Xstates[2],
                                                                          Xstates[3]))

    # Mostra o progresso da otimização
    Nfeval += 1
    # Acumula dados da otimização
    Xstates_history = np.vstack([Xstates_history, Xstates])
    outputs_history = np.vstack([outputs_history, np.hstack([dragCruise])])


print('{0:4s} | {1:8s} {2:8s} {3:8s} {4:9s} {5:8s} |'.format('Iter', 'Drag', 'Var1', 'Var2', 'Var3', 'Var4'))
# global timeOpt
# timeOpt = time.sta
Nfeval = 1
Xstates_history = np.array([0.0, 0.0, 0.0, 0.0])
outputs_history = np.array([0.0])

res = minimize(objectiveFunction,
               Xstates0,
               method='trust-constr',
               bounds=bounds,
               callback=callbackfun,
               tol=1e-2,
               options={'maxiter': 200, 'disp': True})

desvars = res.x
print('---------------------')
print(res)
print('---------------------')
print(desvars)



