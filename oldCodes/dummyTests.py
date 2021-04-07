import time
from _collections import OrderedDict
from configparser import ConfigParser
import numpy as np
import os

from aircraftInfo import AircraftInfo
import MDO

# ----Process Time--------------------------------------------
startTime = time.time()

# ----Debug bool----------------------------------------------

config = ConfigParser()
config.read(os.path.join("../outputsConfig.cfg"))

os.environ['DEBUG'] = config['env']['DEBUG']
os.environ['PLOT'] = config['env']['PLOT']
os.environ['PRINT'] = config['env']['PRINT']


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

wingSecPosition = wingSpan/2*wingSecPercentage
wingPosSec = wingSpan/2*(1-wingSecPercentage)

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
            "b": horizontalSpan/2,
            "sweepLE": np.arctan((horizontalRootChord-horizontalTipChord)/4/horizontalSpan/2),
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
            "sweepLE": np.arctan((verticalRootChord-verticalTipChord)/4/verticalSpan/2),
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


keysSurfaceDict = list(stateVariables["wing"].keys())
surfaceArea = 0
surfaceMAC = 0
surfaceSpan = 0
surfaceTipX = 0
# -----------------------------------------------


print(zip(1,2))


