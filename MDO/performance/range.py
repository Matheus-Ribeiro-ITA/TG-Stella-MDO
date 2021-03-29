import numpy as np


def rangeCruise(engineFC, mission, aircraftInfo):
    mf = 1.0
    mfFinal = aircraftInfo.weight.empty/aircraftInfo.weight.MTOW
    cLCruise = aircraftInfo.cLCruise
    cD0Cruise = aircraftInfo.cD0
    kCruise = aircraftInfo.k
    loiterTimer = aircraftInfo.loiterTime
    fuelFrac = engineFC["fuelFrac"]
    cCruise = engineFC["cCruise"]
    vCruise = mission["cruise"]["vCruise"]

    mfCruise = mf*fuelFrac["engineValue"]*fuelFrac["taxi"]*fuelFrac["takeOff"]*fuelFrac["climb"]

    def ffLoiter():
        liftToDrag = 1 / (2 * np.sqrt(cD0Cruise * kCruise))
        cLoiter = 0.8 * cCruise
        ffLoiter = np.exp(-loiterTimer * cLoiter / liftToDrag)  # fuel fraction brequet equation
        return ffLoiter

    ffLoiter = ffLoiter()
    ffCruise = mfFinal / (mfCruise * fuelFrac["descent"] * fuelFrac["landing"]*ffLoiter)
    cD = cD0Cruise + kCruise*cLCruise**2
    rangeCruise = np.log(ffCruise)*vCruise*cLCruise/(cCruise*cD)# fuel fraction brequet equation

    return rangeCruise

