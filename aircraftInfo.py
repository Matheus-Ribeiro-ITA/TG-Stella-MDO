import MDO
import numpy as np
from math import tan
import os


class AircraftInfo:
    def __init__(self, stateVariables, controlVariables, engineInfo=None):
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
        self.controlVariables = controlVariables
        self.engineInfo = engineInfo

        self.machCalc = 0.1  # TODO:
        self.reynoldsCalc = 1*10**6  # TODO:

        # Wing Info
        self.wing = Surface(surfaceDict=stateVariables['wing'],
                            controlVariables=controlVariables,
                            name="wing")

        # Horizontal Info
        if 'horizontal' in stateVariables:
            self.horizontal = Surface(surfaceDict=stateVariables['horizontal'],
                                      controlVariables=controlVariables,
                                      name="horizontal")
        # Vertical Info
        if 'vertical' in stateVariables:
            self.vertical = Surface(surfaceDict=stateVariables['vertical'],
                                    controlVariables=controlVariables,
                                    name="vertical")
        # Fuselage Info
        self.fuselage = Fuselage(length=1.2,
                                 diameter=0.5,
                                 reynoldsCalc=self.reynoldsCalc,
                                 machCalc=self.machCalc)

        # Landing Gear Info
        self.xNoseLG = -2  # TODO
        self.xMainLG = -0.22

        # Airfoil Info
        self.cLMaxWingAirfoil = stateVariables["wing"]["root"]["airfoil"].clmax

        self.cLMaxHorizontalAirfoil = stateVariables["horizontal"]["root"]["airfoil"].clmax
        self.tcRootWing = 0.123  # TODO:

        # Polar Info
        self.cD0 = None
        self.cD1 = None
        self.k = None

        # self.cD0Run = None
        # self.cD1Run = None
        # self.kRun = None

        self.cLRun = None
        self.cDRunAvl = None
        self.cDRun = None

        # Flight Info
        self.cLCruise = None
        self.loiterTime = 3600
        self.cLMax = None  # TODO:

        # Weight and Cg Info
        self.weight = Weight(initialMTOW=200 * 9.81)
        self.cg = Cg()
        self.weight.empty, self.cg.empty = MDO.weightCalc(self, method="Raymer")

        weightVar = os.getenv("WEIGHT")
        if weightVar == 'Raymer':
            self.weight.MTOW = self.weight.empty + self.weight.fuel
        else:
            self.weight.MTOW = float(weightVar) * 9.81

        # Stall
        self.alphaStalls = None
        self.stallPosition = None
        self.yStrips = None

        self.alphaStallWing = None
        self.stallPositionWing = None
        self.cLSlope = None
        self.cLAlpha0 = None

        # Stability
        self.xNeutralPoint = None
        self.staticMargin = None

        # Thrust Curve
        self.thrust = Thrust()


def xyMeanChord(surfDict):
    """
    # Description:
        Calculates x distance from root LE of the mean aerodynamic chord.
    See Gundlach, Jay-Designing Unmanned Aircraft Systems -
    A Comprehensive Approach-American Institute of Aeronautics and Astronautics (2012) for equations.

    ## Params:
        -
    """
    keysSurfaceDict = list(surfDict.keys())
    spanSum = 0
    dArea = 0
    areaTotal = 0
    for i in range(len(keysSurfaceDict) - 1):
        cRoot = surfDict[keysSurfaceDict[i]]['chord']
        cTip = surfDict[keysSurfaceDict[i+1]]['chord']
        span = surfDict[keysSurfaceDict[i+1]]['b']

        d = span/3*(cRoot + 2*cTip)/(cRoot + cTip) + spanSum
        area = (cTip+cRoot)/2*span

        dArea += d*area
        spanSum += span
        areaTotal += area

    yMeanChord = dArea/areaTotal
    spanSum = 0
    xSec = 0
    for i in range(len(keysSurfaceDict) - 1):
        span = surfDict[keysSurfaceDict[i+1]]['b']
        sweepLE = surfDict[keysSurfaceDict[i+1]]['sweepLE']

        if spanSum < yMeanChord < spanSum + span:
            ySec = yMeanChord-spanSum
            xMeanChord = xSec + ySec*tan(sweepLE)
            break
        xSec += span*tan(sweepLE)

    return [xMeanChord, yMeanChord]


