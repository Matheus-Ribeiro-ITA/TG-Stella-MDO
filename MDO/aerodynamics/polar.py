from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

def polar(results):
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

    popt, _ = curve_fit(_objective, cLs, cDs)
    cD0, k = popt
    return cD0, k


def _objective(x, cD0, k):
    return cD0 + k*x**2


def plotPolar(aircraftInfo):
    t = np.linspace(-1.5, 1.5, 20, endpoint=True)

    # Plot the square wave signal
    plt.plot(aircraftInfo.k*t**2 + aircraftInfo.cD0, t)
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