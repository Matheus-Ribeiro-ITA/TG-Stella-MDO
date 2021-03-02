import json
from math import radians, sqrt, tan
import avl.avlwrapper as avl
from _collections import OrderedDict
from pprint import pprint
from aircraftInfo import infoSurface


def avlGeoBuild(stateVariables, controlVariables):
    stateVariables = _addControl2States(stateVariables, controlVariables)
    # print("K and V:")
    # for k, v in stateVariables["wing"].items():
    #     print(k, v)
    # pprint(stateVariables)
    # print("")

    surfaces = []
    for surfaceName, surfaceDict in stateVariables.items():
        secPoint = []
        sections = []
        for secName, secData in surfaceDict.items():
            section, secPoint = _translateSec(secName, secData, secPoint, surfaceName=surfaceName)
            sections.append(section)

        surfaces.append(avl.Surface(name=surfaceName,
                                    n_chordwise=12,
                                    chord_spacing=avl.Spacing.cosine,
                                    n_spanwise=20,
                                    span_spacing=avl.Spacing.cosine,
                                    y_duplicate=0.0,
                                    sections=sections))

    surfaceArea, surfaceMAC, surfaceSpan, surfaceSweep = infoSurface(stateVariables['wing'])
    ref_pnt = avl.Point(x=0, y=0, z=0)
    aircraftAvl = avl.Aircraft(name='aircraft',
                               reference_area=surfaceArea,
                               reference_chord=surfaceMAC,
                               reference_span=surfaceSpan,
                               reference_point=ref_pnt,
                               mach=0,
                               surfaces=surfaces)
    return aircraftAvl


def _translateSec(secName, secData, secPoint, surfaceName=None):
    if secName == "root":
        secPoint = [secData['x'], secData['y'], secData['z']]
        sec_le_pnt = avl.Point(*secPoint)
    else:
        if surfaceName == "vertical":
            secPoint = [secPoint[0] + secData['b'] * tan(secData['sweepLE']),
                        secPoint[1] + secData['b'] * tan(secData['dihedral']),
                        secPoint[2] + secData['b']]

        else:
            secPoint = [secPoint[0] + secData['b'] * tan(secData['sweepLE']),
                        secPoint[1] + secData['b'],
                        secPoint[2] + secData['b'] * tan(secData['dihedral'])]

        sec_le_pnt = avl.Point(x=secPoint[0],
                               y=secPoint[1],
                               z=secPoint[2])

    controlSurfaces = None
    if "control" in secData:
        if secData['control'] == "aileron":
            commandInversion = -1
        else: commandInversion = 1
        controlSurfaces = avl.Control(name=secData['control'],
                                      gain=1.0,
                                      x_hinge=0.6,
                                      duplicate_sign=commandInversion)

    section = avl.Section(leading_edge_point=sec_le_pnt,
                          chord=secData['chord'],
                          airfoil=avl.NacaAirfoil(secData['airfoil']),
                          controls=[controlSurfaces])
    return section, secPoint


