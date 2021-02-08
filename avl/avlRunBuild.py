import json
from math import radians, sqrt, tan
import avl.avlwrapper as avl
import time
import numpy as np


def _atmosphere(z, tba=288.15):
    """
     - Description:
         Funçao que retorna a Temperatura, Pressao e Densidade para uma determinada
    altitude z [m]. Essa funçao usa o modelo padrao de atmosfera para a
    temperatura no solo de Tba.

    -Inputs:
        z [float]: Altitude in meters.
        Tba [float]:

    - Outputs:
        T [float]: Temperature in kelvins.
        p [float]: Pressure in Pascals.
        rho [float]: Density in kg/m^3.
        mi [float]: Viscosity in .
    """

    # Zbase (so para referencia)
    # 0 11019.1 20063.1 32161.9 47350.1 50396.4

    # DEFINING CONSTANTS
    # Earth radius
    r = 6356766
    # gravity
    g0 = 9.80665
    # air gas constant
    R = 287.05287
    # layer boundaries
    Ht = [0, 11000, 20000, 32000, 47000, 50000]
    # temperature slope in each layer
    A = [-6.5e-3, 0, 1e-3, 2.8e-3, 0]
    # pressure at the base of each layer
    pb = [101325, 22632, 5474.87, 868.014, 110.906]
    # temperature at the base of each layer
    Tstdb = [288.15, 216.65, 216.65, 228.65, 270.65];
    # temperature correction
    Tb = tba - Tstdb[0]
    # air viscosity
    mi0 = 18.27e-6  # [Pa s]
    T0 = 291.15  # [K]
    C = 120  # [K]

    # geopotential altitude
    H = r * z / (r + z)

    # selecting layer
    if H < Ht[0]:
        raise ValueError('Under sealevel')
    elif H <= Ht[1]:
        i = 0
    elif H <= Ht[2]:
        i = 1
    elif H <= Ht[3]:
        i = 2
    elif H <= Ht[4]:
        i = 3
    elif H <= Ht[5]:
        i = 4
    else:
        raise ValueError('Altitude beyond model boundaries')

    # Calculating temperature
    T = Tstdb[i] + A[i] * (H - Ht[i]) + Tb

    # Calculating pressure
    if A[i] == 0:
        p = pb[i] * np.exp(-g0 * (H - Ht[i]) / R / (Tstdb[i] + Tb))
    else:
        p = pb[i] * (T / (Tstdb[i] + Tb)) ** (-g0 / A[i] / R)

    # Calculating density
    rho = p / R / T

    # Calculating viscosity with Sutherland's Formula
    mi = mi0 * (T0 + C) / (T + C) * (T / T0) ** (1.5)

    return T, p, rho, mi


def avlRunBuild(mission, aircraftInfo):
    """
    # Description:
        Build cases to run on AVL.

    ## Parameters (Required):
    - mission [dict]: Conditions for AVL cases. Ex: mission["cruize"]["altitude"].
    - aircraftInfo [class object]: Info about the aircraft. Ex: aircraftInfo.mass.

    ## Returns:
    - cases [list(dict)]: Cases to run on AVL.
    """
    g = 9.81
    mass = aircraftInfo.mass
    wingArea = aircraftInfo.wingArea
    meanChord = aircraftInfo.meanChord
    cLMax = aircraftInfo.cLMax
    cases = []
    if "cruize" in mission:
        T, p, rho, mi = _atmosphere(mission["cruize"]["altitude"])
        vCruise = mission["cruize"]["vCruise"]

        cl = 2 * mass*g / (rho * vCruise ** 2 * wingArea)
        clParam = avl.Parameter(name='alpha', setting='CL', value=cl)
        trimParam = avl.Parameter(name='elevator', setting='Cm', value=0.0)

        cases.append(avl.Case(name='trimmed',
                              alpha=clParam,
                              elevator=trimParam))

    if "roll" in mission:
        # AVL good in: -0.10 < pb/2V < 0.10
        T, p, rho, mi = _atmosphere(mission["roll"]["altitude"])
        vCruise = mission["roll"]["vCruise"]
        cl = 2 * mass*g / (rho * vCruise ** 2 * wingArea)
        clParam = avl.Parameter(name='alpha', setting='CL', value=cl)
        rParam = avl.Parameter(name='roll_rate', setting='pb/2V', value=mission["roll"]["rollRate"])
        trimParam = avl.Parameter(name='aileron', setting='Cl', value=0.0)
        cases.append(avl.Case(name='rollRate',
                              alpha=clParam,
                              roll_rate=rParam,
                              elevator=trimParam))

    if "dive" in mission:
        #AVL good in: -0.03 < qc/2V < 0.03
        T, p, rho, mi = _atmosphere(mission["dive"]["altitude"])
        loadFactor = mission["dive"]["loadFactor"]
        cLDive = aircraftInfo.cLMax
        vDive = np.sqrt(2 * mass * g * (loadFactor + 1) / (rho * cLDive * wingArea))
        q = g*loadFactor/vDive
        qc2v = q*meanChord/(2*vDive)

        clParam = avl.Parameter(name='alpha', setting='CL', value=cLDive)
        qParam = avl.Parameter(name='pitch_rate', setting='qc/2V', value=qc2v)
        trimParam = avl.Parameter(name='elevator', setting='Cm', value=0.0)
        cases.append(avl.Case(name='dive',
                              alpha=clParam,
                              roll_rate=qParam,
                              elevator=trimParam))
        # ----------------------

    return cases
