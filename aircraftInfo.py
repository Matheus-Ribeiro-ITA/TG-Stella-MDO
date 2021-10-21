import MDO
import numpy as np
from math import tan
import os
from dataclasses import dataclass


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
        self.engine = Engine(engineInfo)

        self.machCalc = 0.1  # TODO:
        self.reynoldsCalc = 1*10**6  # TODO:

        # Wing Info
        self.wing = Surface(surfaceDict=stateVariables['wing'],
                            controlVariables=controlVariables,
                            name="wing")

        # Horizontal Info
        # if 'horizontal' in stateVariables:  # TODO: Add V case
        #     self.horizontal = Surface(surfaceDict=stateVariables['horizontal'],
        #                               controlVariables=controlVariables,
        #                               name="horizontal")
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

        # self.cLMaxHorizontalAirfoil = stateVariables["horizontal"]["root"]["airfoil"].clmax  # TODO: Add V case
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
        self.cLMax = None
        self.cLAlpha0 = None
        self.cLSlope = None

        # Flight Info
        self.performance = Performance()
        self.cLCruise = None
        self.loiterTime = 3600

        # Weight and Cg Info
        self.weight = Weight(initialMTOW=200 * 9.81)
        self.cg = Cg(self)
        self.weight.calc(aircraftInfo=self)
        # self.cg.calc()


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
        self.thrust = Thrust(engineInfo)

    def adjustCG(self, cgFixed=None, smFixedPercent=None):

        if smFixedPercent is not None:
            if self.xNeutralPoint is None: raise Exception("Neutral Point not calculated for some reason")
            self.cg.calc = self.xNeutralPoint - smFixedPercent*self.wing.meanChord/100
        else:
            self.cg.calc = cgFixed

        if 'y' in os.getenv('DEBUG').lower():
            print("-"*10)
            print(f"xNeutralPoint: {self.xNeutralPoint}")


class Surface:
    def __init__(self, surfaceDict=None, controlVariables=None, name=None):
        self.xMeanChord, self.yMeanChord = xyMeanChord(surfaceDict)
        self.area, self.meanChord, self.span, self.sweep, self.tipX = MDO.infoSurface(surfaceDict)
        self.taperRatio = surfaceDict['tip']['chord']/surfaceDict['root']['chord']
        self.aspectRatio = self.span**2/self.area
        self.rootX = surfaceDict['root']['x']

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
    def __init__(self, engineInfo):
        self.v0 = None
        self.v1 = None
        self.v2 = None
        self.slopeHeight = engineInfo['altitudeCorrection']['slope']


class Weight:
    def __init__(self, initialMTOW=200 * 9.81):
        self.engine = 63 * 9.8  # Atobá Data

        self.initialMTOW = initialMTOW
        # weightEmpty, cgEmpty = MDO.weightCalc(self, method="Raymer")
        # self.empty = None
        self.fuel = 20 * 9.8

        self.fuelReserve = 5 * 9.8
        self.fuelDescent = None
        self.fuelCruise = None
        self.fuelClimb = None
        self.fuelTakeOff = None

        self.fuelActual = self.fuel
        # self.MTOW = None
        self.allElse = {  # Atobá Data (kg, m)
            "All": [30 * 9.8, -3.1],
        }

        self.wing = None
        self.horizontal = None
        self.vertical = None
        self.fuselage = None

    def calc(self, aircraftInfo):
        weightVar = os.getenv("WEIGHT")
        if weightVar == 'Raymer':
            self.empty, _ = MDO.weightCalc(aircraftInfo, weightInfo=self, method="Raymer")
            self.MTOW = self.empty + self.fuel
        else:
            self.empty = float(weightVar) * 9.81 - self.fuel
            self.MTOW = float(weightVar) * 9.81


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


class Cg:
    def __init__(self, aircraftInfo):
        self.engine = [aircraftInfo.fuselage.length, 0, 0]  # TODO
        self.wing = None
        self.horizontal = None
        self.vertical = None
        self.fuselage = None
        self.fuel = 0.0  # TODO:

        self.full = []
        self.empty = []

        self.calc = None
        self.cg_cruise = 0.31625  # TODO: (cgFull + cgCalc)/2

    # def calc(self):
    #     weightVar = os.getenv("WEIGHT")
    #     if weightVar == 'Raymer':
    #         _, self.empty = MDO.weightCalc(self, method="Raymer")
    #     else:
    #         self.empty = 0.31625


class Engine:
    def __init__(self, engineInfo):
        self.name = engineInfo['name']
        self.consumptionMaxLperH = engineInfo['engineFC']['consumptionMaxLperH']
        self.fuelDensity = engineInfo['engineFC']['fuelDensityKgperL']


class Performance:
    def __init__(self):
        self.cruise = FlightInfo()
        self.climb = FlightInfo()
        self.descent = FlightInfo()


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

        if spanSum <= yMeanChord < spanSum + span:
            ySec = yMeanChord-spanSum
            xMeanChord = xSec + ySec*tan(sweepLE)
            break
        xSec += span*tan(sweepLE)
        spanSum += span

    return [xMeanChord, yMeanChord]


@dataclass
class FlightInfo:
    cD: list = None
    cL: list = None
    range: float = None
    time: float = None


