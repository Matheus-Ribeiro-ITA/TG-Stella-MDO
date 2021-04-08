from MDO.auxTools import atmosphere
import numpy as np
import scipy

import sys
import matplotlib.pyplot as plt


def climbFuel(aircraftInfo=None, heightInitial=0, heightFinal=1500, rateOfClimb=1, nSteps=20, logger=None):

    wingArea = aircraftInfo.wing.area
    weightTakeOff = aircraftInfo.weight.empty + aircraftInfo.weight.fuel - aircraftInfo.weight.fuelTakeOff
    v0 = aircraftInfo.thrust.v0
    v1 = aircraftInfo.thrust.v1
    v2 = aircraftInfo.thrust.v2
    heightSlope = aircraftInfo.thrust.slopeHeight
    cD0 = aircraftInfo.cD0
    cD1 = aircraftInfo.cD1
    cD2 = aircraftInfo.k

    heights = np.linspace(heightInitial, heightFinal, nSteps)

    def funDrag(velocity):
        cL = 2 * weight / (wingArea * velocity ** 2 * rho)
        return 1/2*rho*velocity**2*wingArea*(cD0 + cD1 * cL + cD2 * cL ** 2)

    def funThrottleRequired(velocity):
        thrustMax = (v0 + v1 * velocity + v2 * velocity ** 2) * (1 + heightSlope * height)
        return (funDrag(velocity) + rateOfClimb*weight/velocity)/thrustMax

    def rateConstraint(velocity):
        thrustMax = (v0 + v1 * velocity + v2 * velocity ** 2) * (1 + heightSlope * height)
        drag = funDrag(velocity)
        return (thrustMax - drag) * velocity / weight - rateOfClimb

    def velocityUpperConstraint(velocity):
        return 90 - velocity

    def velocityLowerConstraint(velocity):
        return velocity

    cons = [{'type': 'ineq', 'fun': rateConstraint},
            {'type': 'ineq', 'fun': velocityUpperConstraint},
            {'type': 'ineq', 'fun': velocityLowerConstraint}]

    velocityClimb = 30
    xDist = 0
    totalFuelKg = 0.0  # Weird: I declare as float but it becomes a np.array
    for i in range(len(heights)-1):
        weight = weightTakeOff - totalFuelKg * 9.8
        height = (heights[i]+heights[i+1])/2
        T, p, rho, mi = atmosphere(height)
        r = scipy.optimize.minimize(funThrottleRequired,
                                    velocityClimb,
                                    constraints=cons,
                                    tol=1e-2)
        if not r.success:
            logger.warning(f"Climb speed convergence failed {r.fun}")
            print(r)
            vs = np.linspace(20, 50, 20)
            drags = [funDrag(v) for v in vs]
            thrustMax = [(v0 + v1 * v + v2 * v ** 2) * (1 + heightSlope * height) for v in vs]
            rateDrag = [rateOfClimb * weight / v for v in vs]
            totalDrag = [d+r for d, r in zip(drags, rateDrag)]
            print(height)
            plt.plot(vs, drags, label='Drag')
            plt.plot(vs, rateDrag, label='Rate Drag')
            plt.plot(vs, thrustMax, label='Thrust')
            plt.plot(vs, totalDrag, label='Total Drag')
            plt.legend()
            plt.grid()
            plt.savefig('aa.png')
            plt.show()

            cls = [2 * weight / (wingArea * v ** 2 * rho) for v in vs]
            plt.plot(vs, cls, label='CL')
            plt.legend()
            plt.grid()
            plt.show()

            aircraftInfo.weight.fuelClimb = 5*9.8
            aircraftInfo.performance.climb.range = 0
            return
            # sys.exit("aa! errors!")

        velocityClimb = r.x
        throttle = r.fun
        time = (heights[i+1] - heights[i])/rateOfClimb
        xDist += r.x[0]*time
        fuelKgS = aircraftInfo.engine.consumptionMaxLperH*aircraftInfo.engine.fuelDensity*throttle/3600
        totalFuelKg += fuelKgS*time

    aircraftInfo.weight.fuelClimb = totalFuelKg*9.8
    aircraftInfo.performance.climb.time = (heightFinal-heightInitial)/rateOfClimb
    aircraftInfo.performance.climb.range = xDist
    return






