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

    clMaxWing = aircraftInfo.cLMaxWingAirfoil
    aoaWing, clStripsWing, yStripsWing = _getStrips(results, surface="wing")
    alphaStallsWing = _slopAproximation(aoaWing, clStripsWing, clMaxWing)
    _updateAircraftInfo(aircraftInfo, yStripsWing, alphaStallsWing, clStripsWing, surface="Wing")

    clMaxHorizontal = aircraftInfo.cLMaxHorizontalAirfoil
    aoaHorizontal, clStripsHorizontal, yStripsHorizontal = _getStrips(results, surface="horizontal")
    alphaStallsHorizontal = _slopAproximation(aoaHorizontal, clStripsHorizontal, clMaxHorizontal)
    _updateAircraftInfo(aircraftInfo, yStripsHorizontal, alphaStallsHorizontal, clStripsHorizontal, surface="Horizontal")


def plotStall(aircraftInfo):
    zippedPairs = zip(aircraftInfo.yStripsWing, aircraftInfo.alphaStallsWing)
    alphaStallsWing = [x for _, x in sorted(zippedPairs)]
    yStripsWing = sorted(aircraftInfo.yStripsWing)
    plt.plot(yStripsWing, alphaStallsWing)
    plt.xlabel(' Wing Span (m)')
    plt.ylabel(' Angle of Stall (deg)')
    plt.ylim((10, 20))
    plt.show()

    # zippedPairs = zip(aircraftInfo.yStripsHorizontal, aircraftInfo.alphaStallsHorizontal)
    # alphaStallsHorizontal = [x for _, x in sorted(zippedPairs)]
    # yStripsHorizontal = sorted(aircraftInfo.yStripsHorizontal)
    # plt.plot(yStripsHorizontal, alphaStallsHorizontal)
    # plt.xlabel(' Horizontal Span (m)')
    # plt.ylabel(' Angle of Stall (deg)')
    # # plt.ylim((10, 20))
    # plt.show()
    
    

def _slopAproximation(aoa, clStrips, clMax):
    
    # Remember: that we have 3 polar points.
    clStripsSlope = [(a - b)/(aoa[2]-aoa[1]) for a, b in zip(clStrips[2], clStrips[1])]
    
    diffAlphas = [(clMax - cl)/clSlope for cl, clSlope in zip(clStrips[1], clStripsSlope)]
    alphaStalls = [aoa[1] + diffAlpha for diffAlpha in diffAlphas]
    
    return alphaStalls


def _getStrips(results, surface="wing"):
    aoa = []
    clStrips = []

    for k, v in results.items():
        if k.startswith("Polar"):
            aoa.append(v["Totals"]["Alpha"])
            clStrips.append(v["StripForces"][surface]["cl"])
            yStrips = v["StripForces"][surface]["Yle"]
    return aoa, clStrips, yStrips


def _updateAircraftInfo(aircraftInfo, yStrips, alphaStalls, clStrips, surface="Wing"):
    exec(f"aircraftInfo.yStrips{surface} = yStrips")
    exec(f"aircraftInfo.alphaStalls{surface} = alphaStalls")
    exec(f"aircraftInfo.alphaStall{surface} = min(alphaStalls)")
    exec(f"aircraftInfo.clStrips{surface} = clStrips")
    exec(f"aircraftInfo.stallPosition{surface} = yStrips[alphaStalls.index(aircraftInfo.alphaStall{surface})]")