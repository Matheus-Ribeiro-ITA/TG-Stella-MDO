import matplotlib.pyplot as plt

def plotliftDistribution(aircraftInfo):
    zippedPairs = zip(aircraftInfo.yStripsWing, aircraftInfo.clStripsWing[-1])
    clStripWing = [x for _, x in sorted(zippedPairs)]
    yStripsWing = sorted(aircraftInfo.yStripsWing)

    plt.plot(yStripsWing, clStripWing)
    plt.xlabel(' Wing Span (m)')
    plt.ylabel(' cl ')
    plt.show()

    # zippedPairs = zip(aircraftInfo.yStripsHorizontal, aircraftInfo.alphaStallsHorizontal)
    # aircraftInfo.alphaStallsHorizontal = [x for _, x in sorted(zippedPairs)]
    # aircraftInfo.yStripsHorizontal = sorted(aircraftInfo.yStripsHorizontal)
    # plt.plot(aircraftInfo.yStripsHorizontal, aircraftInfo.alphaStallsHorizontal)
    # plt.xlabel(' Horizontal Span (m)')
    # plt.ylabel(' Angle of Stall (deg)')
    # # plt.ylim((10, 20))
    # plt.show()