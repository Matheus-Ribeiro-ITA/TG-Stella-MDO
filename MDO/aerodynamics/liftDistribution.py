import matplotlib.pyplot as plt

def plotliftDistribution(aircraftInfo):
    zippedPairs = zip(aircraftInfo.yStripsWing, aircraftInfo.clStripsWing[-1])
    clStripWing = [x for _, x in sorted(zippedPairs)]
    yStripsWing = sorted(aircraftInfo.yStripsWing)

    plt.plot(yStripsWing, clStripWing)
    plt.xlabel(' Wing Span (m)')
    plt.ylabel(' cl ')
    plt.show()

    # zippedPairs = zip(aircraftInfo.yStripsHorizontal, aircraftInfo.clStripsHorizontal[-1])
    # clStripHorizontal = [x for _, x in sorted(zippedPairs)]
    # yStripsHorizontal = sorted(aircraftInfo.yStripsHorizontal)
    #
    # plt.plot(yStripsHorizontal, clStripHorizontal)
    # plt.xlabel(' Horizontal Span (m)')
    # plt.ylabel(' cl ')
    # plt.show()
