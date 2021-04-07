from MDO.auxTools import atmosphere
import numpy as np


def cruise(aircraftInfo=None, avlCases=None, fuelKg=None, fuelDescentKg=None, nSteps=10, logger=None):
    wingArea = aircraftInfo.wing.area
    emptyWeight = aircraftInfo.weight.empty
    v0 = aircraftInfo.thrust.v0
    v1 = aircraftInfo.thrust.v1
    v2 = aircraftInfo.thrust.v2
    velocityCruise = avlCases['cruise']['vCruise']
    heightSlope = aircraftInfo.thrust.slopeHeight
    heightCruise = avlCases['cruise']['altitude']
    cD0 = aircraftInfo.cD0
    cD1 = aircraftInfo.cD1
    cD2 = aircraftInfo.k

    if not fuelKg:
        fuelKg = aircraftInfo.Weight.fuelActual/9.8
    if not fuelDescentKg:
        fuelDescentKg = aircraftInfo.Weight.fuelLanding / 9.8

    T, p, rho, mi = atmosphere(heightCruise)

    fuelKgArray = np.linspace(fuelKg, fuelDescentKg, nSteps)
    totalTime = 0
    rangeCruise = 0
    aircraftInfo.performance.cruise.cL = []
    aircraftInfo.performance.cruise.cD = []
    for i in range(len(fuelKgArray)-1):
        fuelKg = (fuelKgArray[i]+fuelKgArray[i+1])/2
        aircraftWeight = emptyWeight + fuelKg*9.8
        cL = 2 * aircraftWeight / (wingArea * velocityCruise ** 2 * rho)
        aircraftInfo.performance.cruise.cL.append(cL)
        cD = cD0 + cD1 * cL + cD2 * cL ** 2
        aircraftInfo.performance.cruise.cD.append(cD0 + cD1 * cL + cD2 * cL ** 2)
        aircraftInfo.dragCruise = 1 / 2 * rho * cD * velocityCruise ** 2 * aircraftInfo.wing.area
        thrust = (v0 + v1 * velocityCruise + v2 * velocityCruise ** 2) * (1 + heightSlope * heightCruise)
        throttle = aircraftInfo.dragCruise / thrust
        fuelKgS = aircraftInfo.engine.consumptionMaxLperH * aircraftInfo.engine.fuelDensity * throttle / 3600
        time = (fuelKgArray[i]-fuelKgArray[i+1])/fuelKgS
        totalTime += time
        rangeCruise += velocityCruise*time

    aircraftInfo.performance.cruise.time = totalTime
    aircraftInfo.performance.cruise.range = rangeCruise
    return
