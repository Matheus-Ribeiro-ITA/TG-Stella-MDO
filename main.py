import time
from _collections import OrderedDict
from configparser import ConfigParser
import numpy as np
import os

from aircraftInfo import AircraftInfo
import MDO

# ----Process Time--------------------------------------------
startTime = time.time()

# ----logging--------------------------------------------
logger = MDO.createLog(name="main")
logger.info("------------------BEGIN------------------")

# ----Config ----------------------------------------------

config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))

os.environ['DEBUG'] = config['env']['DEBUG']
os.environ['PLOT'] = config['env']['PLOT']
os.environ['PRINT'] = config['env']['PRINT']
os.environ['WEIGHT'] = config['methods']['WEIGHT']

# ----Vertical Stabilizer-------------------------------------
# Options: "conventional", "h", "v".
verticalType = "v"

# --Airfoils------------------------------------------------
wingAirfoil = "ls417mod_cruise"
stabAirfoil = "naca0012_cruise"

# ----Variables Optimizer---------------------------------------
wingSpan = 6
wingSecPercentage = 0.5
wingRootChord = 0.68  # 0.683
wingTipChord = 0.35  # 0.344
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
    },
    # "untrimmed_polar": {
    #     "cLPoints": [0.2, 0.44, 0.8]
    # }
    "hingeMoment": {
        'alpha': 8,
        'flap': 20,
        'aileron': 20,
        'elevator': 20
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

# ---- Aircraft Info Class ----------------------------------------
aircraftInfo = AircraftInfo(stateVariables, controlVariables, engineInfo=engineInfo)
aircraftInfo.cgCalc = cgCalc

# ---- Avl -----------------------------------------
results = MDO.avlMain(aircraftInfo, avlCases, verticalType=verticalType)

# ---- Results -----------------------------------------
MDO.mainResults(results=results, aircraftInfo=aircraftInfo, avlCases=avlCases,
                missionProfile=missionProfile, logger=logger)

# ---- Time-----------------------------------------
print(f"Process Time: {round((time.time() - startTime),1)} s")
logger.info(f"Process Time: {round((time.time() - startTime),1)} s")
logger.info("------------------END------------------")