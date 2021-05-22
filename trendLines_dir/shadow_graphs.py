import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

DRAG_INFO = {
    "Pink_curve": ("CD ind", "cornflowerblue", ".--"),
    "Unnamed: 1": "CD ind",
    "Blue_curve": ("CD prof", "blue", "v--"),
    "Unnamed: 3": "CD prof",
    "Yellow_curve": ("CD fuse", "darkblue", "*--"),
    "Unnamed: 5": "CD ind",
    "Light_blue_curve": ("CD int", "slateblue", "s--"),
    "Unnamed: 7": "CD int",
    "Purple_curve": ("CD gear", "deepskyblue", "+--"),  # Cd yellow repeated
    "Unnamed: 9": "CD gear",
    "Total Sum": ("CD total", "slategray", "d--")
}

LIFT_INFO = {
    "Pink_curve": ("Re = 259k", "cornflowerblue", ".--"),
    "Unnamed: 1": "",
    "Blue_curve": ("Re = 186k", "blue", "v--"),
    "Unnamed: 3": "",
    "Yellow_curve": ("Re = 461k", "darkblue", "*--"),
    "Unnamed: 5": "",
    "Light_blue_curve": ("Re = 737k", "slateblue", "s--"),
    "Unnamed: 7": "",
}

WEIGHT_DATA = {
    "estruturas": 64.4,
    "avionica": 13.6,
    "alternador": 12.7,
    "combustivel": 29,
    "carga paga": 23.6,
    "Peso bruto de projeto": 143.3
}


def pass_data(df=None, COLORS=None):
    columns = df.columns
    names = [COLORS[column] for column in columns]
    data = [df[column].iloc[1:].astype(float) for column in columns]
    return data, names


def plot_data(data=None, names=None, xlabel="X label", ylabel="Y label"):
    # total = np.zeros(len(data[0]))
    for i in range(0, len(data), 2):
        plt.plot(data[i], data[i + 1], names[i][2], color=names[i][1], label=names[i][0])
        # total += np.array(data[i + 1])

    # plt.plot(data[0], total, DRAG_INFO["Total Sum"][2], color=DRAG_INFO["Total Sum"][1], label=DRAG_INFO["Total Sum"][0])
    plt.legend()
    plt.grid()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig("trendLines_dir/images/" + ylabel)
    plt.show()


def aerodynamics_graphs():
    CWD = os.getcwd()
    drag_df = pd.read_csv(os.path.join(CWD, "trendLines_dir", "shadow_data", "Drag_shadow.csv"), sep=';')
    lift_df = pd.read_csv(os.path.join(CWD, "trendLines_dir", "shadow_data", "Lift_drag_datasets.csv"), sep=',')

    print(lift_df.columns)
    data_drag, names_drag = pass_data(df=drag_df, COLORS=DRAG_INFO)
    data_lift, names_lift = pass_data(df=lift_df, COLORS=LIFT_INFO)

    # plot_data(data=data_drag,
    #           names=names_drag,
    #           xlabel="Coeficiente de sustentação (CL)",
    #           ylabel="Coeficiente de arrasto (CD)")

    plot_data(data=data_lift,
              names=names_lift,
              xlabel="Coeficiente de sustentação (CL)",
              ylabel="Razão CL por CD")

    return


def weight_bar_graph():
    labels = ["Estruturas", "Aviônica", "Propulsão", "Combustível", "Carga paga"]
    total_weight = WEIGHT_DATA["Peso bruto de projeto"]

    men_means = [WEIGHT_DATA["estruturas"] / total_weight * 100,
                 WEIGHT_DATA["avionica"] / total_weight * 100,
                 WEIGHT_DATA["alternador"] / total_weight * 100,
                 WEIGHT_DATA["combustivel"] / total_weight * 100,
                 WEIGHT_DATA["carga paga"] / total_weight * 100]
    # women_means = [25, 32, 34, 20, 25]
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, men_means, width, label='Shadow 200')
    # rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Distribuição de peso')
    # ax.set_title('Distribuição de peso Shadow 200')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)
    for p in ax.patches:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        ax.annotate(f'{round(height, 1)} %', (x + width / 2, y + height * 1.02), ha='center')

    fig.tight_layout()
    plt.savefig("trendLines_dir/images/" + "pesos_barras")
    plt.show()


def weight_pie_graph():
    fig1, ax1 = plt.subplots()
    # Pie chart
    labels = ["Estruturas", "Aviônica", "Propulsão", "Combustível", "Carga paga"]
    total_weight = WEIGHT_DATA["Peso bruto de projeto"]
    sizes = [WEIGHT_DATA["estruturas"] / total_weight * 100,
             WEIGHT_DATA["avionica"] / total_weight * 100,
             WEIGHT_DATA["alternador"] / total_weight * 100,
             WEIGHT_DATA["combustivel"] / total_weight * 100,
             WEIGHT_DATA["carga paga"] / total_weight * 100]
    # colors
    # colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#e38dd9']
    colors = ['cornflowerblue', 'deepskyblue', 'slateblue', '#D6D6D6', 'slategray']
    # explsion
    explode = ([0.05] * len(labels))

    plt.pie(sizes, colors=colors, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode=explode)
    # draw circle
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')
    ax1.set_title("Distribuição de massa Shadow 200")
    plt.tight_layout()
    plt.savefig("trendLines_dir/images/" + "pesos_pie")
    plt.show()


if __name__ == "__main__":
    # aerodynamics_graphs()
    weight_pie_graph()
