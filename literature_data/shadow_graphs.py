"""
Graphs and data for the Shadow 200 aircraft.

Source: 'Multi-Disciplinary Design Optimization of Subsonic Fixed-Wing Unmanned Aerial
Vehicles Projected Through 2025', Gundlach
"""


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

SHADOW_WEIGHT_DATA = {
    "estruturas": 38.8,
    "subsistemas": 18.45,
    "avionica": 13.88,
    "propulsao": 12.7,
    "combustivel": 28.25,
    "growth": 7.9,
    "carga paga": 23.58,
    "Peso bruto de projeto": 38.8 + 18.45 + 13.88 + 12.7 + 28.25 + 7.9 + 23.58
}

SHADOW_WEIGHT_BREAKDOWN_DATA = {
    "wing": 8.7,
    "tail": 1.8,
    "fuselage": 2.78,
    "gear": 8.62,
    "installation": 16.9,
    "total": 8.7 + 1.8 + 2.78 + 8.62 + 16.9
}

aircraft_weight_data = {
    "estruturas": 37.9,
    "subsistemas": 18.45,
    "avionica": 13.88,
    "propulsao": 12.7,
    "combustivel": 29.5,
    "carga paga": 23.58,
    "growth": 7.9,
    "Peso bruto de projeto": 37.9 + 18.45 + 13.88 + 12.7 + 29.5 + 23.58 + 7.9
}

aircraft_weight_breakdown_data = {
    "wing": 7.49,
    "tail": 2.94,
    "fuselage": 6.32,
    "gear": 0.65 + 3.65,
    "installation": 16.9,
    'total': 7.49 + 2.94 + 6.32 + 0.65 + 3.65 + 16.9
}

aircraft_polar_data = {
    'cD0': 0.0251,
    'cD1': 0.003,
    'cD2': 0.0586
}


def pass_data(df=None, COLORS=None):
    columns = df.columns
    names = [COLORS[column] for column in columns]
    data = [df[column].iloc[1:].astype(float) for column in columns]
    return data, names


def plot_data(data=None, names=None, xlabel="X label", ylabel="Y label", saveName='',
              plotSum=False):
    total = np.zeros(len(data[0]))
    if names is not None:
        for i in range(0, len(data), 2):
            plt.plot(data[i], data[i + 1], names[i][2], color=names[i][1], label=names[i][0])
            total += np.array(data[i + 1]) if plotSum else 0
        if plotSum:
            plt.plot(data[0], total, DRAG_INFO["Total Sum"][2], color=DRAG_INFO["Total Sum"][1], label=DRAG_INFO["Total Sum"][0])
    else:
        for i in range(0, len(data), 2):
            plt.plot(data[i], data[i + 1])

    plt.legend()
    plt.grid()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig("literature_data/images/" + ylabel + saveName)
    plt.show()


def aerodynamics_graphs():
    CWD = os.getcwd()
    drag_df = pd.read_csv(os.path.join(CWD, "literature_data", "shadow_data", "Drag_shadow.csv"), sep=';')
    lift_df = pd.read_csv(os.path.join(CWD, "literature_data", "shadow_data", "Lift_drag_datasets.csv"), sep=',')

    data_drag, names_drag = pass_data(df=drag_df, COLORS=DRAG_INFO)
    data_lift, names_lift = pass_data(df=lift_df, COLORS=LIFT_INFO)

    # Drag Polar Shadow 200
    plot_data(data=data_drag,
              names=names_drag,
              xlabel="Coeficiente de sustentação (CL)",
              ylabel="Coeficiente de arrasto (CD)",
              plotSum=True)

    plot_data(data=data_lift,
              names=names_lift,
              xlabel="Coeficiente de sustentação (CL)",
              ylabel="Razão CL por CD")

    # Drag Polar Shadow 200 vs custom data
    cLAircraft = np.linspace(0, 1.5, 20, endpoint=True)
    cDAircraft = aircraft_polar_data['cD2'] * cLAircraft ** 2 + aircraft_polar_data['cD0'] + aircraft_polar_data['cD1'] * cLAircraft

    total = np.zeros(len(data_drag[0]))
    for i in range(0, len(data_drag), 2):
        total += np.array(data_drag[i + 1])

    data_drag_comparison = [data_drag[0], total, cLAircraft, cDAircraft]
    namesComparison = [('Gundlach (2004)', 'blue', 'v--'), '', ('Autor', 'darkorchid', '.--'), '']
    plot_data(data=data_drag_comparison,
              names=namesComparison,
              xlabel="Coeficiente de sustentação (CL)",
              ylabel="Coeficiente de arrasto (CD)",
              saveName='comparison')

    data_drag_comparison_cl_cd = [data_lift[0], data_lift[1], cLAircraft, cLAircraft/cDAircraft]
    plot_data(data=data_drag_comparison_cl_cd,
              names=namesComparison,
              xlabel="Coeficiente de sustentação (CL)",
              ylabel="Razão CL por CD",
              saveName='comparison')

    return


