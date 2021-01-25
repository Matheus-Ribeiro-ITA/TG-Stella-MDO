# library & dataset
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt


class Uav:
    def __init__(self, name, mtow, payload, wingSpan, length, cruiseSpeed, maxSpeed,
                 stallSpeed, rangeUav, endurance, ceiling, altitude, airfoil, aspectRatio,
                 chord, isEletric, isCombustion):
        self.name = name
        self.mtow = mtow
        self.payload = payload
        self.wingSpan = wingSpan
        self.length = length
        self.cruiseSpeed = cruiseSpeed
        self.maxSpeed = maxSpeed
        self.stallSpeed = stallSpeed
        self.range = rangeUav
        self.endurance = endurance
        self.ceiling = ceiling
        self.altitude = altitude
        self.airfoil = airfoil
        self.aspectRatio = aspectRatio
        self.chord = chord
        self.isEletric = isEletric
        self.isCombustion = isCombustion

    def __repr__(self):
        return self.name


class UavDataFrame:
    """
    # UavDataFrame Object
    The UavDataFrame Object display data from UAVs in operation in the world.
    ## Datasets:
    -UAV Database [URL]: https://dataverse.no/dataset.xhtml?persistentId=doi:10.18710/L41IGQ
    ## Attributes (return-only):
    - numberUavs [int]: Number of UAVs we have data of.
    - names [list of strings]: Names of UAVs.
    - mtows [list of floats]: MTOWs of UAVs
    ...
    """

    def __init__(self, newData=False):
        dirFolder = os.path.curdir
        dataFrameName = "dataframeUAV"

        if os.path.isfile(os.path.join(dirFolder, dataFrameName)) and not newData:
            self.df = pd.read_pickle(dataFrameName)

        else:
            self.df = pd.read_excel(
                os.path.join(dirFolder, "04_Visualization.xlsx"),
                engine='openpyxl',
            )
            self.df.to_pickle(dataFrameName)

        # self.numberUavs = len(self.df["Name"])
        # self.names = self.df["Name"]
        # self.mtows = self.df["MTOW [kg]"]
        # self.payloads = self.df["Payload [kg]"]
        # self.wingSpans = self.df["Wingspan [m]"]
        # self.length = self.df["Length [m]"]
        # self.cruiseSpeed = self.df["Cruise Speed [m/s]"]
        # self.maxSpeed = self.df["Max speed [m/s]"]
        # self.stallSpeed = self.df["Stall Speed [m/s]"]
        # self.range = self.df["Range [km]"]
        # self.endurance = self.df["Endurance [h]"]
        # self.ceiling = self.df["Ceiling [m]"]
        # self.altitude = self.df["Altitude [m]"]
        # self.airfoil = self.df["Airfoil"]
        # self.aspectRatio = self.df["Aspect ratio"]
        # self.chord = self.df["Chord (est.) [m]"]
        # self.isEletric = self.df["Eletric [Bool]"]
        # self.isCombustion = self.df["Combustion [Bool]"]

    def __repr__(self):
        return repr(self.df)

    def plot_wingspan_payload(self, uav=None):
        # x = [wingSpan for wingSpan in self.wingSpans if wingSpan < 20]
        # y = [mtow for mtow in self.wingSpans if wingSpan < 20]

        b_payload = sns.jointplot(x=self.wingSpans, y=self.payloads,
                                  kind='scatter', s=100, color='m', edgecolor="skyblue", linewidth=1)
        if uav:
            sns.scatterplot(x=[uav.wingSpan], y=[uav.payload],
                            s=100, color='k', edgecolor="darkblue", linewidth=1,
                            ax=b_payload.ax_joint)

        sns.set(style="white", color_codes=True)
        plt.show()


class AtobaUAV:
    def __init__(self):
        self.name = "Atoba UAV"
        self.mtow = 480
        self.payload = 100
        self.wingSpan = 11
        self.length = 7.2
        self.cruiseSpeed = 120 / 3.6
        self.maxSpeed = 280 / 3.6
        self.stallSpeed = 55 / 3.6
        self.range = 160
        self.endurance = 20
        self.ceiling = 3050
        self.altitude = None
        self.airfoil = "ls417mod-il"
        self.aspectRatio = 5.5
        self.chord = 0.66
        self.isEletric = False
        self.isCombustion = True


def plotUavs(listUavs, xName, yName, stellaUav=None, save=False, lowerLimit=0, upperLimit=100):
    x = []
    y = []

    for uav in listUavs:
        xValue = getattr(uav, xName)
        yValue = getattr(uav, yName)
        if type(xValue) == int or type(xValue) == float:
            if lowerLimit < xValue < upperLimit and (type(yValue) == int or type(yValue) == float):
                x.append(xValue)
                y.append(yValue)

    ax = sns.JointGrid(x=x, y=y)
    # ax = sns.jointplot(x=x, y=y,
    #                           kind='scatter', s=100, color='m', edgecolor="skyblue", linewidth=1)
    if stellaUav:
        sns.scatterplot(x=[getattr(stellaUav, xName)], y=[getattr(stellaUav, yName)],
                        s=100, color='k', edgecolor="darkblue", linewidth=1,
                        ax=ax.ax_joint)

    ax.plot(sns.regplot, sns.boxplot)
    sns.set(style="white", color_codes=True)
    ax.set_axis_labels(xlabel=xName, ylabel=yName, fontsize=16)
    plt.show()

    if save: plt.savefig(f'images/TrendLine_{xName}_{yName}.png')

# uavDataFrame = UavDataFrame()
# atoba = AtobaUAV()
#
# listUav = [Uav(*row[0:17]) for index, row in uavDataFrame.df.iterrows()]
#
# plotUavs(listUav, "wingSpan", "mtow", atoba)
# plotUavs(listUav, "wingSpan", "payload", atoba)
# plotUavs(listUav, "wingSpan", "range", atoba)
# plotUavs(listUav, "wingSpan", "endurance", atoba)
# plotUavs(listUav, "wingSpan", "aspectRatio", atoba)
