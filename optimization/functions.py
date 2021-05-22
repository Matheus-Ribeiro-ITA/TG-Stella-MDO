import os
from configparser import ConfigParser
import matplotlib.pyplot as plt
import math
from _collections import OrderedDict
import numpy as np

from aircraftInfo import AircraftInfo
import MDO

config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))

Nfeval = 1
Xstates_history = np.array([0.0, 0.0, 0.0])
outputs_history = np.array([0.0])

# ----logging--------------------------------------------
logger = MDO.createLog(name="genetic")
logger.info("------------------BEGIN------------------")


def objectiveFun(stateVars):
    # ----Vertical Stabilizer-------------------------------------
    # Options: "conventional", "h", "v".
    verticalType = "v"

    # --Airfoils------------------------------------------------
    wingAirfoil = "ls417mod_cruise"
    stabAirfoil = "naca0012_cruise"
    # ----Variables Optimizer---------------------------------------
    wingSpan = stateVars[0] * 10
    wingSecPercentage = 0.5
    wingRootChord = stateVars[1]  # 0.683
    wingTipChord = stateVars[2]  # 0.344
    wingMiddleChord = (wingRootChord + wingTipChord) / 2

    horizontalSpan = 1.5
    horizontalRootChord = 0.5
    horizontalTipChord = 0.5
    horizontalXPosition = 2

    verticalSpan = 0.8  # Remember that is H vertical
    verticalRootChord = 0.375
    verticalTipChord = 0.375

    endPlateTipChord = 0.4

    wingSecPosition = wingSpan / 2 * wingSecPercentage
    wingPosSec = wingSpan / 2 * (1 - wingSecPercentage)

    # ----Config---------------------------------------
    cgCalc = 0.25

    # ----Optimizer state Variables-------------------------------------------
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
                "chord": wingMiddleChord,
                "b": wingSecPosition,
                "sweepLE": np.arctan((wingRootChord - wingMiddleChord) / 4 / wingSecPosition),
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData(wingAirfoil)
            },
            "tip": {
                "chord": wingTipChord,
                "b": wingPosSec,
                "sweepLE": np.arctan((wingMiddleChord - wingTipChord) / 4 / wingPosSec),
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
                "b": endPlateTipChord,
                "sweepLE": 0,
                "aoa": 0,
                "dihedral": 0,
                "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
            }
        })
    }

    # ---- Control Surfaces definition --------------------------------------------
    controlVariables = {
        "aileron": {
            "spanStartPercentage": 0.67,
            "cHinge": 0.7,  # From Leading Edge
            "gain": 1,
            "duplicateSign": 1
        },
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

    # ---- Avl Cases to analyse --------------------------------------------
    avlCases = {
        "cruise": {
            "altitude": 1500,
            "vCruise": 120 / 3.6,
        },  # Cruise trimmed (W/L = 1), change
        # "dive": {
        #     "altitude": 1000,
        #     "vDive": 30,
        #     "loadFactor": 1.5
        # },  # Change to Clmax
        "polar": {
            "cLPoints": [0.2, 0.44, 0.8, 1.2]
        },
        "takeOffRun": {
            'alpha': 5,
            'flap': 0,
        }
    }

    # ---- Engine Info ------------------------------------------
    engineInfo = {
        "name": "DLE 170",
        "maxPowerHp": 17.5,
        "maxThrust": 343,
        "propellerInches": [30, 12],
        "RPM": 7500,
        "engineFC": {
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
            "fuelDensityKgperL": 0.84,  # kg/liter
            "BSFC": 1 * 608.2773878418
            # Table 8.1 Gundlach: (0.7 - 1) lb/(hp.h), 1.8 for 12 l/hr, conversion 608.2773878418 to g/(kW.h)
        },  # Check figure 2.1 for correct value. Slide 248
        "altitudeCorrection": {  # From USAF thesis Travis D. Husaboe
            '1500': 0.89,
            '3000': 0.75,
            'slope': (0.88 - 1) / 1500
        }
    }

    # ---- Mission Profile ------------------------------------------
    missionProfile = {
        "climb": {
            "climbRate": 0.5,  # m/s
            "initialAltitude": 0,
            "endAltitude": 1500,
            "nSteps": 4
        },
        "cruise": {
            "altitude": 1500,
            "nSteps": 4
        },
        "descent": {
            "descentRate": 1,  # Positive value to descent
            "endAltitude": 0,
            "nSteps": 4
        }

    }

    # ---- Aircraft Info Class ----------------------------------------
    aircraftInfo = AircraftInfo(stateVariables, controlVariables, engineInfo=engineInfo)
    aircraftInfo.cg.calc = cgCalc

    # ---- Avl -----------------------------------------
    results = MDO.avlMain(aircraftInfo, avlCases, verticalType=verticalType)

    # ---- Results -----------------------------------------
    return -rangeCalculator(results=results, aircraftInfo=aircraftInfo, avlCases=avlCases,
                            missionProfile=missionProfile, logger=logger) / 100000


def callbackfun(Xstates, *_):
    global Nfeval, Xstates_history, fb_history, outputs_history, time_history
    dragCruise = objectiveFun(Xstates)
    dataStr = '{0:4d} | {1: 3.3f} {2:3.3f} {3:3.3f} {4:3.3f} |'.format(Nfeval,
                                                                       dragCruise,
                                                                       Xstates[0],
                                                                       Xstates[1],
                                                                       Xstates[2])
    print(dataStr)
    logger.info(dataStr)

    # Mostra o progresso da otimização
    Nfeval += 1
    # Acumula dados da otimização
    Xstates_history = np.vstack([Xstates_history, Xstates])
    outputs_history = np.vstack([outputs_history, np.hstack([dragCruise])])


def callbackGenetic(Xstates, convergence=0.):
    global Nfeval, Xstates_history, fb_history, outputs_history, time_history
    dragCruise = objectiveFun(Xstates)
    dataStr = '{0:4d} | {1: 3.3f} {2:3.3f} {3:3.3f} {4:3.3f} |'.format(Nfeval,
                                                                       dragCruise,
                                                                       Xstates[0],
                                                                       Xstates[1],
                                                                       Xstates[2])
    print(dataStr)
    logger.info(dataStr)

    # Mostra o progresso da otimização
    Nfeval += 1
    # Acumula dados da otimização
    Xstates_history = np.vstack([Xstates_history, Xstates])
    outputs_history = np.vstack([outputs_history, np.hstack([dragCruise])])

def rangeCalculator(results=None, aircraftInfo=None, avlCases=None, missionProfile=None, logger=None):
    PRINT = os.getenv('PRINT').lower() == 'yes'
    PLOT = os.getenv('PLOT').lower() == 'yes'
    if PRINT:
        print("------------------------------")

    # ---- Polar --------------------------------------------------
    if 'y' in config['output']['POLAR'].lower():
        [aircraftInfo.cD0, aircraftInfo.cD1, aircraftInfo.k, aircraftInfo.dataPolar] = MDO.polar(results, aircraftInfo)
        if PRINT:
            print("Polar:", aircraftInfo.cD0, aircraftInfo.cD1, aircraftInfo.k)
        if PLOT:
            MDO.plotPolar(aircraftInfo)

    # ---- Stall --------------------------------------------------
    if 'y' in config['output']['STALL'].lower() \
            or 'y' in config['output']['TAKEOFF'].lower():  # TODO: Improve Clmax for takeOff
        MDO.stall(results, aircraftInfo)
        if PRINT:
            print("Wing Stall: ", round(aircraftInfo.alphaStallWing, 1), "deg at ",
                  round(2 * aircraftInfo.stallPositionWing / aircraftInfo.wing.span * 100, 2), "% of wing")
            print(f"CL Max aircraft: {aircraftInfo.cLMax}")
        if PLOT:
            MDO.plotStall(aircraftInfo)
            MDO.plotliftDistribution(results, aircraftInfo)

    # ---- Thrust ---------------------------------
    if 'y' in config['output']['THRUST'].lower() \
            or 'y' in config['output']['TAKEOFF'].lower():
        [aircraftInfo.thrust.v0, aircraftInfo.thrust.v1, aircraftInfo.thrust.v2] = MDO.performance.dynamicThrustCurve(
            aircraftInfo.engineInfo, method="actuatorDisk")
        if PRINT:
            print(f"Thrust: {aircraftInfo.thrust.v0}, {aircraftInfo.thrust.v1}, {aircraftInfo.thrust.v2}")

    # ---- Take Off ---------------------------------
    if 'y' in config['output']['TAKEOFF'].lower():
        if "takeOffRun" in avlCases:
            [aircraftInfo.cDRunAvl, cDParasite, aircraftInfo.cDRun, aircraftInfo.cLRun] = MDO.getRun(results,
                                                                                                     aircraftInfo)
            aircraftInfo.alphaRun = results["trimmed"]["Totals"]["Alpha"]
            # mission['takeOffRun']["alpha"] = aircraftInfo.alphaRun
            [runway, speedTakeOff, timeTakeOff] = MDO.performance.takeOffRoll(aircraftInfo, dt=0.01, nsteps=15000)
            aircraftInfo.weight.fuelTakeOff = timeTakeOff * (
                    aircraftInfo.engine.consumptionMaxLperH * aircraftInfo.engine.fuelDensity / 3600) * 9.8
            if PRINT:
                print(f"Aircraft TOW: {aircraftInfo.weight.MTOW / 9.81} kg")
                print(f"Runway Length: {round(runway, 3)} m")
                print(f"Take Off Speed: {speedTakeOff} m/s")
                print(f"Time TakeOff: {timeTakeOff} s")
                print(f"Fuel mass TakeOff: {round(aircraftInfo.weight.fuelTakeOff / 9.8, 1)} kg")
                print(f"CD Run AVL: {aircraftInfo.cDRunAvl}")
                print(f"CD Run Total: {aircraftInfo.cDRun}")
                print(f"Alpha Run: {round(aircraftInfo.alphaRun, 4)} º")

    # ---- Descent ---------------------------------
    if 'y' in config['output']['DESCENT']:
        MDO.descentFuel(aircraftInfo=aircraftInfo,
                        heightInitial=missionProfile['cruise']['altitude'],
                        heightFinal=missionProfile['descent']['endAltitude'],
                        rateOfDescent=missionProfile['descent']['descentRate'],
                        nSteps=missionProfile['descent']['nSteps'],
                        logger=logger)

        if PRINT:
            print(f"fuel descent: {round(aircraftInfo.weight.fuelDescent / 9.8, 1)} kg")
            print(f"time descent: {round(aircraftInfo.performance.descent.time / 60, 1)} min")

    # ---- Climb ---------------------------------
    if 'y' in config['output']['CLIMB'].lower():
        MDO.climbFuel(aircraftInfo=aircraftInfo,
                      heightInitial=missionProfile['climb']['initialAltitude'],
                      heightFinal=missionProfile['climb']['endAltitude'],
                      rateOfClimb=missionProfile['climb']['climbRate'],
                      nSteps=missionProfile['climb']['nSteps'],
                      logger=logger)
        if PRINT:
            print(f"Fuel Climb: {round(aircraftInfo.weight.fuelClimb / 9.8, 1)} kg")
            print(f"Time Climb: {round(aircraftInfo.performance.climb.time / 60, 1)} min")

    # ---- Cruise ---------------------------------
    if 'y' in config['output']['CRUISE'].lower():
        fuelKg = (aircraftInfo.weight.fuel - aircraftInfo.weight.fuelTakeOff - aircraftInfo.weight.fuelClimb) / 9.8
        fuelDescentKg = (aircraftInfo.weight.fuelReserve + aircraftInfo.weight.fuelDescent) / 9.8

        MDO.cruise(aircraftInfo=aircraftInfo,
                   avlCases=avlCases,
                   fuelKg=fuelKg,
                   fuelDescentKg=fuelDescentKg,
                   nSteps=missionProfile['cruise']['nSteps'],
                   logger=logger)
        if PRINT:
            print(
                f"Range Cruise: {round(aircraftInfo.performance.cruise.range / 1000, 2)} km, with {round(fuelKg - fuelDescentKg, 1)} kg of fuel")
            print(
                f"Time Cruise: {math.floor(aircraftInfo.performance.cruise.time / 3600)} h e {round(aircraftInfo.performance.cruise.time / 60 - math.floor(aircraftInfo.performance.cruise.time / 3600) * 60, 1)} min")

    # ---- Plot Mission Profile ---------------------------

    if 'y' in config['output']['CRUISE'].lower() and \
            'y' in config['output']['CLIMB'].lower() and \
            'y' in config['output']['DESCENT'].lower():

        rangeClimb = aircraftInfo.performance.climb.range
        rangeCruise = aircraftInfo.performance.cruise.range
        rangeDescent = aircraftInfo.performance.descent.range
        rangeAll = rangeDescent + rangeCruise + rangeDescent

        if PLOT:
            missionPlot = [[0, runway / 1000, rangeClimb / 1000, (rangeClimb + rangeCruise) / 1000,
                            rangeAll / 1000],
                           [0, 0, 1500, 1500, 0]]

            plt.plot(missionPlot[0], missionPlot[1])
            plt.xlabel("Range (km)")
            plt.ylabel("Altitude (m)")
            plt.show()

        if PRINT:
            print(f"Range flight: {round(rangeAll / 1000, 1)} km")

    # ---- End ---------------------------
    if PRINT:
        print("------------------------------")

    return rangeAll
