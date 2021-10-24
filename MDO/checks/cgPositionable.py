
def cgPositionable(aircraftInfo):
    """
    Function to check if is possible to position the CG.

    Moves the internal weight of the fuselage and the fuselage
    it self to put the Center of Gravity on the correct Static Margin
    """

    allElseCG = (aircraftInfo.cg.calc*aircraftInfo.weight.MTOW - (
    aircraftInfo.cg.wing[0]*aircraftInfo.weight.wing +
    aircraftInfo.cg.fuselage[0]*aircraftInfo.weight.fuselage +
    # aircraftInfo.cg.horizontal[0]*aircraftInfo.weight.horizontal +  # TODO: ADD V case
    aircraftInfo.cg.vertical[0]*aircraftInfo.weight.vertical)) / aircraftInfo.weight.allElse['All'][0]

    allElseCgPercentFuselage = (allElseCG/aircraftInfo.fuselage.length)*100

    secure_factor = 80

    passed = False

    if -secure_factor < allElseCgPercentFuselage < secure_factor:
        passed = True

    return passed, allElseCgPercentFuselage
