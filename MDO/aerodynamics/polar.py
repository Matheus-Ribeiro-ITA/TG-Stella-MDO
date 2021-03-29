from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt


def polar(results, aircraftInfo):
    """
    # Description:
        Get from avl Results the 3 CLs and CDs and build the polar: CD0 and K.

    ## Parameters:
    - results [dict]:

    ## Returns:
    - cD0 [float]:
    - k [float]:
    """
    cLs = []
    cDs = []

    for k, v in results.items():
        if k.startswith("Polar"):
            cLs.append(v["Totals"]["CLtot"])
            cDs.append(v["Totals"]["CDtot"])

    if not cLs:
        raise Exception("polar.py can't find CLs")

    cDParasite = _parasiteDrag(aircraftInfo)

    cDs = [cD + cDParasite for cD in cDs]
    popt, _ = curve_fit(_objective, cLs, cDs)
    dataPolar = [cLs, cDs]
    cD0, cD1, k = popt
    return [cD0, cD1, k, dataPolar]


def _parasiteDrag(aircraftInfo):
    wingArea = aircraftInfo.wing.area

    def _fuselageDrag():
        interferenceFactor = aircraftInfo.fuselage.interferenceFactor
        coefficientFriction = aircraftInfo.fuselage.coefficientFriction
        finenessRatio = aircraftInfo.fuselage.finenessRatio
        surfaceWet = aircraftInfo.fuselage.wetArea

        return interferenceFactor * coefficientFriction * \
               (1 + 60 / (finenessRatio ** 3) + 0.0025 * finenessRatio) * surfaceWet / wingArea

    def _sphereDrag():
        sphereDragCoefficient = 0.15  # Cf= 0.15 for Re> 4.10^5 and 0.41 for bellow
        frontalArea = aircraftInfo.fuselage.gimbalFrontalArea
        return sphereDragCoefficient*frontalArea/wingArea

    return _fuselageDrag() + _sphereDrag() + 0.03


def plotPolar(aircraftInfo):
    t = np.linspace(-1.5, 1.5, 20, endpoint=True)

    # Plot the square wave signal
    plt.plot(aircraftInfo.k * t ** 2 + aircraftInfo.cD0 + aircraftInfo.cD1 * t, t)
    plt.scatter(aircraftInfo.dataPolar[1], aircraftInfo.dataPolar[0], color="k")
    # x axis label for the square wave plot
    plt.xlabel('CD')

    # y axis label for the square wave plot
    plt.ylabel('CL')
    plt.grid(True, which='both')

    # Provide x axis and line color
    plt.axhline(y=0, color='k')

    # Set the max and min values for y axis
    plt.ylim(-1.2, 1.2)

    # Display the square wave
    plt.show()


def _objective(x, cD0, cD1, k):
    return cD0 + cD1 * x + k * x ** 2


def getRun(results, aircraftInfo):
    """
    # Description:
        Get values for takeoff Run.

    ## Parameters:
    - results [dict]:

    ## Returns:
    - cD0 [float]:
    - k [float]:
    """
    cLRun = results['TakeOffRun']["Totals"]["CLtot"]
    cDRunAvl = results['TakeOffRun']["Totals"]["CDtot"]

    cDParasite = _parasiteDrag(aircraftInfo)

    cDAvlTotal = cDRunAvl + cDParasite
    return [cDRunAvl, cDParasite, cDAvlTotal, cLRun]