def _addControl2States(stateVariables, controlVariables):
    """
    -Description
        Add control surfaces from "controlVariables" to the "stateVariables"

    - Input
    :param stateVariables[Dict]: aircraft state variables. Ex: wing chord, espan etc
    :param controlVariables[Dict]:
    - Output
    :return:
    """
    if "aileron" in controlVariables:
        aileronDict = controlVariables["aileron"]
        rootSecSpan = stateVariables["wing"]["middle"]["b"]
        wingSpan = rootSecSpan + stateVariables["wing"]["tip"]["b"]

        aileronDivisionValue = aileronDict["spanStartPercentage"] * wingSpan - rootSecSpan
        # Case aileron in between Middle and Tip section:
        if aileronDivisionValue > 0:
            chord = _linearizationSecValues(stateVariables, "middle", "tip", aileronDivisionValue, "chord")
            aoa = _linearizationSecValues(stateVariables, "middle", "tip", aileronDivisionValue, "aoa")
            stateVariables["wing"].update({
                "aileron": {
                    "chord": chord,
                    "b": aileronDivisionValue,
                    "sweepLE": stateVariables["wing"]["tip"]["sweepLE"],
                    "aoa": aoa,
                    "dihedral": 0,
                    "airfoil": stateVariables["wing"]["tip"]["airfoil"],
                    "control": "aileron",
                }
            })
            stateVariables["wing"]["tip"].update({"control": "aileron"})
            newB = stateVariables["wing"]["tip"]["b"] - aileronDivisionValue
            stateVariables["wing"]["tip"].update({"b": newB})
            stateVariables["wing"].move_to_end("tip", last=True)
        # Case aileron in between Root and Middle section:
        if aileronDivisionValue < 0:
            aileronDivisionValue = rootSecSpan + aileronDivisionValue
            chord = _linearizationSecValues(stateVariables, "root", "middle", aileronDivisionValue, "chord")
            aoa = _linearizationSecValues(stateVariables, "root", "middle", aileronDivisionValue, "aoa")
            stateVariables["wing"].update({
                "aileron": {
                    "chord": chord,
                    "b": aileronDivisionValue,
                    "sweepLE": stateVariables["wing"]["middle"]["sweepLE"],
                    "aoa": aoa,
                    "dihedral": 0,
                    "airfoil": stateVariables["horizontal"]["middle"]["airfoil"],
                    "control": "aileron",
                }
            })
            stateVariables["wing"]["middle"].update({"control": "aileron"})
            newB = stateVariables["wing"]["middle"]["b"] - aileronDivisionValue
            stateVariables["wing"]["middle"].update({"b": newB})
            stateVariables["wing"]["tip"].update({"control": "aileron"})
            stateVariables["wing"].move_to_end("middle", last=True)
            stateVariables["wing"].move_to_end("tip", last=True)
        # Case aileron exactly on Middle section:
        if aileronDivisionValue == 0:
            stateVariables["wing"]["middle"].update({"control": "aileron"})
            stateVariables["wing"]["tip"].update({"control": "aileron"})
            stateVariables["wing"].move_to_end("middle", last=True)
            stateVariables["wing"].move_to_end("tip", last=True)

    if "elevator" in controlVariables:
        elevatorDict = controlVariables["elevator"]

        DivisionValue = elevatorDict["spanStartPercentage"] * stateVariables["horizontal"]["tip"]["b"]
        # Case aileron in between Middle and Tip section:
        if DivisionValue > 0:
            chord = _linearizationSecValues(stateVariables, "root", "tip", DivisionValue, "chord", surface="horizontal")
            aoa = _linearizationSecValues(stateVariables, "root", "tip", DivisionValue, "aoa", surface="horizontal")
            stateVariables["horizontal"].update({
                "elevator": {
                    "chord": chord,
                    "b": DivisionValue,
                    "sweepLE": stateVariables["horizontal"]["tip"]["sweepLE"],
                    "aoa": aoa,
                    "dihedral": 0,
                    "airfoil": stateVariables["horizontal"]["tip"]["airfoil"],
                    "control": "elevator",
                }
            })
            stateVariables["horizontal"]["tip"].update({"control": "elevator"})
            newB = stateVariables["horizontal"]["tip"]["b"] - DivisionValue
            stateVariables["horizontal"]["tip"].update({"b": newB})
            stateVariables["horizontal"].move_to_end("tip", last=True)

        # Case aileron exactly on Middle section:
        if DivisionValue == 0:
            stateVariables["horizontal"]["root"].update({"control": "elevator"})
            stateVariables["horizontal"]["tip"].update({"control": "elevator"})
            stateVariables["horizontal"].move_to_end("root", last=True)
            stateVariables["horizontal"].move_to_end("tip", last=True)

    if "rudder" in controlVariables:
        elevatorDict = controlVariables["rudder"]

        DivisionValue = elevatorDict["spanStartPercentage"] * stateVariables["vertical"]["tip"]["b"]
        # Case aileron in between Middle and Tip section:
        if DivisionValue > 0:
            chord = _linearizationSecValues(stateVariables, "root", "tip", DivisionValue, "chord", surface="vertical")
            aoa = _linearizationSecValues(stateVariables, "root", "tip", DivisionValue, "aoa", surface="vertical")
            stateVariables["vertical"].update({
                "rudder": {
                    "chord": chord,
                    "b": DivisionValue,
                    "sweepLE": stateVariables["vertical"]["tip"]["sweepLE"],
                    "aoa": aoa,
                    "dihedral": 0,
                    "airfoil": stateVariables["vertical"]["tip"]["airfoil"],
                    "control": "rudder",
                }
            })
            stateVariables["vertical"]["tip"].update({"control": "rudder"})
            newB = stateVariables["vertical"]["tip"]["b"] - DivisionValue
            stateVariables["vertical"]["tip"].update({"b": newB})
            stateVariables["vertical"].move_to_end("tip", last=True)

        # Case aileron exactly on Middle section:
        if DivisionValue == 0:
            stateVariables["vertical"]["root"].update({"control": "rudder"})
            stateVariables["vertical"]["tip"].update({"control": "rudder"})
            stateVariables["vertical"].move_to_end("root", last=True)
            stateVariables["vertical"].move_to_end("tip", last=True)
    return stateVariables


def _linearizationSecValues(stateVariables, secName01, secName02, xValue, yName, surface="wing"):
    ratioYX = (stateVariables[surface][secName02][yName] - stateVariables[surface][secName01][yName]) / \
              stateVariables[surface][secName02]["b"]
    yValue = ratioYX * xValue + stateVariables[surface][secName01][yName]
    return yValue
