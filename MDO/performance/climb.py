from MDO.auxTools import atmosphere
import numpy as np
import scipy
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
        thrustMax = (v0 + v1 * velocity + v2 * velocity ** 2) * (1 + heightSlope * heights[i])
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

    velocityClimb = 25
    xDist = 0
    totalFuelKg = 0.0  # Weird: I declare as float but it becomes a np.array
    for i in range(len(heights)-1):
        weight = weightTakeOff - totalFuelKg * 9.8
        height = (heights[i]+heights[i+1])/2
        T, p, rho, mi = atmosphere(height)
        r = scipy.optimize.minimize(funThrottleRequired, velocityClimb, constraints=cons)
        if not r.success:
            logger.warning(f"Descent speed convergence failed")
        velocityClimb = r.x
        # thrustRequired = r.fun + rateOfClimb*mtow/velocityClimb
        # thrustMax = (v0 + v1 * velocityClimb + v2 * velocityClimb ** 2) * (1 + heightSlope * heights[i])
        # throttle = thrustRequired/thrustMax
        throttle = r.fun
        time = (heights[i+1] - heights[i])/rateOfClimb
        xDist += r.x[0]*time
        fuelKgS = aircraftInfo.engine.consumptionMaxLperH*aircraftInfo.engine.fuelDensity*throttle/3600
        totalFuelKg += fuelKgS*time

        # print(f"Altitude {height}")
        # print(f"Velocity {r.x}")
        # print(f"Fun {r.fun}")
        # print(f"Drag {drag}")
        # print("Time: ", time)
        # print("Total Fuel: ", totalFuel, " kg")
        # print("")

    aircraftInfo.weight.fuelClimb = totalFuelKg[0]*9.8
    aircraftInfo.performance.climb.time = (heightFinal-heightInitial)/rateOfClimb
    aircraftInfo.performance.climb.range = xDist
    return


    # plt.scatter(velocities, heights)
    # plt.xlim([0, 100])
    # plt.show()





