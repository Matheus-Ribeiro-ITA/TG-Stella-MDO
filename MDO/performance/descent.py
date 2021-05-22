import numpy as np
from MDO.auxTools import atmosphere
import scipy


def descentFuel(aircraftInfo=None, heightInitial=1500, heightFinal=0, rateOfDescent=1, nSteps=20, logger=None):
    wingArea = aircraftInfo.wing.area
    weightLand = aircraftInfo.weight.empty + aircraftInfo.weight.fuelReserve
    v0 = aircraftInfo.thrust.v0
    v1 = aircraftInfo.thrust.v1
    v2 = aircraftInfo.thrust.v2
    heightSlope = aircraftInfo.thrust.slopeHeight
    cD0 = aircraftInfo.cD0
    cD1 = aircraftInfo.cD1
    cD2 = aircraftInfo.k

    heights = np.linspace(heightFinal, heightInitial, nSteps)

    def funDrag(velocity):
        cL = 2 * weight / (wingArea * velocity ** 2 * rho)
        return 1/2*rho*velocity**2*wingArea*(cD0 + cD1 * cL + cD2 * cL ** 2)

    def funThrottleRequired(velocity):
        thrustMax = (v0 + v1 * velocity + v2 * velocity ** 2) * (1 + heightSlope * height)
        return (funDrag(velocity) - rateOfDescent*weight/velocity)/thrustMax

    def rateConstraint(velocity):
        thrustMin = (v0 + v1 * velocity + v2 * velocity ** 2) * (1 + heightSlope * height)*0.1
        drag = funDrag(velocity)
        return (drag - thrustMin) * velocity / weight - rateOfDescent

    def velocityUpperConstraint(velocity):
        return 90 - velocity

    def velocityLowerConstraint(velocity):
        return velocity

    cons = [{'type': 'ineq', 'fun': rateConstraint},
            {'type': 'ineq', 'fun': velocityUpperConstraint},
            {'type': 'ineq', 'fun': velocityLowerConstraint}]

    velocityDescent = 15
    xDist = 0
    totalFuelKg = 0.0  # Weird: I declare as float but it becomes a np.array

    for i in range(len(heights)-1):
        weight = weightLand + totalFuelKg * 9.8
        height = (heights[i]+heights[i+1])/2
        T, p, rho, mi = atmosphere(height)
        r = scipy.optimize.minimize(funThrottleRequired, velocityDescent, constraints=cons)
        velocityDescent = r.x
        if not r.success:
            logger.warning(f"Descent speed convergence failed {r.fun}")
        throttle = r.fun
        time = (heights[i+1] - heights[i])/rateOfDescent
        xDist += r.x[0] * time
        fuelKgS = aircraftInfo.engine.consumptionMaxLperH*aircraftInfo.engine.fuelDensity*throttle/3600
        totalFuelKg += fuelKgS*time

    aircraftInfo.weight.fuelDescent = totalFuelKg[0]*9.8
    aircraftInfo.performance.descent.time = (heightInitial - heightFinal) / rateOfDescent
    aircraftInfo.performance.descent.range = xDist

    return

