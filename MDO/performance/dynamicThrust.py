import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, curve_fit
import os
import pandas as pd


def dynamicThrust(engineInfo, velocity, method="actuatorDisk"):
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
            deltaV = np.sqrt(velocity ** 2 + 2 * thrustRequired / (1.225 * diskArea)) - velocity
            etaIdeal = 1 / (deltaV / (2 * velocity) + 1)
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
        return 4.392399 * 10 ** -8 * rpm * diameterInches ** 3.5 / (np.sqrt(pitchInches)) * (
                    4.23333 * 10 ** -4 * rpm * pitchInches - velocity / dynamicCorrection)

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
        Plot the dynamic thrust.

    # Parameters:
        aircraftInfo[object]:
    """

    thrust_graphs_shadow()
    plt.xlabel("Velocidade (m/s)")
    plt.ylabel("Empuxo (N)")
    plt.legend()
    plt.grid()
    plt.savefig("literature_data/images/" + "shadow_vs_disk")
    plt.show()


FLAP_INFO = {
    "15kft": ("4500 m (GUNDLACH, 2004)", "cornflowerblue", ".--"),
    "Unnamed: 1": "CD ind",
    "11.25kft": ("3450 m (GUNDLACH, 2004)", "blue", "v--"),
    "Unnamed: 3": "CD prof",
    "7.5kft": ("2300 m (GUNDLACH, 2004)", "darkblue", "*--"),
    "Unnamed: 5": "CD ind",
    "3.75kft": ("1150 m (GUNDLACH, 2004)", "slateblue", "s--"),
    "Unnamed: 7": "CD int",
    "0kft": ("0 m (GUNDLACH, 2004)", "deepskyblue", "+--"),  # Cd yellow repeated
    "Unnamed: 9": "CD int",
}


def pass_data(df=None, COLORS=None):
    columns = df.columns
    names = [COLORS[column] for column in columns]
    data = []

    for i, column in enumerate(columns):
        if column.startswith("Unn"):
            a = [float(df[column].iloc[i]) * 4.45 for i in range(1, df[column].shape[0])]
        else:
            a = [float(df[column].iloc[i]) * 0.514444 for i in range(1, df[column].shape[0])]
        data.append(a)
    return data, names


def plot_data(data=None, names=None, xlabel="X label", ylabel="Y label"):
    for i in range(4, len(data), 2):
        plt.plot(data[i], data[i + 1], names[i][2], color=names[i][1], label=names[i][0])
    # plt.plot(data[8], data[9], names[8][2], color=names[8][1], label=names[8][0])

    # plt.legend()
    # plt.grid()
    # plt.xlabel(xlabel)
    # plt.ylabel(ylabel)
    # plt.xlim([0, 60])
    # plt.savefig("literature_data/images/" + "thrust_shadow")
    # plt.show()


def thrust_graphs_shadow():
    CWD = os.getcwd()
    thrust_df = pd.read_csv(os.path.join(CWD, "literature_data", "shadow_data", "Thrust_datasets.csv"), sep=',')
    data_thrust, names_drag = pass_data(df=thrust_df, COLORS=FLAP_INFO)

    print(data_thrust[8][:-5], data_thrust[9][:-5])
    m, b = np.polyfit([0, 1150, 2300], [data_thrust[9][0]/data_thrust[9][0],
                                        data_thrust[7][0]/data_thrust[9][0],
                                        data_thrust[5][0]/data_thrust[9][0]], 1)
    print(m, b)
    # print(data_thrust[5][0] / data_thrust[7][0])
    # print(data_thrust[3][0] / data_thrust[7][0])
    # print(data_thrust[1][0] / data_thrust[7][0])

    plot_data(data=data_thrust,
              names=names_drag,
              xlabel="Velocidade (m/s)",
              ylabel="Tração máximo (N)")
    return


engineInfo = {
    "name": "DLE 170",
    "maxPowerHp": 38,
    "maxThrust": 343,
    "propellerInches": [28, 12],
    "RPM": 7500,
    "engineFC": {
        "fuelFrac": {
            'engineValue': 0.998,
            'taxi': 0.998,
            'takeOff': 0.998,
            'climb': 0.995,
            "descent": 0.990,
            "landing": 0.992
        },
        "cCruise": 0.03794037940379404,  # 0.068 standard value
        "consumptionMaxLperH": 12,  # liters/hour
        "consumptionCruiseLperH": 7,  # liters/hour
        "fuelDensityKgperL": 0.84,  # kg/liter
        "BSFC": 1 * 608.2773878418
        # Table 8.1 Gundlach: (0.7 - 1) lb/(hp.h), 1.8 for 12 l/hr, conversion 608.2773878418 to g/(kW.h)
    },  # Check figure 2.1 for correct value. Slide 248
    "altitudeCorrection": {  # From USAF thesis Travis D. Husaboe
        '1500': 0.89,
        '3000': 0.75,
        'slope': (0.88 - 1) / 1500
    }
}

if __name__ == "__main__":
    plotDynamicThrust(engineInfo)
