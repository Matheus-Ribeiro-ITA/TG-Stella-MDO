from MDO.auxTools import atmosphere
import numpy as np
import scipy

import sys
import matplotlib.pyplot as plt


def climbFuel(aircraftInfo=None, heightInitial=0, heightFinal=1500, rateOfClimb=1, nSteps=5, logger=None):
    wingArea = aircraftInfo.wing.area + 2
    weightTakeOff = aircraftInfo.weight.empty + aircraftInfo.weight.fuel - aircraftInfo.weight.fuelTakeOff
    t0 = aircraftInfo.thrust.v0
    t1 = aircraftInfo.thrust.v1
    t2 = aircraftInfo.thrust.v2
    heightSlope = aircraftInfo.thrust.slopeHeight
    cD0 = aircraftInfo.cD0
    cD1 = aircraftInfo.cD1
    cD2 = aircraftInfo.k

    heights = np.linspace(heightInitial, heightFinal, nSteps)

    def funDrag(velocity):
        cL = 2 * weight / (wingArea * velocity ** 2 * rho)
        return 1 / 2 * rho * velocity ** 2 * wingArea * (cD0 + cD1 * cL + cD2 * cL ** 2)

    def funThrottleRequired(velocity):
        return funDrag(velocity) + rateOfClimb * weight / velocity

    xDist = 0
    totalFuelKg = 0.0  # Weird: I declare as float but it becomes a np.array
    for i in range(len(heights) - 1):
        weight = weightTakeOff - totalFuelKg * 9.8
        height = (heights[i] + heights[i + 1]) / 2
        T, p, rho, mi = atmosphere(height)
        velocityClimb = analytical_velocity(wingArea=wingArea, weight=weight, rho=rho, height=height,
                                            cD0=cD0, cD2=cD2, rateOfClimb=rateOfClimb)
        thrustMax = (t0 + t1 * velocityClimb + t2 * velocityClimb ** 2) * (1 + heightSlope * height)
        throttle = funThrottleRequired(velocityClimb) / thrustMax
        time = (heights[i + 1] - heights[i]) / rateOfClimb
        xDist += velocityClimb * time
        fuelKgS = aircraftInfo.engine.consumptionMaxLperH * aircraftInfo.engine.fuelDensity * throttle / 3600
        totalFuelKg += fuelKgS * time

    aircraftInfo.weight.fuelClimb = totalFuelKg * 9.8
    aircraftInfo.performance.climb.time = (heightFinal - heightInitial) / rateOfClimb
    aircraftInfo.performance.climb.range = xDist
    return


def analytical_velocity(wingArea=None, weight=None,
                        t0=None, t1=None, t2=None,
                        heightSlope=None, rho=None, height=None,
                        cD0=None, cD1=None, cD2=None,
                        rateOfClimb=None):
    p_4 = rho * wingArea * cD0
    p_3 = 0
    p_2 = 0
    p_1 = -rateOfClimb * weight
    p_0 = -4 * weight ** 2 * cD2 / (rho * wingArea)

    poly = [p_4, p_3, p_2, p_1, p_0]
    sol = np.roots(poly)
    sol = [np.real(num) for num in sol if np.isreal(num) and np.real(num) > 0]

    if len(sol) != 1:
        raise ValueError("More or less than 1 solution for climb velocity")
    return sol[0]


def climbFuel_iterative(aircraftInfo=None, heightInitial=0, heightFinal=1500, rateOfClimb=1, nSteps=5, logger=None):
    wingArea = aircraftInfo.wing.area
    weightTakeOff = aircraftInfo.weight.empty + aircraftInfo.weight.fuel - aircraftInfo.weight.fuelTakeOff
    t0 = aircraftInfo.thrust.v0
    t1 = aircraftInfo.thrust.v1
    t2 = aircraftInfo.thrust.v2
    heightSlope = aircraftInfo.thrust.slopeHeight
    cD0 = aircraftInfo.cD0
    cD1 = aircraftInfo.cD1
    cD2 = aircraftInfo.k

    heights = np.linspace(heightInitial, heightFinal, nSteps)

    def funDrag(velocity):
        cL = 2 * weight / (wingArea * velocity ** 2 * rho)
        return 1 / 2 * rho * velocity ** 2 * wingArea * (cD0 + cD1 * cL + cD2 * cL ** 2)

    def funThrottleRequired(velocity):
        thrustMax = (t0 + t1 * velocity + t2 * velocity ** 2) * (1 + heightSlope * height)
        return (funDrag(velocity) + rateOfClimb * weight / velocity) / thrustMax

    def rateConstraint(velocity):
        thrustMax = (t0 + t1 * velocity + t2 * velocity ** 2) * (1 + heightSlope * height)
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
    for i in range(len(heights) - 1):
        weight = weightTakeOff - totalFuelKg * 9.8
        height = (heights[i] + heights[i + 1]) / 2
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
            thrustMax = [(t0 + t1 * v + t2 * v ** 2) * (1 + heightSlope * height) for v in vs]
            rateDrag = [rateOfClimb * weight / v for v in vs]
            totalDrag = [d + r for d, r in zip(drags, rateDrag)]
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

            aircraftInfo.weight.fuelClimb = 5 * 9.8
            aircraftInfo.performance.climb.range = 0
            return
            # sys.exit("aa! errors!")

        velocityClimb = r.x
        print("Otimization: ", velocityClimb)
        print("Analytical: ", analytical_velocity(wingArea=wingArea, weight=weight, t0=t0, t1=t1, t2=t2,
                                                  heightSlope=heightSlope, rho=rho, height=height, cD0=cD0,
                                                  cD1=cD1, cD2=cD2, rateOfClimb=rateOfClimb))
        throttle = r.fun
        time = (heights[i + 1] - heights[i]) / rateOfClimb
        xDist += r.x[0] * time
        fuelKgS = aircraftInfo.engine.consumptionMaxLperH * aircraftInfo.engine.fuelDensity * throttle / 3600
        totalFuelKg += fuelKgS * time

    aircraftInfo.weight.fuelClimb = totalFuelKg * 9.8
    aircraftInfo.performance.climb.time = (heightFinal - heightInitial) / rateOfClimb
    aircraftInfo.performance.climb.range = xDist
    return
