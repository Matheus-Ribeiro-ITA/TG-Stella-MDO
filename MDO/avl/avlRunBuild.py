import avl as avlW
import numpy as np
from MDO.auxTools import atmosphere


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
        T, p, rho, mi = atmosphere(mission["cruise"]["altitude"])
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
        T, p, rho, mi = atmosphere(mission["roll"]["altitude"])
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
