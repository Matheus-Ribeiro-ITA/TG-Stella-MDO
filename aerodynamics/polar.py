from scipy.optimize import curve_fit

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