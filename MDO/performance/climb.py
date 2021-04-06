from MDO.auxTools import atmosphere
import numpy as np
import scipy
import matplotlib.pyplot as plt


def climbFuel(aircraftInfo=None, heightInitial=0, heightFinal=1500, rateOfClimb=1, nSteps=20):

    wingArea = aircraftInfo.wing.area
    mtow = aircraftInfo.weight.MTOW
    v0 = aircraftInfo.thrust.v0
    v1 = aircraftInfo.thrust.v1
    v2 = aircraftInfo.thrust.v2
    heightSlope = aircraftInfo.thrust.slopeHeight
    cD0 = aircraftInfo.cD0
    cD1 = aircraftInfo.cD1
    cD2 = aircraftInfo.k

    heights = np.linspace(heightInitial, heightFinal, nSteps)

    def funDrag(velocity):
        cL = 2 * mtow / (wingArea * velocity ** 2 * rho)
        return 1/2*rho*velocity**2*wingArea*(cD0 + cD1 * cL + cD2 * cL ** 2)

    def rateConstraint(velocity):
        thrust = (v0 + v1 * velocity + v2 * velocity ** 2) * (1 + heightSlope * height)
        drag = funDrag(velocity)
        return (thrust - drag) * velocity / mtow - rateOfClimb

    def velocityUpperConstraint(velocity):
        return 90 - velocity

    def velocityLowerConstraint(velocity):
        return velocity

    cons = [{'type': 'ineq', 'fun': rateConstraint},
            {'type': 'ineq', 'fun': velocityUpperConstraint},
            {'type': 'ineq', 'fun': velocityLowerConstraint}]

    velocityClimb = 15
    velocities = []
    totalFuel = 0
    for i in range(len(heights)-1):
        height = heights[i]
        T, p, rho, mi = atmosphere(heights[i])
        r = scipy.optimize.minimize(funDrag, velocityClimb, constraints=cons)
        velocityClimb = r.x
        velocities.append(velocityClimb)
        drag = r.fun
        thrust = (v0 + v1 * velocityClimb + v2 * velocityClimb ** 2) * (1 + heightSlope * heights[i])
        # pw = 2*thrust*vGuess/(1 + heightSlope * height)
        throttle = drag/thrust
        time = (heights[i+1] - heights[i])/rateOfClimb
        fuelKgS = aircraftInfo.engine.consumptionMaxLperH*aircraftInfo.engine.fuelDensity*throttle/3600
        totalFuel += fuelKgS*time

        # print(f"Altitude {height}")
        # print(f"Velocity {r.x}")
        # print(f"Fun {r.fun}")
        # print(f"Drag {drag}")
        # print("Time: ", time)
        # print("Total Fuel: ", totalFuel, " kg")
        # print("")

    totalTime = (heightFinal-heightInitial)/rateOfClimb
    return [totalFuel, totalTime]


    # plt.scatter(velocities, heights)
    # plt.xlim([0, 100])
    # plt.show()





