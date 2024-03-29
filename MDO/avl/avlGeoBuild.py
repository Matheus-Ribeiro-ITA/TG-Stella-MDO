from math import tan
import avl
from numpy import pi


def avlGeoBuild(stateVariables, controlVariables, verticalType="conventional"):
    stateVariables = _addControl2States(stateVariables, controlVariables, verticalType)
    surfaces = []

    for surfaceName, surfaceDict in stateVariables.items():
        secPoint = []
        sections = []
        # Especial case for H vertical
        if "vertical" in surfaceName.lower() and verticalType == "h":
            sections = _sectionsVerticalH(surfaceDict)

        elif "vertical" in surfaceName.lower() and verticalType == "conventional":
            for secName, secData in surfaceDict.items():
                section, secPoint = _translateSec(secName, secData, secPoint, surfaceName=surfaceName,
                                                  controlVariables=controlVariables)
                sections.append(section)

        elif "horizontal" in surfaceName.lower() and verticalType != "v":
            for secName, secData in surfaceDict.items():
                section, secPoint = _translateSec(secName, secData, secPoint, surfaceName=surfaceName,
                                                  controlVariables=controlVariables)
                sections.append(section)

        elif "wing" in surfaceName.lower():
            for secName, secData in surfaceDict.items():
                section, secPoint = _translateSec(secName, secData, secPoint, surfaceName=surfaceName,
                                                  controlVariables=controlVariables)
                sections.append(section)

        # Not duplicate the conventional vertical (H is duplicated)
        if "vertical" in surfaceName.lower() and verticalType == "conventional":
            yDuplicate = 1
        else:
            yDuplicate = 0

        if surfaceName == "horizontal" or surfaceName == "vertical":
            nChordWise = 9
            nSpanWise = 15
        else:
            nChordWise = 12
            nSpanWise = 20

        if len(sections) > 1:
            surfaces.append(avl.Surface(name=surfaceName,
                                        n_chordwise=nChordWise,
                                        chord_spacing=avl.Spacing.cosine,
                                        n_spanwise=nSpanWise,
                                        span_spacing=avl.Spacing.cosine,
                                        y_duplicate=yDuplicate,
                                        sections=sections))

    # Special case for V tail
    if verticalType.lower() == "v":
        surface = _surfaceVerticalV(stateVariables["vertical"])
        surfaces.append(surface)

    surfaceArea, surfaceMAC, surfaceSpan, surfaceSweep, surfaceTipX = infoSurface(stateVariables['wing'])

    if "endPlate" in stateVariables:
        surfaceEndPlate = _surfaceEndPlate(surfaceTipX, surfaceSpan/2, stateVariables["wing"], stateVariables["endPlate"])
        surfaces.append(surfaceEndPlate)

    ref_pnt = avl.Point(x=0, y=0, z=0)
    aircraftAvl = avl.Aircraft(name='aircraft',
                               reference_area=surfaceArea,
                               reference_chord=surfaceMAC,
                               reference_span=surfaceSpan,
                               reference_point=ref_pnt,
                               mach=0,
                               surfaces=surfaces)

    return aircraftAvl


def _translateSec(secName, secData, secPoint, surfaceName=None, controlVariables=None):
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
            commandInversion = 1  # TODO: Hinge moment (-1 to invert)
        else:
            commandInversion = 1
        controlSurfaces = avl.Control(name=secData['control'],
                                      gain=1.0,
                                      x_hinge=controlVariables[secData['control']]['cHinge'],
                                      duplicate_sign=commandInversion)

    section = avl.Section(leading_edge_point=sec_le_pnt,
                          chord=secData['chord'],
                          airfoil=avl.FileAirfoil(secData['airfoil'].name + ".dat"),
                          cl_alpha_scaling=secData['airfoil'].claf,
                          profile_drag=avl.ProfileDrag(cd=secData['airfoil'].cd, cl=secData['airfoil'].cl),
                          controls=[controlSurfaces])
    return section, secPoint


