from dataclasses import dataclass
from _collections import OrderedDict

stateVariables = {
    "wing": OrderedDict({
        "root": {
            "chord": 0.3,
            "aoa": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "airfoil": "2414"
        },
        "middle": {
            "chord": 0.3,
            "b": 1,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "2414"
        },
        "tip": {
            "chord": 0.1,
            "b": 0.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "2414"
        },
    }),
    "horizontal": OrderedDict({
        "root": {
            "chord": 0.2,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0,
            "airfoil": "0012"
        },
        "tip": {
            "chord": 0.2,
            "b": 0.4,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "0012"
        }
    }),
    "vertical": OrderedDict({
        "root": {
            "chord": 0.2,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0.5,
            "airfoil": "0012"
        },
        "tip": {
            "chord": 0.2,
            "b": 0.4,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "0012"
        }
    })
}


class AircraftInfo:
    def __init__(self, stateVariables):
        """
        # Description:
        - Aircraft Info that can be useful on AVL and other calculations.

        ## Parameters (required):
        - stateVariables [dict]: Project stateVariables.

        ## Atributes (return only):
        - stateVariables [dict]: Copy of Project stateVariables.
        - wingArea [float]: Area of wing.
        - meanChord [float]: Mean Aerodynamic Chord of wing.
        - wingSpan [float]: Wing span.
        """
        self.stateVariables = stateVariables.copy()
        wingArea, wingMAC, wingSpan = infoSurface(stateVariables['wing'])
        self.wingArea = wingArea
        self.meanChord = wingMAC
        self.wingSpan = wingSpan


def infoSurface(surfaceDict):
    """
    # Description:
        Get surface (wing, horizontal or vertical) area, mean aero chord and span.

    ## Inputs:
    - surfaceDict [dict]: valeus from surfaces in stateVariables inner dict. Ex: stateVariables['wing'].

    ## Outputs:
    - surfaceArea [float]:
    - surfaceMAC [float]:
    - surfaceSpan [float]:
    """
    keysSurfaceDict = list(surfaceDict.keys())
    surfaceArea = 0
    surfaceMAC = 0
    surfaceSpan = 0
    for i in range(len(keysSurfaceDict) - 1):
        chordRootSec = surfaceDict[keysSurfaceDict[i]]['chord']
        chordTipSec = surfaceDict[keysSurfaceDict[i + 1]]['chord']
        spanSec = surfaceDict[keysSurfaceDict[i + 1]]['b']

        secArea = spanSec * (chordRootSec + chordTipSec) / 2
        surfaceArea += secArea

        taperRatio = chordTipSec / chordRootSec
        secMAC = 2 / 3 * chordRootSec * (1 + taperRatio + taperRatio ** 2) / (1 + taperRatio)
        surfaceMAC += secArea * secMAC

        surfaceSpan += spanSec

    surfaceMAC = surfaceMAC / surfaceArea

    return surfaceArea, surfaceMAC, surfaceSpan
