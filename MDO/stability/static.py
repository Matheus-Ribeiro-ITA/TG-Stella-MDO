
def getNeutralPoint(results, aircraftInfo):

    neutralPoint = []
    for k, v in results.items():
        # if k.startswith("trimmed"):
        #     aircraftInfo.xNeutralPoint = v["StabilityDerivatives"]["Xnp"]

        if k.startswith("PolarTrimmed"):
            neutralPoint.append(v["StabilityDerivatives"]["Xnp"])

    aircraftInfo.xNeutralPoint = sum(neutralPoint)/len(neutralPoint)

    aircraftInfo.staticMargin = 100*(aircraftInfo.xNeutralPoint - aircraftInfo.cg.calc)/aircraftInfo.wing.meanChord
