import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, curve_fit


def dynamicThrust(engineInfo, velocity, method="actuatorDisk"):
    """
    # Description:
        Calculates the dynamic thrust.

    # Parameters:
        aircraftInfo[object]:
    """

    radiusPropeller = engineInfo['propellerInches'][0]*0.0254/2
    diskArea = 3.1415*radiusPropeller**2
    diameterInches = engineInfo['propellerInches'][0]
    pitchInches = engineInfo['propellerInches'][1]
    rpm = engineInfo['RPM']
    powerHp = engineInfo['maxPowerHp']
    power = 745.7*powerHp

    def _actuatorSolver(velocity, etaCorrection):
        """
        # Description:
            Solves the actuator disk equation for a velocity. Also apply a correction on eta
        of non ideal propeller efficiency, usually between 0.85 and 9.5

        ## Parameters:
        - Velocity [float]: Aircraft speed in m/s.
        - etaCorrection [float]: Non ideal efficiency.

        ## Return:
        - Thrust [float]: Max thrust provided.
        """
        def _actuatorDiskTheory(thrustRequired):
            """Formula derived from 'Designing Unmanned Aircraft Systems: A Comprehensive Approach'"""
            deltaV = np.sqrt(velocity**2 + 2*thrustRequired/(1.225*diskArea)) - velocity
            etaIdeal = 1/(deltaV/(2*velocity) + 1)
            thrustReal = power * etaIdeal * etaCorrection / velocity
            erroThrust = thrustReal - thrustRequired
            return erroThrust

        solution = fsolve(_actuatorDiskTheory, 100)

        return solution

    def _thrustInternetFormula(velocity, dynamicCorrection):
        """Formula found on
        https://www.electricrcaircraftguy.com/2013/09/propeller-static-dynamic-thrust-equation.html

        dynamicCorrection: correction discussed on website
        """
        return 4.392399*10**-8*rpm * diameterInches**3.5/(np.sqrt(pitchInches))*(4.23333*10**-4*rpm*pitchInches - velocity/dynamicCorrection)

    METHOD = {
        "actuatorDisk": _actuatorSolver(velocity, 0.5),
        "internetFormula": _thrustInternetFormula(velocity, 1.3)
    }

    return float(METHOD[method])


def dynamicThrustCurve(engineInfo, method="actuatorDisk"):

    velocityList = np.linspace(0.5, 50, 10)
    thrustList = [dynamicThrust(engineInfo, velocity, method=method) for velocity in velocityList]

    def _objective(x, cD0, cD1, k):
        return cD0 + cD1 * x + k * x ** 2

    popt, _ = curve_fit(_objective, velocityList, thrustList)
    cD0, cD1, k = popt

    return [cD0, cD1, k]

def plotDynamicThrust(engineInfo):
    """
    # Description:
        Calculates the dynamic thrust.

    # Parameters:
        aircraftInfo[object]:
    """

    radiusPropeller = engineInfo['propellerInches'][0] * 0.0254 / 2
    diskArea = 3.1415 * radiusPropeller ** 2
    diameterInches = engineInfo['propellerInches'][0]
    pitchInches = engineInfo['propellerInches'][1]
    rpm = engineInfo['RPM']
    powerHp = engineInfo['maxPowerHp']
    power = 745.7 * powerHp

    def _actuatorSolver(velocity, etaCorrection):
        """
        # Description:
            Solves the actuator disk equation for a velocity. Also apply a correction on eta
        of non ideal propeller efficiency, usually between 0.85 and 9.5

        ## Parameters:
        - Velocity [float]: Aircraft speed in m/s.
        - etaCorrection [float]: Non ideal efficiency.

        ## Return:
        - Thrust [float]: Max thrust provided.
        """
        def _actuatorDiskTheory(thrustRequired):
            """Formula derived from 'Designing Unmanned Aircraft Systems: A Comprehensive Approach'"""
            deltaV = np.sqrt(velocity**2 + 2*thrustRequired/(1.225*diskArea)) - velocity
            etaIdeal = 1/(deltaV/(2*velocity) + 1)
            thrustReal = power * etaIdeal * etaCorrection / velocity
            erroThrust = thrustReal - thrustRequired
            return erroThrust

        solution = fsolve(_actuatorDiskTheory, 100)

        return solution

    def _thrustInternetFormula(velocity, dynamicCorrection):
        """Formula found on
        https://www.electricrcaircraftguy.com/2013/09/propeller-static-dynamic-thrust-equation.html

        dynamicCorrection: correction discussed on website
        """
        return 4.392399*10**-8*rpm * diameterInches**3.5/(np.sqrt(pitchInches))*(4.23333*10**-4*rpm*pitchInches - velocity/dynamicCorrection)

    velocityList = np.linspace(0.5, 50, 40)
    thrustActuator = [_actuatorSolver(velocity) for velocity in velocityList]
    thrustInternet = [_thrustInternetFormula(velocity) for velocity in velocityList]
    thrustInternet35p = [_thrustInternetFormula(velocity/1.30) for velocity in velocityList]

    plt.scatter(velocityList, thrustActuator, color='b', label="Actuator Disk Theory (90% correction)")
    plt.scatter(velocityList, thrustInternet, color='r', label="Internet Guy Formula")
    plt.scatter(velocityList, thrustInternet35p, color='green', label="Internet Guy Formula (30% correction)")
    plt.xlabel("Velocity (m/s)")
    plt.ylabel("Thrust (N)")
    plt.legend()
    plt.show()



    # velocityList = np.linspace(2, 60, 20)
    # etaIdeal50N = [actuatorDiskTheory(velocity, 5) for velocity in velocityList]
    #
    # plt.scatter(velocityList, etaIdeal50N)
    # plt.show()
    #
    #
    # thrust = [power*eta*0.9/velocity for eta, velocity in zip(etaIdeal50N, velocityList)]
    # plt.scatter(velocityList, thrust)
    # plt.show()

