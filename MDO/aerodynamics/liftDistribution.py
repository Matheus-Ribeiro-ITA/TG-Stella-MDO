import matplotlib.pyplot as plt
import numpy as np
import json
import os

def plotliftDistribution(results, aircraftInfo):

    for k, v in results.items():
        if k.startswith("trimmed"):
            clNormStrips = v["StripForces"]["wing"]["c cl"]

    zippedPairs = zip(aircraftInfo.yStripsWing, aircraftInfo.clStripsWing[-1])
    clStripWing = [x for _, x in sorted(zippedPairs)]
    yStripsWing = sorted(aircraftInfo.yStripsWing)

    L0 = 0.5417
    elipticWing = [L0*np.sqrt(1 - (x/3)**2) for x in yStripsWing]


    plt.plot(yStripsWing, elipticWing)
    plt.plot(yStripsWing, clNormStrips)
    plt.plot(yStripsWing, clStripWing)
    plt.xlabel(' Wing Span (m)')
    plt.ylabel(' cl ')
    plt.show()

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


def liftDistNewton(results, mission):
    T, p, rho, mi = _atmosphere(mission["cruise"]["altitude"])

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