def _sectionsVerticalH(surfaceDict):
    """
    # Description:
        Create avl surface Vertical estabilizer in H.

    ## Parameters:
        surfaceDict [Dict]: Vertical Dict, 1st level nested in StateVariables.

    ## Returns:
        Sections [List]: List of Section AVL Object.
    """
    sections = []

    secPointRoot = [surfaceDict["root"]['x'], surfaceDict["root"]['y'], surfaceDict["root"]['z']]
    secPointLow = [secPointRoot[0] + surfaceDict["tip"]['b'] * tan(surfaceDict["tip"]['sweepLE']),
                   secPointRoot[1] - surfaceDict["tip"]['b'] * tan(surfaceDict["tip"]['dihedral']),
                   secPointRoot[2] - surfaceDict["tip"]['b']]
    secPointHigh = [secPointRoot[0] + surfaceDict["tip"]['b'] * tan(surfaceDict["tip"]['sweepLE']),
                    secPointRoot[1] + surfaceDict["tip"]['b'] * tan(surfaceDict["tip"]['dihedral']),
                    secPointRoot[2] + surfaceDict["tip"]['b']]

    secLePointLow = avl.Point(*secPointLow)
    secPointRoot = avl.Point(*secPointRoot)
    secPointHigh = avl.Point(*secPointHigh)

    controlSurfaces = None
    if "control" in surfaceDict["root"]:
        controlSurfaces = avl.Control(name=surfaceDict["root"]['control'],
                                      gain=1.0,
                                      x_hinge=0.6,  # TODO:
                                      duplicate_sign=1)

    sections = [
        avl.Section(leading_edge_point=secLePointLow,
                    chord=surfaceDict["tip"]['chord'],
                    airfoil=avl.FileAirfoil(surfaceDict["tip"]['airfoil'].name + ".dat"),
                    cl_alpha_scaling=surfaceDict["tip"]['airfoil'].claf,
                    profile_drag=avl.ProfileDrag(cd=surfaceDict["tip"]['airfoil'].cd,
                                                 cl=surfaceDict["tip"]['airfoil'].cl),
                    controls=[controlSurfaces]),
        avl.Section(leading_edge_point=secPointRoot,
                    chord=surfaceDict["root"]['chord'],
                    airfoil=avl.FileAirfoil(surfaceDict["root"]['airfoil'].name + ".dat"),
                    cl_alpha_scaling=surfaceDict["root"]['airfoil'].claf,
                    profile_drag=avl.ProfileDrag(cd=surfaceDict["root"]['airfoil'].cd,
                                                 cl=surfaceDict["root"]['airfoil'].cl),
                    controls=[controlSurfaces]),
        avl.Section(leading_edge_point=secPointHigh,
                    chord=surfaceDict["tip"]['chord'],
                    airfoil=avl.FileAirfoil(surfaceDict["tip"]['airfoil'].name + ".dat"),
                    cl_alpha_scaling=surfaceDict["tip"]['airfoil'].claf,
                    profile_drag=avl.ProfileDrag(cd=surfaceDict["tip"]['airfoil'].cd,
                                                 cl=surfaceDict["tip"]['airfoil'].cl),
                    controls=[controlSurfaces])
    ]
    return sections


