import pandas as pd
import os
import matplotlib.pyplot as plt

FLAP_INFO = {
    "No_flap": ("Sem flap", "cornflowerblue", ".--"),
    "Unnamed: 1": "CD ind",
    "Plain_flap": ("Flap simples", "blue", "v--"),
    "Unnamed: 3": "CD prof",
    "Slotted_flap": ("Flap Slotted", "darkblue", "*--"),
    "Unnamed: 5": "CD ind",
    "Flower_flap": ("Flap Flower", "slateblue", "s--"),
    "Unnamed: 7": "CD int",
    "Double_flap": ("Flap duplo", "deepskyblue", "+--"),  # Cd yellow repeated
    "Unnamed: 9": "CD int",
}


def pass_data(df=None, COLORS=None):
    columns = df.columns
    names = [COLORS[column] for column in columns]
    data = []

    for i, column in enumerate(columns):
        if column.startswith("Unn"):
            a = [(float(df[column].iloc[i])/float(df["Unnamed: 1"].iloc[i])-1)*100 for i in range(1, df[column].shape[0])]
        else:
            a = [float(df[column].iloc[i]) for i in range(1, df[column].shape[0])]
        data.append(a)
    return data, names


def plot_data(data=None, names=None, xlabel="X label", ylabel="Y label"):
    # total = np.zeros(len(data[0]))
    for i in range(2, len(data), 2):
        plt.plot(data[i], data[i + 1], names[i][2], color=names[i][1], label=names[i][0])
        # total += np.array(data[i + 1])

    # plt.plot(data[0], total, DRAG_INFO["Total Sum"][2], color=DRAG_INFO["Total Sum"][1], label=DRAG_INFO["Total Sum"][0])
    plt.legend()
    plt.grid()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.xlim([0, 60])
    plt.savefig("trendLines_dir/images/" + "flaps_percentual")
    plt.show()


def flap_graphs():
    CWD = os.getcwd()
    flaps_df = pd.read_csv(os.path.join(CWD, "trendLines_dir", "flaps", "flap_datasets.csv"), sep=',')
    data_drag, names_drag = pass_data(df=flaps_df, COLORS=FLAP_INFO)

    plot_data(data=data_drag,
              names=names_drag,
              xlabel="Ângulo de enflechamento (º)",
              ylabel="Aumento percentual de CL máximo (%)")
    return


if __name__ == "__main__":
    flap_graphs()