class Surface:
    def __init__(self, surfaceDict=None, controlVariables=None, name=None):
        self.xMeanChord, self.yMeanChord = xyMeanChord(surfaceDict)
        self.area, self.meanChord, self.span, self.sweep, self.tipX = MDO.infoSurface(surfaceDict)
        self.taperRatio = surfaceDict['tip']['chord']/surfaceDict['root']['chord']
        self.aspectRatio = self.span**2/self.area

        if "aileron" in controlVariables and name == 'wing':
            self.aileronArea = self.area*controlVariables["aileron"]["spanStartPercentage"]*\
                               (1-controlVariables["aileron"]["cHinge"])
        else:
            self.aileronArea = self.area*0.4*0.2  # Standard Value

        if "ruddervator" in controlVariables and name == 'vertical':
            pass  # TODO:

        if "elevator" in controlVariables and name == 'horizontal':
            self.elevatorArea = self.area * controlVariables["elevator"]["spanStartPercentage"] * \
                               (1 - controlVariables["elevator"]["cHinge"])
        else:
            self.elevatorArea = self.area * 0.4 * 0.2  # TODO: Change this parameters to inputs

        if "rudder" in controlVariables and name == 'vertical':
            self.rudderArea = self.area * controlVariables["rudder"]["spanStartPercentage"] * \
                                (1 - controlVariables["rudder"]["cHinge"])
        else:
            self.rudderArea = self.area * 0.4 * 0.2


class Fuselage:
    def __init__(self, length=1.2, diameter=0.5, reynoldsCalc=None, machCalc=None):
        self.finenessRatio = length / diameter
        self.wetArea = np.pi * diameter * length * (1 - 2 / self.finenessRatio) ** (2.0 / 3.0) * (1 + 1 / self.finenessRatio ** 2)
        self.length = length
        self.interferenceFactor = 1.05
        self.coefficientFriction = 0.455/(np.log10(reynoldsCalc) ** 2.58 * (1 + 0.144 * machCalc ** 2) ** 0.58)
        # Gimbal
        self.gimbalFrontalArea = 3.1415*0.20**2


class Thrust:
    def __init__(self):
        self.v0 = None
        self.v1 = None
        self.v2 = None


class Weight:
    def __init__(self, initialMTOW=200 * 9.81):
        self.engine = 63 * 9.81  # Atobá Data

        self.initialMTOW = initialMTOW
        # weightEmpty, cgEmpty = MDO.weightCalc(self, method="Raymer")
        self.empty = None
        self.fuel = 0 * 9.81

        # All Else Weight
        # self.allElse = {  # Atobá Data (kg, m)
        #     "propeller": [2.6*9.81, -3.1],
        #     "brakes": [2.38*9.81, -.350],
        #     "parachute": [13*9.81, 0],
        #     "gimbal": [3*9.81, 0],
        #     "receptors": [0.424*9.81, 0],
        #     "batery60Ah": [12.7*9.81, 0],
        #     "batery12Ah": [3.845*9.81, 0],
        #     "ballast": [10*9.81, 0]
        # }  # TODO:
        self.allElse = {  # Atobá Data (kg, m)
            "All": [0 * 9.81, -3.1],
        }

        # self.cgEmpty = cgEmpty
        # self.cgFull = 0.0  # TODO:
        # self.cgCalc = 0.31625  # TODO: (cgFull + cgCalc)/2


class Cg:
    def __init__(self):
        self.engine = [-2.5, 0, 0]  # TODO
        self.empty = None
        self.full = 0.0  # TODO:
        self.calc = 0.31625  # TODO: (cgFull + cgCalc)/2


