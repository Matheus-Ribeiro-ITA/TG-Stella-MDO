import json
import codecs
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

fontP = FontProperties()
my_dpi = 600
size = 5
missionsSwitch = ["cruise", "takeOff"]
airfoilSwitch = {
    'n0012': 0,
    'ah95156': 0,
    'ah94w145': 0,
    'ah94145': 0,
    'naca4415': 0,
    'e1230': 0,
    'ls417mod': 1,
    'ls421mod': 1,
    'goe398': 1,
    'rhodesg34': 0,
    'rhodesg32': 0,
    'n22': 1,
    'goe693': 1,
    'clarky': 0,
    'n24': 1,
    'goe449': 0,
    'goe527': 0,
    'e657': 0,
    'rhodesg36': 0,
    'goe498': 1,
    'fx76mp160': 0,  # Bad
    'la203a': 0,
    'la5055': 0,
    'ls417': 0,
    'naca23018': 0,
    'e548': 0,
    'e420': 0
}

# ------------------------
mission = missionsSwitch[0]
flapOn = False
# ------------------------


def _plotData(xValueStr, yValueStr, dataList=None, xlim=None, ylim =None):
    plt.figure(figsize=(8.4, 8), dpi=my_dpi)
    for data in dataList:
        plt.plot(data[xValueStr], data[yValueStr], marker='o', markersize=2,
                 linestyle='--',
                 label=f"{data['airfoil']}_{str(data['Re']/1000)} k")

    plt.grid()
    plt.title(f"{mission}")
    plt.xlabel(f'{xValueStr}')
    plt.ylabel(f'{yValueStr}')
    plt.xlim(xlim)
    plt.ylim(ylim)

    plt.legend(loc='upper center', bbox_to_anchor=(1.1, 1.0),
          fancybox=True, shadow=True, ncol=1, fontsize=size)
    plt.savefig(f'{xValueStr}_{yValueStr}_{mission}.jpg', format='jpg', dpi=my_dpi)
    plt.show()


dirPath = os.getcwd()
if flapOn:
    folderPath = f"{dirPath}\\coord_seligFmt\\xfoilDataFlap"
    mission = missionsSwitch[1]
else:
    folderPath = f"{dirPath}\\coord_seligFmt\\xfoilData"

savedDatas = [filename for filename in os.listdir(folderPath)]

xtr_top = 0.1
xtr_bot = 0.1

dataList = []
dataCruiseList = []
dataTakeOffList = []

for filename in savedDatas:
    if airfoilSwitch[filename.split('_')[0]] == 1:
        obj_text = codecs.open(os.path.join(folderPath, filename), 'r', encoding='utf-8').read()
        dataLoaded = json.loads(obj_text)

        ReStr = filename.split('_')[1].split('.')[0]
        if int(ReStr) > 800:
            dataCruiseList.append(dataLoaded)
        else:
            dataTakeOffList.append(dataLoaded)

MISSION = {
    "cruise": dataCruiseList,
    "takeOff": dataTakeOffList,
}

_plotData("alphas", "CLs", MISSION[mission])
_plotData("alphas", "Cms", MISSION[mission])
# _plotData("CDs", "CLs", MISSION[mission])
_plotData("CDs", "CLs", MISSION[mission], xlim=[0.02, 0.12])

