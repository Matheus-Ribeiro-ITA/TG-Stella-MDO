"""
Weight estimation
"""
import numpy as np


def weightCalc(aircraftInfo, method="Raymer"):
    """

    """
    wingArea = aircraftInfo.wing.area
    aileronArea = aircraftInfo.wing.aileronArea
    arWing = aircraftInfo.wing.span ** 2 / wingArea
    tcRootWing = aircraftInfo.tcRootWing
    taperRatioWing = aircraftInfo.wing.taperRatio
    wingSweep = aircraftInfo.wing.sweep
    mtow = aircraftInfo.weight.initialMTOW
    wingMeanChord = aircraftInfo.wing.meanChord
    xWingMeanChord = aircraftInfo.wing.xMeanChord

    # Horizontal
    horizontalArea = aircraftInfo.horizontal.area
    xHorizontalMeanChord = aircraftInfo.horizontal.xMeanChord
    horizontalMeanChord = aircraftInfo.horizontal.meanChord

    # Vertical
    verticalArea = aircraftInfo.vertical.area
    xVerticalMeanChord = aircraftInfo.vertical.xMeanChord
    verticalMeanChord = aircraftInfo.vertical.meanChord

    # Fuselage
    fuselageWetArea = aircraftInfo.fuselage.wetArea
    fuselageLength = aircraftInfo.fuselage.length

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
        return aircraftInfo.weight.engine, aircraftInfo.cg.engine[0]

    def _allElseWeight():
        return sum([v[0] for v in aircraftInfo.weight.allElse.values()]), sum([v[1] for v in aircraftInfo.weight.allElse.values()])

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
