"""
Weight estimation
"""
import numpy as np


def weightCalc(aircraftInfo, method="Raymer"):
    """

    """
    wingArea = aircraftInfo.wingArea
    aileronArea = aircraftInfo.aileronArea
    arWing = aircraftInfo.wingSpan ** 2 / aircraftInfo.wingArea
    tcRootWing = aircraftInfo.tcRootWing
    taperRatioWing = aircraftInfo.taperRatioWing
    wingSweep = aircraftInfo.wingSweep
    mtow = aircraftInfo.initalMTOW
    wingMeanChord = aircraftInfo.meanChord
    xWingMeanChord = aircraftInfo.xWingMeanChord

    # Horizontal
    horizontalArea = aircraftInfo.horizontalArea
    xHorizontalMeanChord = aircraftInfo.xHorizontalMeanChord
    horizontalMeanChord = aircraftInfo.horizontalMeanChord

    # Vertical
    verticalArea = aircraftInfo.verticalArea
    xVerticalMeanChord = aircraftInfo.xVerticalMeanChord
    verticalMeanChord = aircraftInfo.verticalMeanChord

    # Fuselage
    fuselageWetArea = aircraftInfo.fuselageWetArea
    fuselageLength = aircraftInfo.fuselageLength

    def _raymerWing():
        Nz = 1.5 * 2.5
        wingAreaBtu = wingArea * 10.7639  # Wing Area in ft^2.
        controlAreaBtu = aileronArea * 10.7639  # Control Surface Area in ft^2.
        mto6Btu = mtow * 0.224809  # lbf
        wingWeightBtu = 0.0051 * (mto6Btu * Nz) ** 0.557 * wingAreaBtu ** 0.649 \
                        * arWing ** 0.55 * tcRootWing ** (-0.4) \
                        * (1 + taperRatioWing) ** 0.1 * \
                        (np.cos(wingSweep)) ** (-1) * controlAreaBtu ** 0.1
        wingWeight = wingWeightBtu / 0.224809  # Wing weight in N.

        xCgWing = xWingMeanChord + 0.4 * wingMeanChord
        return wingWeight, xCgWing

    def _raymerStabSurfaces(surfaceArea, meanChord, xMeanChord):
        weight = 27 * 9.81 * surfaceArea
        xcg = xMeanChord + 0.4 * meanChord
        return weight, xcg

    def _raymerFuselage():
        Wf = 24 * 9.81 * fuselageWetArea
        xcgf = 0.45 * fuselageLength
        return Wf, xcgf

    def _raymerLandingGear(W0, xCG, loadPercentage, weightFactor=0.043):
        weightLandingGear = loadPercentage * weightFactor * W0
        return weightLandingGear, xCG

    def _engineWeight():
        return aircraftInfo.engineWeight, aircraftInfo.xEngine

    def _allElseWeight():
        return sum([v[0] for v in aircraftInfo.allElse.values()]), sum([v[1] for v in aircraftInfo.allElse.values()])


    methods = {
        "Raymer": [_raymerWing(),
                  _raymerStabSurfaces(horizontalArea, horizontalMeanChord, xHorizontalMeanChord),
                  _raymerStabSurfaces(verticalArea, verticalMeanChord, xVerticalMeanChord),
                  _raymerFuselage(),
                  _raymerLandingGear(mtow, aircraftInfo.xNoseLG, 0.15),
                  _raymerLandingGear(mtow, aircraftInfo.xMainLG, 0.85),
                   _engineWeight(),
                   _allElseWeight()]
    }

    return [sum(i) for i in zip(*methods[method])]