def _surfaceVerticalV(surfaceVertical):
    """
    # Description:
        Create avl surface Vertical estabilizer in H.

    ## Parameters:
        surfaceDict [Dict]: Vertical Dict, 1st level nested in StateVariables.

    ## Returns:
        Sections [List]: List of Section AVL Object.
    """
    # assert surfaceHorizontal["root"]['x'] == surfaceVertical["root"]['x'], "Vertical root differ Horizontal root"

    secPointRoot = [surfaceVertical["root"]['x'], surfaceVertical["root"]['y'], surfaceVertical["root"]['z']]

    secPointLowRight = [secPointRoot[0] + surfaceVertical["tip"]['b'] * tan(surfaceVertical["tip"]['sweepLE']),
                        secPointRoot[1] + surfaceVertical["tip"]['b'] * tan(
                            45 * pi / 180 + surfaceVertical["tip"]['dihedral']),
                        secPointRoot[2] - surfaceVertical["tip"]['b']]

    secLePointLowRight = avl.Point(*secPointLowRight)
    secPointRoot = avl.Point(*secPointRoot)

    controlSurfaces = None
    if "control" in surfaceVertical["root"]:
        controlSurfaces = avl.Control(name=surfaceVertical["root"]['control'],
                                      gain=1.0,
                                      x_hinge=0.6,  # TODO:
                                      duplicate_sign=1)

    sections = [
        avl.Section(leading_edge_point=secLePointLowRight,
                    chord=surfaceVertical["tip"]['chord'],
                    airfoil=avl.FileAirfoil(surfaceVertical["tip"]['airfoil'].name + ".dat"),
                    cl_alpha_scaling=surfaceVertical["tip"]['airfoil'].claf,
                    profile_drag=avl.ProfileDrag(cd=surfaceVertical["tip"]['airfoil'].cd,
                                                 cl=surfaceVertical["tip"]['airfoil'].cl),
                    controls=[controlSurfaces]),
        avl.Section(leading_edge_point=secPointRoot,
                    chord=surfaceVertical["root"]['chord'],
                    airfoil=avl.FileAirfoil(surfaceVertical["root"]['airfoil'].name + ".dat"),
                    cl_alpha_scaling=surfaceVertical["root"]['airfoil'].claf,
                    profile_drag=avl.ProfileDrag(cd=surfaceVertical["root"]['airfoil'].cd,
                                                 cl=surfaceVertical["root"]['airfoil'].cl),
                    controls=[controlSurfaces])
    ]

    yDuplicate = 0
    nChordWise = 9
    nSpanWise = 15

    return avl.Surface(name="vertical",
                       n_chordwise=nChordWise,
                       chord_spacing=avl.Spacing.cosine,
                       n_spanwise=nSpanWise,
                       span_spacing=avl.Spacing.cosine,
                       y_duplicate=yDuplicate,
                       sections=sections)


def _surfaceEndPlate(surfaceTipX, surfaceSpan, surfaceWing, surfaceEndPlate):
    """
    # Description:
        Create avl surface Vertical estabilizer in H.

    ## Parameters:
        surfaceDict [Dict]: Vertical Dict, 1st level nested in StateVariables.

    ## Returns:
        Sections [List]: List of Section AVL Object.
    """

    # assert surfaceHorizontal["root"]['x'] == surfaceVertical["root"]['x'], "Vertical root differ Horizontal root"
    secPointRoot = [surfaceTipX, surfaceSpan, 0]  # TODO: Dihedral
    secPointHigh = [secPointRoot[0] + surfaceEndPlate["tip"]['b'] * tan(surfaceEndPlate["tip"]['sweepLE']),
                    secPointRoot[1],
                    secPointRoot[2] + surfaceEndPlate["tip"]['b']]

    secLePointLow = avl.Point(*secPointRoot)
    secPointRootHigh = avl.Point(*secPointHigh)

    sections = [
        avl.Section(leading_edge_point=secLePointLow,
                    chord=surfaceWing["tip"]['chord'],
                    airfoil=avl.FileAirfoil(surfaceEndPlate["root"]['airfoil'].name + ".dat"),
                    cl_alpha_scaling=surfaceEndPlate["root"]['airfoil'].claf,
                    profile_drag=avl.ProfileDrag(cd=surfaceEndPlate["root"]['airfoil'].cd,
                                                 cl=surfaceEndPlate["root"]['airfoil'].cl)
                    ),
        avl.Section(leading_edge_point=secPointRootHigh,
                    chord=surfaceWing["tip"]['chord'], # TODO: Add variable endplate chord
                    airfoil=avl.FileAirfoil(surfaceEndPlate["tip"]['airfoil'].name + ".dat"),
                    cl_alpha_scaling=surfaceEndPlate["tip"]['airfoil'].claf,
                    profile_drag=avl.ProfileDrag(cd=surfaceEndPlate["tip"]['airfoil'].cd,
                                                 cl=surfaceEndPlate["tip"]['airfoil'].cl),
                    )
    ]

    yDuplicate = 0
    nChordWise = 6
    nSpanWise = 10

    return avl.Surface(name="endPlate",
                       n_chordwise=nChordWise,
                       chord_spacing=avl.Spacing.cosine,
                       n_spanwise=nSpanWise,
                       span_spacing=avl.Spacing.cosine,
                       y_duplicate=yDuplicate,
                       sections=sections)


