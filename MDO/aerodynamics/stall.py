import matplotlib.pyplot as plt


def stall(results, aircraftInfo):
    """
    # Description:
        Get from avl Results the 3 CLs and CDs and build the polar: CD0 and K.

    ## Parameters:
    - results [dict]:

    ## Returns:
    - cD0 [float]:
    - k [float]:
    """
    aoa = []
    clStrips = []
    clStripsSlope = []

    clMax = aircraftInfo.cLMaxWingAirfoil

    for k, v in results.items():
        if k.startswith("Polar"):
            aoa.append(v["Totals"]["Alpha"])
            clStrips.append(v["StripForces"]["wing"]["cl"])
            yStrips = v["StripForces"]["wing"]["Yle"]

    for i in range(len(clStrips)-1):
        clStripsSlope.append([(a - b)/(aoa[i+1]-aoa[i]) for a, b in zip(clStrips[i+1], clStrips[i])])

    alphaStalls = []
    for i in range(len(clStripsSlope)):
        diffAlphas = [(clMax - cl)/clSlope for cl, clSlope in zip(clStrips[i], clStripsSlope[i])]
        alphaStalls.append([aoa[i] + diffAlpha for diffAlpha in diffAlphas])

    aircraftInfo.yStrips = yStrips
    aircraftInfo.alphaStalls = alphaStalls
    aircraftInfo.alphaStall = min(alphaStalls[0])
    aircraftInfo.stallPosition = yStrips[alphaStalls[0].index(aircraftInfo.alphaStall)]


def plotStall(aircraftInfo):
    zippedPairs = zip(aircraftInfo.yStrips, aircraftInfo.alphaStalls[0])
    aircraftInfo.alphaStalls[0] = [x for _, x in sorted(zippedPairs)]
    aircraftInfo.yStrips = sorted(aircraftInfo.yStrips)

    plt.plot(aircraftInfo.yStrips, aircraftInfo.alphaStalls[0])
    plt.xlabel(' Wing Span (m)')
    plt.ylabel(' Angle of Stall (deg)')
    plt.ylim((10, 20))
    plt.show()

