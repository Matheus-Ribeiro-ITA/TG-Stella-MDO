import MDO
import numpy as np

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
        self.wingArea, self.meanChord, self.wingSpan, self.wingSweep = MDO.infoSurface(stateVariables['wing'])
        self.xWingMeanChord = self.wingSpan * 0.05  # TODO
        self.taperRatioWing = stateVariables['wing']['tip']['chord']/stateVariables['wing']['root']['chord']
        self.aspectRatio = self.wingSpan**2/self.wingArea
        if "aileron" in controlVariables:
            self.aileronArea = self.wingArea*controlVariables["aileron"]["spanStartPercentage"]*\
                               (1-controlVariables["aileron"]["cHinge"])
        else:
            self.aileronArea = self.wingArea*0.4*0.2

        # Horizontal Info
        self.horizontalArea, self.horizontalMeanChord, self.horizontalSpan, self.horizontalSweep = \
            MDO.infoSurface(stateVariables['horizontal'])
        self.xHorizontalMeanChord = self.horizontalSpan * 0.05  # TODO

        # Vertical Info
        self.verticalArea, self.verticalMeanChord, self.verticalSpan, self.verticalSweep = \
            MDO.infoSurface(stateVariables['vertical'])
        self.xVerticalMeanChord = self.verticalSpan * 0.05  # TODO

        # Fuselage Info
        lengthFuselage = 1.2
        diameterFuselage = 0.5
        self.finenessRatio = lengthFuselage / diameterFuselage
        self.fuselageWetArea = np.pi * diameterFuselage * lengthFuselage * (1 - 2 / self.finenessRatio) ** (2.0 / 3.0) * (1 + 1 / self.finenessRatio ** 2)
        self.fuselageLength = lengthFuselage
        self.interferenceFactor = 1.05
        self.coefficientFriction = 0.455/(np.log10(self.reynoldsCalc) ** 2.58 * (1 + 0.144 * self.machCalc ** 2) ** 0.58)

        # Gimbal
        self.gimbalFrontalArea = 3.1415*0.20**2

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
            "All": [0*9.81, -3.1],
        }

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
        self.engineWeight = 63*9.81  # Atobá Data
        self.xEngine = -2.5  # TODO

        self.initialMTOW = 200 * 9.81
        weightEmpty, cgEmpty = MDO.weightCalc(self, method="Raymer")
        self.weightEmpty = weightEmpty
        self.weightFuel = 0 * 9.81
        self.MTOW = 120*9.81 #self.weightEmpty + self.weightFuel

        self.cgEmpty = cgEmpty
        self.cgFull = 0.0  # TODO:
        self.cgCalc = 0.31625  # TODO: (cgFull + cgCalc)/2

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

        self.thrustV0 = None
        self.thrustV1 = None
        self.thrustV2 = None