def _addControl2States(stateVariables, controlVariables, verticalType="conventional"):
    """
    -Description
        Add control surfaces from "controlVariables" to the "stateVariables"

    - Input
    :param stateVariables[Dict]: aircraft state variables. Ex: wing chord, espan etc
    :param controlVariables[Dict]:
    - Output
    :return:
    """

    middleSecPosition = stateVariables["wing"]["middle"]["b"]
    wingSpan = middleSecPosition + stateVariables["wing"]["tip"]["b"]

    if "aileron" in controlVariables:
        aileronDict = controlVariables["aileron"]
        aileronDivisionValue = aileronDict["spanStartPercentage"] * wingSpan - middleSecPosition
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
        # Case aileron in between Root and Middle section: (Goes to middle)
        # elif aileronDivisionValue < 0:
        # aileronDivisionValue = 0
        # aileronDivisionValue = rootSecSpan + aileronDivisionValue
        # chord = _linearizationSecValues(stateVariables, "root", "middle", aileronDivisionValue, "chord")
        # aoa = _linearizationSecValues(stateVariables, "root", "middle", aileronDivisionValue, "aoa")
        # stateVariables["wing"].update({
        #     "aileron": {
        #         "chord": chord,
        #         "b": aileronDivisionValue,
        #         "sweepLE": stateVariables["wing"]["middle"]["sweepLE"],
        #         "aoa": aoa,
        #         "dihedral": 0,
        #         "airfoil": stateVariables["wing"]["middle"]["airfoil"],
        #         "control": "aileron",
        #     }
        # })
        # stateVariables["wing"]["middle"].update({"control": "aileron"})
        # newB = stateVariables["wing"]["middle"]["b"] - aileronDivisionValue
        # stateVariables["wing"]["middle"].update({"b": newB})
        # stateVariables["wing"]["tip"].update({"control": "aileron"})
        # stateVariables["wing"].move_to_end("middle", last=True)
        # stateVariables["wing"].move_to_end("tip", last=True)
        # Case aileron exactly on Middle section:
        elif aileronDivisionValue <= 0:
            stateVariables["wing"]["middle"].update({"control": "aileron"})
            stateVariables["wing"]["tip"].update({"control": "aileron"})

    if "elevator" in controlVariables and verticalType != "v":
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

    if verticalType == "conventional":
        if "rudder" in controlVariables:
            elevatorDict = controlVariables["rudder"]

            DivisionValue = elevatorDict["spanStartPercentage"] * stateVariables["vertical"]["tip"]["b"]
            # Case rudder in between Middle and Tip section:
            if DivisionValue > 0:
                chord = _linearizationSecValues(stateVariables, "root", "tip", DivisionValue, "chord",
                                                surface="vertical")
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

            # Case rudder exactly on Root section:
            if DivisionValue == 0:
                stateVariables["vertical"]["root"].update({"control": "rudder"})
                stateVariables["vertical"]["tip"].update({"control": "rudder"})
                stateVariables["vertical"].move_to_end("root", last=True)
                stateVariables["vertical"].move_to_end("tip", last=True)
    elif verticalType == "h":
        # Only full span rudder for Vertical H.
        if "rudder" in controlVariables:
            stateVariables["vertical"]["root"].update({"control": "rudder"})
            stateVariables["vertical"]["tip"].update({"control": "rudder"})
            stateVariables["vertical"].move_to_end("root", last=True)
            stateVariables["vertical"].move_to_end("tip", last=True)

    elif verticalType == "v":
        if "elevator" in controlVariables:
            stateVariables["vertical"]["root"].update({"control": "elevator"})
            stateVariables["vertical"]["tip"].update({"control": "elevator"})
            stateVariables["vertical"].move_to_end("root", last=True)
            stateVariables["vertical"].move_to_end("tip", last=True)

    if "flap" in controlVariables:
        flapDict = controlVariables["flap"]
        # divList = [0]
        # for sec in stateVariables["wing"].values():
        #     try:
        #         divList.append(sec["b"])
        #         divList[-1] += divList[-2]
        #     except KeyError:
        #         pass
        #
        # print(divList)
        flapDivisionValue = flapDict["spanStartPercentage"] * wingSpan
        # Case flap in between Root and Middle section:
        if 0 < flapDivisionValue < middleSecPosition:
            chord = _linearizationSecValues(stateVariables, "root", "middle", flapDivisionValue, "chord")
            aoa = _linearizationSecValues(stateVariables, "root", "middle", flapDivisionValue, "aoa")
            stateVariables["wing"].update({
                "flap": {
                    "chord": chord,
                    "b": flapDivisionValue,
                    "sweepLE": stateVariables["wing"]["middle"]["sweepLE"],
                    "aoa": aoa,
                    "dihedral": 0,
                    "airfoil": stateVariables["wing"]["middle"]["airfoil"],
                    "control": "flap",
                }
            })
            stateVariables["wing"].move_to_end("flap", last=False)
            stateVariables["wing"].move_to_end("root", last=False)
            stateVariables["wing"]["middle"].update({"control": "flap"})
            newB = stateVariables["wing"]["middle"]["b"] - flapDivisionValue
            stateVariables["wing"]["middle"].update({"b": newB})
        # Case flap in between Root and Middle section:
        elif flapDivisionValue == 0:
            stateVariables["wing"]["root"].update({"control": "flap"})
            stateVariables["wing"]["middle"].update({"control": "flap"})
    return stateVariables


