
def getNeutralPoint(results, aircraftInfo):

    for k, v in results.items():
        if k.startswith("trimmed"):
            aircraftInfo.xNeutralPoint = v["StabilityDerivatives"]["Xnp"]
            aircraftInfo.staticMargin = 100*(aircraftInfo.xNeutralPoint - aircraftInfo.cgCalc)/aircraftInfo.meanChord
