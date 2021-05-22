import matplotlib.pyplot as plt
import numpy as np
import json
import os
from MDO.auxTools import atmosphere


def plotliftDistribution(results, aircraftInfo, avlCases=None):

    T, p, rho, mi = atmosphere(avlCases["cruise"]["altitude"])
    for k, v in results.items():
        if k.startswith("trimmed"):
            clNormStrips = v["StripForces"]["wing"]["c cl"]

    zippedPairs = zip(aircraftInfo.yStripsWing, aircraftInfo.clStripsWing[-1])
    clStripWing = [x for _, x in sorted(zippedPairs)]
    yStripsWing = sorted(aircraftInfo.yStripsWing)

    L0 = aircraftInfo.weight.MTOW*4/(np.pi*rho*avlCases['cruise']['vCruise']*aircraftInfo.wing.span)  # TODO
    elipticWing = [L0*np.sqrt(1 - (2*x/aircraftInfo.wing.span)**2) for x in yStripsWing]


    plt.plot(yStripsWing, elipticWing, label='Elliptical Wing')
    plt.plot(yStripsWing, clNormStrips, label='CL norm')
    plt.plot(yStripsWing, clStripWing, label='CL')
    plt.xlabel(' Wing Span (m)')
    plt.ylabel(' cl ')
    plt.show()


def liftDistNewton(results, mission):
    T, p, rho, mi = atmosphere(mission["cruise"]["altitude"])

    for k, v in results.items():
        if k.startswith("trimmed"):
            clStrips = v["StripForces"]["wing"]["cl"]
            yStrips = v["StripForces"]["wing"]["Yle"]
            areaStrips = v["StripForces"]["wing"]["Area"]

    forceStrips = [1/2*rho*area*cl*mission['cruise']['vCruise']**2 for area, cl in zip(areaStrips, clStrips)]
    aJson = {
        "spanSemiWing": yStrips,
        "areaStrips": areaStrips,
        "clStrips": clStrips,
        "forceStrips": forceStrips
    }
    if 'y' in os.getenv("DEBUG"):
        with open("aircraft/liftDistribution.json", "w", encoding="utf-8") as file:
            json.dump(aJson, file, indent=4)
            file.close()
    # zippedPairs = zip(aircraftInfo.yStripsHorizontal, aircraftInfo.clStripsHorizontal[-1])
    # clStripHorizontal = [x for _, x in sorted(zippedPairs)]
    # yStripsHorizontal = sorted(aircraftInfo.yStripsHorizontal)
    #
    # plt.plot(yStripsHorizontal, clStripHorizontal)
    # plt.xlabel(' Horizontal Span (m)')
    # plt.ylabel(' cl ')
    # plt.show()
