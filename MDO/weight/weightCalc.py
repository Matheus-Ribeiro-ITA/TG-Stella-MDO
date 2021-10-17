"""
Weight estimation
"""
import os

import numpy as np


def weightCalc(aircraftInfo, weightInfo=None, method="Raymer"):
    """

    """
    # Wing
    wingArea = aircraftInfo.wing.area
    aileronArea = aircraftInfo.wing.aileronArea
    arWing = aircraftInfo.wing.span ** 2 / wingArea
    tcRootWing = aircraftInfo.tcRootWing
    taperRatioWing = aircraftInfo.wing.taperRatio
    wingSweep = aircraftInfo.wing.sweep
    mtow = weightInfo.initialMTOW
    wingMeanChord = aircraftInfo.wing.meanChord
    xWingMeanChord = aircraftInfo.wing.xMeanChord

    # Horizontal
    horizontalArea = aircraftInfo.horizontal.area
    xHorizontalMeanChord = aircraftInfo.horizontal.xMeanChord
    horizontalMeanChord = aircraftInfo.horizontal.meanChord
    xHorizontalRoot = aircraftInfo.horizontal.rootX

    # Vertical
    verticalArea = aircraftInfo.vertical.area
    xVerticalMeanChord = aircraftInfo.vertical.xMeanChord
    verticalMeanChord = aircraftInfo.vertical.meanChord
    xVerticalRoot = aircraftInfo.vertical.rootX

    # Fuselage
    fuselageWetArea = aircraftInfo.fuselage.wetArea
    fuselageLength = aircraftInfo.fuselage.length

    # Cruise
    q = 1/2*(1*0.0765)*(20*3.28084)**2  # TODO: Dynamic pressure at cruise

    def _raymerWing(method_calc='General Aviation'):
        """Calculated with formula from Raymer new book page 576"""
        Nz = 1.5 * 2.5
        wingAreaFt = wingArea * 10.7639  # wingAreaLb: Wing Area in ft^2.

        if method_calc == 'General Aviation':
            mto6Btu = mtow * 0.224809  # lbf
            wingWeightBtu = 0.036 * wingAreaFt ** 0.758 * (arWing/(np.cos(wingSweep)**2)) ** 0.6 \
                            * q ** 0.006 * taperRatioWing ** 0.04 \
                            * (100*tcRootWing/(np.cos(wingSweep))) ** (-0.3) \
                            * (mto6Btu * Nz) ** 0.49

            wingWeightBtu = 2* wingWeightBtu # TODO: This is a correction carteada to make sense.
        elif method_calc == 'Cargo Transport':
            controlAreaBtu = aileronArea * 10.7639  # Control Surface Area in ft^2.
            mto6Btu = mtow * 0.224809  # lbf
            wingWeightBtu = 0.0051 * (mto6Btu * Nz) ** 0.557 * wingAreaFt ** 0.649 \
                            * arWing ** 0.55 * tcRootWing ** (-0.4) \
                            * (1 + taperRatioWing) ** 0.1 * \
                            (np.cos(wingSweep)) ** (-1) * controlAreaBtu ** 0.1

        wingWeight = wingWeightBtu / 0.224809  # wingWeight: Wing weight in N.
        xCgWing = xWingMeanChord + 0.4 * wingMeanChord

        aircraftInfo.cg.wing = [xCgWing, 0, 0]
        aircraftInfo.weight.wing = wingWeight

        if os.environ["DEBUG"].lower() == 'yes':
            print("-"*10)
            print('Wing Weight and CG: ', wingWeight, xCgWing)
            print(f'Wing area: {wingArea}')
            print(f'Weight/Area: {wingWeight/wingArea/9.81}')

        return wingWeight, xCgWing

    def _raymerStabSurfaces(surfaceArea, meanChord, xMeanChord, xRoot, name='horizontal'):
        weight = 10 * 9.81 * surfaceArea
        xcg = xRoot + xMeanChord + 0.4 * meanChord

        if name == 'horizontal':
            aircraftInfo.cg.horizontal = [xcg, 0, 0]
            aircraftInfo.weight.horizontal = weight
        elif name == 'vertical':
            aircraftInfo.cg.vertical = [xcg, 0, 0]
            aircraftInfo.weight.vertical = weight

        if os.environ["DEBUG"].lower() == 'yes':
            print("-" * 10)
            print('Horizontal or Vertical Weight and CG: ', weight, xcg)
            print(f'Weight/Area: {weight / surfaceArea / 9.81}')
        return weight, xcg

    def _raymerFuselage():
        Wf = 7 * 9.81 * fuselageWetArea
        xcgf = 0.45 * fuselageLength

        aircraftInfo.cg.fuselage = [xcgf, 0, 0]
        aircraftInfo.weight.fuselage = Wf

        if os.environ["DEBUG"].lower() == 'yes':
            print("-" * 10)
            print('Fuselage Weight and CG: ', Wf, xcgf)
            print(f'Weight/Area: {Wf / fuselageWetArea / 9.81}')
        return Wf, xcgf

    def _raymerLandingGear(W0, xCG, loadPercentage, weightFactor=0.043):
        weightLandingGear = loadPercentage * weightFactor * W0
        if os.environ["DEBUG"].lower() == 'yes':
            print("-" * 10)
            print('Landing Weight and CG: ', weightLandingGear, xCG)
        return weightLandingGear, xCG

    def _engineWeight():
        if os.environ["DEBUG"].lower() == 'yes':
            print("-" * 10)
            print('Engine Weight and CG: ', weightInfo.engine, aircraftInfo.cg.engine[0])
        return weightInfo.engine, aircraftInfo.cg.engine[0]

    def _allElseWeight():
        allElseWeight = sum([v[0] for v in weightInfo.allElse.values()])
        allElseWeightCG = sum([v[1] for v in weightInfo.allElse.values()])
        if os.environ["DEBUG"].lower() == 'yes':
            print("-" * 10)
            print('All else Weight and CG: ', allElseWeight, allElseWeightCG)
        return allElseWeight, allElseWeightCG

    methods = {
        "Raymer": [_raymerWing(),
                   _raymerStabSurfaces(horizontalArea, horizontalMeanChord, xHorizontalMeanChord, xHorizontalRoot, name='horizontal'),
                   _raymerStabSurfaces(verticalArea, verticalMeanChord, xVerticalMeanChord, xVerticalRoot,  name='vertical'),
                   _raymerFuselage(),
                   _raymerLandingGear(mtow, aircraftInfo.xNoseLG, 0.15),
                   _raymerLandingGear(mtow, aircraftInfo.xMainLG, 0.85),
                   _engineWeight(),
                   _allElseWeight()]
    }

    return [sum(i) for i in zip(*methods[method])]
