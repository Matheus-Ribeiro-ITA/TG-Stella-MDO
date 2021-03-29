import avl as avlW
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
    weight = aircraftInfo.weight.MTOW
    wingArea = aircraftInfo.wing.area
    meanChord = aircraftInfo.wing.meanChord
    # cLMax = aircraftInfo.cLMax
    cases = []
    if "cruise" in mission:
        T, p, rho, mi = _atmosphere(mission["cruise"]["altitude"])
        vCruise = mission["cruise"]["vCruise"]
        aircraftInfo.cLCruise = 2 * weight / (rho * vCruise ** 2 * wingArea)
        clParam = avlW.Parameter(name='alpha', setting='CL', value=aircraftInfo.cLCruise)
        trimParam = avlW.Parameter(name='elevator', setting='Cm', value=0.0)
        cases.append(avlW.Case(name='trimmed',
                               alpha=clParam,
                               elevator=trimParam,
                               X_cg=aircraftInfo.cgCalc))

    if "roll" in mission:
        # AVL good in: -0.10 < pb/2V < 0.10
        T, p, rho, mi = _atmosphere(mission["roll"]["altitude"])
        vCruise = mission["roll"]["vCruise"]
        cl = 2 * weight / (rho * vCruise ** 2 * wingArea)
        clParam = avlW.Parameter(name='alpha', setting='CL', value=cl)
        rParam = avlW.Parameter(name='roll_rate', setting='pb/2V', value=mission["roll"]["rollRate"])
        trimParam = avlW.Parameter(name='aileron', setting='Cl', value=0.0)
        cases.append(avlW.Case(name='rollRate',
                               alpha=clParam,
                               roll_rate=rParam,
                               elevator=trimParam))

    if "dive" in mission:
        #AVL good in: -0.03 < qc/2V < 0.03
        T, p, rho, mi = _atmosphere(mission["dive"]["altitude"])
        loadFactor = mission["dive"]["loadFactor"]
        cLDive = aircraftInfo.cLMax
        vDive = np.sqrt(2 * weight * (loadFactor + 1) / (rho * cLDive * wingArea))
        q = g*loadFactor/vDive
        qc2v = q*meanChord/(2*vDive)

        clParam = avlW.Parameter(name='alpha', setting='CL', value=cLDive)
        qParam = avlW.Parameter(name='pitch_rate', setting='qc/2V', value=qc2v)
        trimParam = avlW.Parameter(name='elevator', setting='Cm', value=0.0)
        cases.append(avlW.Case(name='dive',
                               alpha=clParam,
                               roll_rate=qParam,
                               elevator=trimParam))

    if "polar" in mission:
        for i, cL in enumerate(mission["polar"]["cLPoints"]):
            clParam = avlW.Parameter(name='alpha', setting='CL', value=cL)
            trimParam = avlW.Parameter(name='elevator', setting='Cm', value=0.0)
            cases.append(avlW.Case(name="PolarTrimmed_" + str(i),
                                   alpha=clParam,
                                   elevator=trimParam))

    if "untrimmed_polar" in mission:
        for i, cL in enumerate(mission["untrimmed_polar"]["cLPoints"]):
            clParam = avlW.Parameter(name='alpha', setting='CL', value=cL)
            # trimParam = avl.Parameter(name='elevator', setting='Cm', value=0.0)
            cases.append(avlW.Case(name="PolarUntrimmed_" + str(i),
                                   alpha=clParam))

    if "takeOffRun" in mission:
        alphaParam = avlW.Parameter(name='alpha', setting='alpha', value=mission['takeOffRun']['alpha'])
        flapParam = avlW.Parameter(name='flap', setting='flap', value=mission['takeOffRun']['flap'])
        if "aileron" in mission['takeOffRun']:
            aileronParam = avlW.Parameter(name='aileron', setting='aileron', value=mission['takeOffRun']['aileron'])
        else:
            aileronParam = avlW.Parameter(name='aileron', setting='aileron', value=0)
        cases.append(avlW.Case(name="TakeOffRun",
                               alpha=alphaParam,
                               flap=flapParam,
                               aileorn=aileronParam))
    if "hingeMoment" in mission:
        alphaParam = avlW.Parameter(name='alpha', setting='alpha', value=mission['hingeMoment']['alpha'])
        flapParam = avlW.Parameter(name='flap', setting='flap', value=mission['hingeMoment']['flap'])
        aileronParam = avlW.Parameter(name='aileron', setting='aileron', value=mission['hingeMoment']['aileron'])
        elevatorParam = avlW.Parameter(name='elevator', setting='elevator', value=mission['hingeMoment']['elevator'])
        cases.append(avlW.Case(name="hingeMoment",
                               alpha=alphaParam,
                               flap=flapParam,
                               aileorn=aileronParam,
                               elevator=elevatorParam))

    return cases