def weight_bar_graph(in_percentage=False):
    labels = ["Estruturas", "Subsistemas", "Aviônica", "Propulsão", "Combustível",  "Carga paga", "Crescimento",
              None if in_percentage else "Peso total"]
    total_weight = SHADOW_WEIGHT_DATA["Peso bruto de projeto"]

    men_means = [SHADOW_WEIGHT_DATA["estruturas"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_DATA["estruturas"],
                 SHADOW_WEIGHT_DATA["subsistemas"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_DATA["subsistemas"],
                 SHADOW_WEIGHT_DATA["avionica"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_DATA["avionica"],
                 SHADOW_WEIGHT_DATA["propulsao"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_DATA["propulsao"],
                 SHADOW_WEIGHT_DATA["combustivel"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_DATA["combustivel"],
                 SHADOW_WEIGHT_DATA["carga paga"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_DATA["carga paga"],
                 SHADOW_WEIGHT_DATA["growth"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_DATA["growth"],
                 None if in_percentage else SHADOW_WEIGHT_DATA["Peso bruto de projeto"]]

    men_means_our_aricraft = [aircraft_weight_data["estruturas"] / total_weight * 100 if in_percentage else aircraft_weight_data["estruturas"],
                 aircraft_weight_data["subsistemas"] / total_weight * 100 if in_percentage else aircraft_weight_data["subsistemas"],
                 aircraft_weight_data["avionica"] / total_weight * 100 if in_percentage else aircraft_weight_data["avionica"],
                 aircraft_weight_data["propulsao"] / total_weight * 100 if in_percentage else aircraft_weight_data["propulsao"],
                 aircraft_weight_data["combustivel"] / total_weight * 100 if in_percentage else aircraft_weight_data["combustivel"],
                 aircraft_weight_data["carga paga"] / total_weight * 100 if in_percentage else aircraft_weight_data["carga paga"],
                 aircraft_weight_data["growth"] / total_weight * 100 if in_percentage else aircraft_weight_data["growth"],
                 None if in_percentage else aircraft_weight_data["Peso bruto de projeto"]]
    # women_means = [25, 32, 34, 20, 25]

    if in_percentage:
        labels = labels.pop()
        men_means = men_means.pop()
        men_means_our_aricraft = men_means_our_aricraft.pop()


    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, men_means, width, label='Gundlach (2004)')
    rects2 = ax.bar(x+width*1.1, men_means_our_aricraft, width, label='Autor')
    # rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if in_percentage:
        ax.set_ylabel('Distribuição de peso (%)')
    else:
        ax.set_ylabel('Distribuição de peso (Kg)')
    # ax.set_title('Distribuição de peso Shadow 200')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45)
    ax.legend()

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)
    for i, p in enumerate(ax.patches):
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()

        if in_percentage:
            ax.annotate(f'{round(height, 1)} %', (x + width / 2, y + height * 1.02), ha='center', fontsize=6.5)
        else:
            ax.annotate(f'{round(height, 1)}', (x + width / 2, y + height * 1.02), ha='center', fontsize=6.5)

    fig.tight_layout()
    plt.savefig("literature_data/images/" + "pesos_barras")
    plt.show()


def weight_breakdown_bar_graph(in_percentage=False):
    labels = ["Asa", "Empenagem", "Fuselagem", "Trem de pouso", "Instalação",
              None if in_percentage else "Peso estrutural \n total"]
    total_weight = SHADOW_WEIGHT_BREAKDOWN_DATA["total"]

    men_means = [SHADOW_WEIGHT_BREAKDOWN_DATA["wing"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_BREAKDOWN_DATA["wing"],
                 SHADOW_WEIGHT_BREAKDOWN_DATA["tail"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_BREAKDOWN_DATA["tail"],
                 SHADOW_WEIGHT_BREAKDOWN_DATA["fuselage"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_BREAKDOWN_DATA["fuselage"],
                 SHADOW_WEIGHT_BREAKDOWN_DATA["gear"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_BREAKDOWN_DATA["gear"],
                 SHADOW_WEIGHT_BREAKDOWN_DATA["installation"] / total_weight * 100 if in_percentage else SHADOW_WEIGHT_BREAKDOWN_DATA["installation"],
                 None if in_percentage else SHADOW_WEIGHT_BREAKDOWN_DATA["total"]]

    men_means_our_aricraft = [aircraft_weight_breakdown_data["wing"] / total_weight * 100 if in_percentage else aircraft_weight_breakdown_data["wing"],
                 aircraft_weight_breakdown_data["tail"] / total_weight * 100 if in_percentage else aircraft_weight_breakdown_data["tail"],
                 aircraft_weight_breakdown_data["fuselage"] / total_weight * 100 if in_percentage else aircraft_weight_breakdown_data["fuselage"],
                 aircraft_weight_breakdown_data["gear"] / total_weight * 100 if in_percentage else aircraft_weight_breakdown_data["gear"],
                 aircraft_weight_breakdown_data["installation"] / total_weight * 100 if in_percentage else aircraft_weight_breakdown_data["installation"],
                 None if in_percentage else aircraft_weight_breakdown_data["total"]]
    # women_means = [25, 32, 34, 20, 25]

    if in_percentage:
        labels = labels.pop()
        men_means = men_means.pop()
        men_means_our_aricraft = men_means_our_aricraft.pop()


    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, men_means, width, label='Gundlach (2004)')
    rects2 = ax.bar(x+width*1.1, men_means_our_aricraft, width, label='Autor')
    # rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if in_percentage:
        ax.set_ylabel('Distribuição de peso (%)')
    else:
        ax.set_ylabel('Distribuição de peso (Kg)')
    # ax.set_title('Distribuição de peso Shadow 200')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45)
    ax.legend()

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)
    for i, p in enumerate(ax.patches):
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()

        if in_percentage:
            ax.annotate(f'{round(height, 1)} %', (x + width / 2, y + height * 1.02), ha='center', fontsize=7)
        else:
            ax.annotate(f'{round(height, 1)}', (x + width / 2, y + height * 1.02), ha='center', fontsize=7)

    fig.tight_layout()
    plt.savefig("literature_data/images/" + "pesos_barras_breakdown")
    plt.show()


def weight_pie_graph():
    fig1, ax1 = plt.subplots()
    # Pie chart
    labels = ["Estruturas", "Aviônica", "Propulsão", "Combustível", "Carga paga", 'Crescimento', 'Subsistemas']
    total_weight = SHADOW_WEIGHT_DATA["Peso bruto de projeto"]
    sizes = [SHADOW_WEIGHT_DATA["estruturas"] / total_weight * 100,
             SHADOW_WEIGHT_DATA["avionica"] / total_weight * 100,
             SHADOW_WEIGHT_DATA["propulsao"] / total_weight * 100,
             SHADOW_WEIGHT_DATA["combustivel"] / total_weight * 100,
             SHADOW_WEIGHT_DATA["carga paga"] / total_weight * 100,
             SHADOW_WEIGHT_DATA["growth"] / total_weight * 100,
             SHADOW_WEIGHT_DATA["subsistemas"] / total_weight * 100]
    # colors
    # colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#e38dd9']
    colors = ['cornflowerblue', 'deepskyblue', 'slateblue', '#D6D6D6', 'slategray', 'c', 'aquamarine']
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
    plt.savefig("literature_data/images/" + "pesos_pie")
    plt.show()


if __name__ == "__main__":
    # aerodynamics_graphs()
    # weight_pie_graph()
    # weight_bar_graph(in_percentage=False)
    weight_breakdown_bar_graph(in_percentage=False)