def _linearizationSecValues(stateVariables, secName01, secName02, xValue, yName, surface="wing"):
    ratioYX = (stateVariables[surface][secName02][yName] - stateVariables[surface][secName01][yName]) / \
              stateVariables[surface][secName02]["b"]
    yValue = ratioYX * xValue + stateVariables[surface][secName01][yName]
    return yValue


def infoSurface(surfaceDict):
    """
    # Description:
        Get surface (wing, horizontal or vertical) area, mean aero chord and span.

    ## Inputs:
    - surfaceDict [dict]: valeus from surfaces in stateVariables inner dict. Ex: stateVariables['wing'].

    ## Outputs:
    - surfaceArea [float]:
    - surfaceMAC [float]:
    - surfaceSpan [float]:
    """
    keysSurfaceDict = list(surfaceDict.keys())
    surfaceArea = 0
    surfaceMAC = 0
    surfaceSpan = 0
    surfaceTipX = 0

    for i in range(len(keysSurfaceDict) - 1):
        chordRootSec = surfaceDict[keysSurfaceDict[i]]['chord']
        chordTipSec = surfaceDict[keysSurfaceDict[i + 1]]['chord']
        spanSec = surfaceDict[keysSurfaceDict[i + 1]]['b']

        # Surface Sweep
        surfaceTipX += surfaceDict[keysSurfaceDict[i + 1]]['sweepLE']*surfaceDict[keysSurfaceDict[i + 1]]['b']

        # Surface Area
        secArea = spanSec * (chordRootSec + chordTipSec) / 2
        surfaceArea += secArea

        # Surface MAC
        taperRatio = chordTipSec / chordRootSec
        secMAC = 2 / 3 * chordRootSec * (1 + taperRatio + taperRatio ** 2) / (1 + taperRatio)
        surfaceMAC += secArea * secMAC

        surfaceSpan += spanSec

    # Sweep at 1/4 wing
    surfaceSweep = (surfaceTipX + (surfaceDict['tip']['chord']-surfaceDict['root']['chord'])*1/4)/surfaceSpan

    # Mean MAC from Sections
    surfaceMAC = surfaceMAC / surfaceArea

    return 2*surfaceArea, surfaceMAC, 2*surfaceSpan, surfaceSweep, surfaceTipX