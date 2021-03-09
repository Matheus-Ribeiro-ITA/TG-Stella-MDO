import os
import pickle
import json
import matplotlib.pyplot as plt

LEGEND ={
    "wingAreaList": "Wing Area (m^2)",
    "wingSpanList": "Wing Span (m)",
    "runwayList": "Runway length (m)",
    "wingRootChordList": "Wing Root Chord (m)",
    "wingTaperRatio": "Wing taper ratio tip/root",
    "wingDivList": "Wing division (%)",
    "aircraftMassList": 'Aircraft Weight (kg)',
    "AspectRatioList": "Aspect Ratio",
    "alphaStallList": "Stall angle (deg)",
    "stallPositionList": "Stall position (%)"
}

pathSave = "resultsUntrimmed"

def _plotByLists(xListStr, yListStr, bestIndex):
    exec(f"plt.scatter({xListStr}, {yListStr})")
    exec(f"plt.scatter({xListStr}[{bestIndex}], {yListStr}[{bestIndex}], color='r')")
    plt.xlabel(LEGEND[xListStr])
    plt.ylabel(LEGEND[yListStr])
    plt.grid()
    plt.show()


allList = os.listdir(os.path.join(os.getcwd(), pathSave))
pickleList = [name for name in allList if ".pickle" in name]
jsonList = [name for name in allList if ".json" in name]

aircraftInfoList = []
resultsList = []
for i, _ in enumerate(pickleList):
    with open(f'{pathSave}/{pickleList[i]}', 'rb') as file2:
        aircraftInfoList.append(pickle.load(file2))
        file2.close()

wingAreaList = []
runwayList = []
wingSpanList = []
AspectRatioList = []
wingRootChordList = []
wingTaperRatio = []
wingDivList = []
aircraftMassList = []
stallPositionList = []
alphaStallList = []

minRunWay = 999
i = 0
for aircraftInfo in aircraftInfoList:
    wingAreaList.append(aircraftInfo.wingArea)
    runwayList.append(aircraftInfo.runway)
    wingSpanList.append(aircraftInfo.wingSpan)
    wingRootChordList.append(aircraftInfo.stateVariables["wing"]["root"]["chord"])
    AspectRatioList.append(aircraftInfo.wingSpan**2/aircraftInfo.wingArea)
    wingTaperRatio.append(aircraftInfo.taperRatioWing)
    wingDivList.append(100*aircraftInfo.stateVariables["wing"]["middle"]["b"]/(aircraftInfo.stateVariables["wing"]["middle"]["b"] + aircraftInfo.stateVariables["wing"]["tip"]["b"]))
    aircraftMassList.append(aircraftInfo.MTOW/9.81)
    stallPositionList.append(2*aircraftInfo.stallPositionWing/aircraftInfo.wingSpan)
    alphaStallList.append(aircraftInfo.alphaStallWing)

    if aircraftInfo.runway < minRunWay and aircraftInfo.wingArea < 5:
        minRunWay = aircraftInfo.runway
        bestAircraft = aircraftInfo
        bestIndex = i

    xStateBest = [aircraftInfo.wingSpan, wingDivList[bestIndex]/100, wingRootChordList[bestIndex]]
    i += 1

_plotByLists("wingSpanList", "runwayList", bestIndex)
_plotByLists("wingAreaList", "runwayList", bestIndex)
_plotByLists("AspectRatioList", "runwayList", bestIndex)
_plotByLists("wingRootChordList", "runwayList", bestIndex)
_plotByLists("wingTaperRatio", "runwayList", bestIndex)
_plotByLists("wingDivList", "runwayList", bestIndex)
_plotByLists("aircraftMassList", "runwayList", bestIndex)

_plotByLists("wingAreaList", "aircraftMassList", bestIndex)
_plotByLists("wingTaperRatio", "stallPositionList", bestIndex)
_plotByLists("wingTaperRatio", "alphaStallList", bestIndex)
# plt.scatter(wingSpanList, runwayList)
# plt.xlabel("Wing Span (m)")
# plt.ylabel("Runway length (m)")
# plt.show()