"""
Graphs and data for the Shadow 200 aircraft.

Source: 'Multi-Disciplinary Design Optimization of Subsonic Fixed-Wing Unmanned Aerial
Vehicles Projected Through 2025', Gundlach
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

FLAP_INFO = {
    "15kft": ("4500 m", "cornflowerblue", ".--"),
    "Unnamed: 1": "CD ind",
    "11.25kft": ("3450 m", "blue", "v--"),
    "Unnamed: 3": "CD prof",
    "7.5kft": ("2300 m", "darkblue", "*--"),
    "Unnamed: 5": "CD ind",
    "3.75kft": ("1150 m", "slateblue", "s--"),
    "Unnamed: 7": "CD int",
    "0kft": ("0 m", "deepskyblue", "+--"),  # Cd yellow repeated
    "Unnamed: 9": "CD int",
}


def pass_data(df=None, COLORS=None):
    columns = df.columns
    names = [COLORS[column] for column in columns]
    data = []

    for i, column in enumerate(columns):
        if column.startswith("Unn"):
            a = [float(df[column].iloc[i])*4.45 for i in range(1, df[column].shape[0])]
        else:
            a = [float(df[column].iloc[i])*0.514444 for i in range(1, df[column].shape[0])]
        data.append(a)
    return data, names


def plot_data(data=None, names=None, xlabel="X label", ylabel="Y label"):
    for i in range(2, len(data), 2):
        plt.plot(data[i], data[i + 1], names[i][2], color=names[i][1], label=names[i][0])

    plt.legend()
    plt.grid()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.xlim([0, 60])
    plt.savefig("literature_data/images/" + "thrust_shadow")
    plt.show()


def flap_graphs():
    CWD = os.getcwd()
    thrust_df = pd.read_csv(os.path.join(CWD, "literature_data", "shadow_data", "Thrust_datasets.csv"), sep=',')
    data_drag, names_drag = pass_data(df=thrust_df, COLORS=FLAP_INFO)

    plot_data(data=data_drag,
              names=names_drag,
              xlabel="Velocidade (m/s)",
              ylabel="Tração máximo (N)")
    return


if __name__ == "__main__":
    flap_graphs()
