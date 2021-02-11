
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

        self.mass = 10
        self.cLMax = 1.5

        self.massEmpty = 380
        self.massFuel = 120
        self.MTOW = self.mass + self.massFuel

        self.cD0 = None
        self.k = None

        self.cLCruise =None

        self.loiterTime = 3600


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