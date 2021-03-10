import json
import codecs
import os
from scipy.optimize import curve_fit

missionsSwitch = ["cruise", "takeOff"]
airfoilSwitch = {
    'n0012': 0,
    'ah95156': 0,
    'ah94w145': 0,
    'ah94145': 0,
    'naca4415': 1,
    'e1230': 0,
    'ls417mod': 1,
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
    'la203a': 1,
    'la5055': 1,
    'ls417': 0,
    'naca23018': 0,
    'e548': 0,
    'e420': 1
}

# ------------------------
mission = missionsSwitch[0]
flapOn = False
# ------------------------
airfoilPolar = {
    'cl': None,
    'cd': None,
    'claf': None,
    'clmax': None,
}

def loadData():
    """
    # Description:
        Loadd data from Xfoil analysed airfoils
    """
    dirPath = os.getcwd()
    if flapOn:
        folderPath = f"{dirPath}\\coord_seligFmt\\xfoilDataFlap"
    else:
        folderPath = f"{dirPath}\\coord_seligFmt\\xfoilData"
    savedDatas = [filename for filename in os.listdir(folderPath)]

    dataCruiseList = []
    dataTakeOffList = []

    for filename in savedDatas:
        obj_text = codecs.open(os.path.join(folderPath, filename), 'r', encoding='utf-8').read()
        dataLoaded = json.loads(obj_text)

        ReStr = filename.split('_')[1].split('.')[0]
        if int(ReStr) > 800:  # Separate Cruise from TakeOff
            dataCruiseList.append(dataLoaded)
        else:
            dataTakeOffList.append(dataLoaded)

    return dataCruiseList, dataTakeOffList


def _objectivePolar(x, cD0, cD1, k):
    """
    # Description:
        Objective function for polar fitting.
    """
    return cD0 + cD1 * x + k * x ** 2


def _objectiveSlope(x, b, a):
    """
    # Description:
        Objective function for CL/alpha fitting.
    """
    return b + x*a


def _polarData(dataList, mission="cruise"):
    """
    # Description:
        Transform xfoil data to AVL data format.
    """
    jsonList = []

    for data in dataList:
        try:
            index12Alpha = data["alphas"].index(8)
            popt, _ = curve_fit(_objectivePolar, data["CLs"][0:index12Alpha], data["CDs"][0:index12Alpha])
            cD0, cD1, k = popt
            poptSlope, _ = curve_fit(_objectiveSlope, data["alphas"][0:index12Alpha], data["CLs"][0:index12Alpha])
            b, a = poptSlope

            CLs = []
            CDs = []
            for CL in [-0.1, 0.5, 1.1]:
                CD = _objectivePolar(CL, cD0, cD1, k)
                CLs.append(CL)
                CDs.append(CD)

            cLmax = max(data["CLs"])

            exec(f"""{data['airfoil']}_{mission} = airfoilPolar.copy() """)
            exec(f"""{data['airfoil']}_{mission}['cl'] = CLs.copy() """)
            exec(f"""{data['airfoil']}_{mission}['cd'] = CDs.copy() """)
            exec(f"""{data['airfoil']}_{mission}['claf'] = a*180/3.1415/(2*3.1415) """)
            exec(f"""{data['airfoil']}_{mission}['clmax'] = cLmax """)

            name = data['airfoil'] + '_' + mission

            exec(f"""jsonList.append([name,{data['airfoil']}_{mission}])""")
        except ValueError:
            print(f"Erro on : {data['airfoil']}")

    return jsonList


def _saveJsonList(jsonList):
    """
    # Description:
        Save data to json for AVL uses.
    """
    dirPath = os.getcwd()
    with open(dirPath+"\\airfoilPolar.json", 'r') as file:
        savedData = json.load(file)
        file.close()

    for jsonData in jsonList:
        savedData.update({jsonData[0]: jsonData[1]})

    with open(dirPath+"\\airfoilPolar.json", 'w') as file:
        json.dump(savedData, file, indent=4)
        file.close()


def _cleanPolarDatas():
    """
        # Description:
            Clean all data already saved.
        """
    dirPath = os.getcwd()
    with open(dirPath+"\\airfoilPolar.json", 'w') as file:
        json.dump({}, file, indent=4)
        file.close()


_cleanPolarDatas()
dataCruiseList, dataTakeOffList = loadData()
jsonList = _polarData(dataCruiseList, mission="cruise")
_saveJsonList(jsonList)
jsonList = _polarData(dataTakeOffList, mission="takeOff")
_saveJsonList(jsonList)


