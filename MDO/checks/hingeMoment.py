def getHingeMoment(results, aircraftInfo):
    """
    # Description:
        Get values for HingeMoment condition normalized per dynamic pressure.

    ## Parameters:
    - results [dict]:
    - aircraftInfo [Object]:

    ## Returns:
    - momentPerPressure [list]:
    """
    cFlap = results['hingeMoment']["HingeMoments"]["flap"]
    cAileron = results['hingeMoment']["HingeMoments"]["aileron"]
    cElevator = results['hingeMoment']["HingeMoments"]["elevator"]

    areaWing = aircraftInfo.wingArea
    meanChord = aircraftInfo.meanChord

    momentPerPressure = [c*areaWing*meanChord for c in [cAileron, cFlap, cElevator]]
    return momentPerPressure
