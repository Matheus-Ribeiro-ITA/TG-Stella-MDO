import time
from _collections import OrderedDict
import numpy as np
import MDO


def set_state_variables(wingRootChord=None, wingAirfoil=None, wingMiddleChord=None,
                        wingSecPosition=None, wingTipChord=None, wingPosSec=None,
                        horizontalRootChord=None, horizontalXPosition=None, verticalXPosition=None,
                        horizontalTipChord=None, horizontalSpan=None, verticalRootChord=None,
                        verticalTipChord=None, verticalSpan=None, stabAirfoil=None,
                        fuselageLength=None, fuselageDiameter=0.18):


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
        # "horizontal": OrderedDict({  # TODO: Add V case
        #     "root": {
        #         "chord": horizontalRootChord if horizontalRootChord is not None else 0,
        #         "aoa": 0,
        #         "x": horizontalXPosition if horizontalXPosition is not None else 0,
        #         "y": 0,
        #         "z": 0.5,
        #         "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
        #     },
        #     "tip": {
        #         "chord": horizontalTipChord,
        #         "b": horizontalSpan / 2 if horizontalSpan is not None else 0,
        #         "sweepLE": np.arctan((horizontalRootChord - horizontalTipChord) / 4 / horizontalSpan / 2) if horizontalSpan is not None else 0,
        #         "aoa": 0,
        #         "dihedral": 0,
        #         "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
        #     }
        # }),
        "vertical": OrderedDict({
            "root": {
                "chord": verticalRootChord,
                "aoa": 0,
                "x": verticalXPosition,
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
        # "endPlate": OrderedDict({
        #     "root": {
        #         "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
        #     },
        #     "tip": {
        #         "chord": 0,
        #         "b": endPlateTipChord,
        #         "sweepLE": 0,
        #         "aoa": 0,
        #         "dihedral": 0,
        #         "airfoil": MDO.airfoils.AirfoilData(stabAirfoil)
        #     }
        # })
        "fuselage": OrderedDict({
            'length': fuselageLength,
            'diameter': fuselageDiameter
        }),
    }

    # ---- Control Surfaces definition --------------------------------------------
    controlVariables = {
        # "aileron": {  # TODO: Fix aileron bug with wingspan
        #     "spanStartPercentage": 0.67,
        #     "cHinge": 0.7,  # From Leading Edge
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
        # "flap": {
        #     "spanStartPercentage": 0.0,
        #     "cHinge": 0.7,  # From Leading Edge
        #     "gain": 1,
        #     "duplicateSign": 1
        # },
    }

    # ---- Avl Cases to analyse --------------------------------------------
    avlCases = {
        "cruise": {
            "altitude": 1500,
            "vCruise": 148 / 3.6,  # TODO: Variable cruise speed
        },  # Cruise trimmed (W/L = 1), change
        # "dive": {
        #     "altitude": 1000,
        #     "vDive": 30,
        #     "loadFactor": 1.5
        # },  # Change to Clmax
        "polar": {
            "cLPoints": [-0.6, -0.2, 0.2, 0.8, 1.0]  # [-0.5, -0.4, 0.2, 0.44, 0.8, 1, 1.2, 1.3]
        },  # [-0.2, 0.6, 0.8, 1.2]
        "takeOffRun": {
            'alpha': 5,
            'flap': 0,
        },
        # "untrimmed_polar": {
        #     "cLPoints": [0.2, 0.44, 0.8]
        # }
        # "hingeMoment": {
        #     'alpha': 8,
        #     'flap': 20,
        #     'aileron': 20,
        #     'elevator': 20
        # },
    }

    avlMandatoryCases = {
        "neutralPoint": {
            "alphas": [0, 6]
        # "altitude": 1500,
        # "vCruise": [120/3.6],
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
            "climbRate": 1,  # m/s
            "initialAltitude": 0,
            "endAltitude": 1500,
            "nSteps": 10
        },
        "cruise": {
            "altitude": 1500,
            "nSteps": 10
        },
        "descent": {
            "descentRate": 1,  # Positive value to descent
            "endAltitude": 0,
            "nSteps": 10
        }

    }

    return stateVariables, controlVariables, avlMandatoryCases, avlCases, engineInfo, missionProfile
