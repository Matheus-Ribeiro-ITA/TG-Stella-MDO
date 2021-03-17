import os
import pickle
import json
import matplotlib.pyplot as plt

# ---- Load Legend -----------------------------
with open("results\\legend.json") as file:
    LEGEND = json.load(file)

pathSave = "results\\resultsWing120"


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
wingMiddleChordList = []
wingTipChordList = []
wingTaperRatio = []
wingDivList = []
aircraftMassList = []
stallPositionList = []
alphaStallList = []
dragCruiseList = []
weightEmptyList = []

minDrag = 999
i = 0
for aircraftInfo in aircraftInfoList:
    if aircraftInfo.runway < 100 \
            and aircraftInfo.dragCruise < 72 \
            and 2 * aircraftInfo.stallPositionWing / aircraftInfo.wingSpan < 0.5 \
            and 100 * aircraftInfo.stateVariables["wing"]["middle"]["b"] / (
            aircraftInfo.stateVariables["wing"]["middle"]["b"] + aircraftInfo.stateVariables["wing"]["tip"]["b"]) < 61:

        wingAreaList.append(aircraftInfo.wingArea)
        runwayList.append(aircraftInfo.runway)
        wingSpanList.append(aircraftInfo.wingSpan)
        wingRootChordList.append(aircraftInfo.stateVariables["wing"]["root"]["chord"])
        wingMiddleChordList.append(aircraftInfo.stateVariables["wing"]["middle"]["chord"])
        wingTipChordList.append(aircraftInfo.stateVariables["wing"]["tip"]["chord"])
        AspectRatioList.append(aircraftInfo.wingSpan ** 2 / aircraftInfo.wingArea)
        wingTaperRatio.append(aircraftInfo.taperRatioWing)
        wingDivList.append(100 * aircraftInfo.stateVariables["wing"]["middle"]["b"] / (
                    aircraftInfo.stateVariables["wing"]["middle"]["b"] + aircraftInfo.stateVariables["wing"]["tip"][
                "b"]))
        aircraftMassList.append(aircraftInfo.MTOW / 9.81)
        stallPositionList.append(2 * aircraftInfo.stallPositionWing / aircraftInfo.wingSpan)
        alphaStallList.append(aircraftInfo.alphaStallWing)
        dragCruiseList.append(aircraftInfo.dragCruise)
        weightEmptyList.append(aircraftInfo.weightEmpty)

        if aircraftInfo.dragCruise < minDrag:
            minDrag = aircraftInfo.dragCruise
            bestAircraft = aircraftInfo
            bestIndex = i
            xStateBest = [aircraftInfo.wingSpan, wingDivList[bestIndex] / 100, wingRootChordList[bestIndex]]

        i += 1

# _plotByLists("wingSpanList", "runwayList", bestIndex)
_plotByLists("wingAreaList", "dragCruiseList", bestIndex)
_plotByLists("wingAreaList", "runwayList", bestIndex)
# _plotByLists("AspectRatioList", "runwayList", bestIndex)
_plotByLists("wingRootChordList", "dragCruiseList", bestIndex)
_plotByLists("wingMiddleChordList", "dragCruiseList", bestIndex)
_plotByLists("wingTipChordList", "dragCruiseList", bestIndex)
# _plotByLists("wingTaperRatio", "runwayList", bestIndex)
_plotByLists("wingDivList", "dragCruiseList", bestIndex)
# _plotByLists("aircraftMassList", "runwayList", bestIndex)

# _plotByLists("wingAreaList", "aircraftMassList", bestIndex)
# _plotByLists("wingTaperRatio", "stallPositionList", bestIndex)
# _plotByLists("wingTaperRatio", "alphaStallList", bestIndex)


devWing = 100 * bestAircraft.stateVariables["wing"]["middle"]["b"] / (
            bestAircraft.stateVariables["wing"]["middle"]["b"] + bestAircraft.stateVariables["wing"]["tip"]["b"])
print('--------------------')
print("Drag AVL: ", bestAircraft.dragCruise)
print("Alpha Cruise: ", bestAircraft.alphaRun)
print("Wing Area: ", bestAircraft.wingArea)
print("Wing Span: ", bestAircraft.wingSpan)
print("EM: ", bestAircraft.staticMargin)
print("Stall Wing: ", bestAircraft.alphaStallWing)
print("Stall position: ", 2 * bestAircraft.stallPositionWing / bestAircraft.wingSpan)
print("devWing", devWing)
print("c root", bestAircraft.stateVariables["wing"]["root"]["chord"])
print("c middle", bestAircraft.stateVariables["wing"]["middle"]["chord"])
print("c tip", bestAircraft.stateVariables["wing"]["tip"]["chord"])
