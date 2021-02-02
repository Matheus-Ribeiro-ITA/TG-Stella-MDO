import json
from math import radians, sqrt, tan
import avl.avlwrapper as avl
import time

stateVariables = {
    "wing": {
        "root": {
            "chord": 0.3,
            "aoa": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "airfoil": "2414"
        },
        "middle": {
            "chord": 0.3,
            "b": 1,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "2414"
        },
        "tip": {
            "chord": 0.1,
            "b": 0.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "2414"
        },
    },
    "horizontal": {
        "root": {
            "chord": 0.2,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0,
            "airfoil": "0012"
        },
        "tip": {
            "chord": 0.2,
            "b": 0.4,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "0012"
        }
    },
    "vertical": {
        "root": {
            "chord": 0.2,
            "aoa": 0,
            "x": 2,
            "y": 0,
            "z": 0.5,
            "airfoil": "0012"
        },
        "tip": {
            "chord": 0.2,
            "b": 0.4,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": "0012"
        }
    }
}



def avlGeoBuild(stateVariables):
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

    surfaceArea, surfaceMAC, surfaceSpan = areaMacSurface(stateVariables['wing'])
    ref_pnt = avl.Point(x=0, y=0, z=0)
    aircraft = avl.Aircraft(name='aircraft',
                            reference_area=surfaceArea,
                            reference_chord=surfaceMAC,
                            reference_span=surfaceSpan,
                            reference_point=ref_pnt,
                            mach=0,
                            surfaces=surfaces)
    return aircraft


def _translateSec(secName, secData, secPoint, surfaceName=None):

    if secName == "root":
        secPoint = [secData['x'], secData['y'], secData['z']]
        wing_root_le_pnt = avl.Point(*secPoint)

        controlSurfaces = []
        if "control" in secData:
            controlSurfaces = avl.Control(name=secData['control'],
                                          gain=1.0,
                                          x_hinge=0.6,
                                          duplicate_sign=1)

        section = avl.Section(leading_edge_point=wing_root_le_pnt,
                              chord=secData['chord'],
                              airfoil=avl.NacaAirfoil(secData['airfoil']))
    else:
        if surfaceName == "vertical":
            secPoint = [secPoint[0] + secData['b'] * tan(secData['sweepLE']),
                        secPoint[1] + secData['b'] * tan(secData['dihedral']),
                        secPoint[2] + secData['b']]
            sec_le_pnt = avl.Point(x=secPoint[0],
                                   y=secPoint[1],
                                   z=secPoint[2])

        else:
            secPoint = [secPoint[0] + secData['b'] * tan(secData['sweepLE']),
                        secPoint[1] + secData['b'],
                        secPoint[2] + secData['b'] * tan(secData['dihedral'])]
            sec_le_pnt = avl.Point(x=secPoint[0],
                                   y=secPoint[1],
                                   z=secPoint[2])

        section = avl.Section(leading_edge_point=sec_le_pnt,
                              chord=secData['chord'],
                              airfoil=avl.NacaAirfoil(secData['airfoil']))
    return section, secPoint


def areaMacSurface(surfaceDict):
    keysSurfaceDict = list(surfaceDict.keys())
    surfaceArea = 0
    surfaceMAC = 0
    surfaceSpan = 0
    for i in range(len(keysSurfaceDict) - 1):
        chordRootSec = surfaceDict[keysSurfaceDict[i]]['chord']
        chordTipSec = surfaceDict[keysSurfaceDict[i + 1]]['chord']
        spanSec = surfaceDict[keysSurfaceDict[i + 1]]['b']

        secArea = spanSec * (chordRootSec + chordTipSec) / 2
        surfaceArea += secArea

        taperRatio = chordTipSec / chordRootSec
        secMAC = 2 / 3 * chordRootSec * (1 + taperRatio + taperRatio ** 2) / (1 + taperRatio)
        surfaceMAC += secArea * secMAC

        surfaceSpan += spanSec

    surfaceMAC = surfaceMAC / surfaceArea

    return surfaceArea, surfaceMAC, surfaceSpan
