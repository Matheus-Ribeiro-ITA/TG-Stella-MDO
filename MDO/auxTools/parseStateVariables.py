import numpy as np
import os


def parseStateVariable(x_states_global, variables='short', x_states_default_values=None):
    """Parse variabels from (Area, AR ...) to AVL formats (cRoot, ...)"""

    if variables == 'all':
        pass
        # x_states = [0]*len(x_states_global)
        #
        # # VARIABLES
        # # -----------------------------
        # # WING
        # wingSpan = x_states_global[0]
        # wingSecPercentage = x_states_global[1]
        # wingArea =  x_states_global[2]
        # aspectRatio = x_states_global[3]
        # taperRatio1 = x_states_global[4]
        # taperRatio2 = x_states_global[5]
        # sweepWing1 = x_states_global[6]
        # sweepWing2 = x_states_global[7]
        #
        #
        # wingRootChord = wingArea/wingSpan/ \
        #                 ((1+taperRatio1)/2*wingSecPercentage + taperRatio1*(1+taperRatio2)/2*(1-wingSecPercentage))
        # wingMiddleChord = wingRootChord * taperRatio1  # wingMiddleChord
        # wingTipChord = wingMiddleChord * taperRatio2 # wingTipChord
        #
        # x_states[0] = wingSpan  # wingSpan
        # x_states[1] = wingSecPercentage # wingSecPercentage
        # x_states[2] = wingRootChord
        # x_states[3] = wingMiddleChord
        # x_states[4] = wingTipChord
        #
        #
        # # -----------------------------
        # # invert V
        # aspectRatioV = x_states_global[8]
        # areaV = x_states_global[9]
        # taperV = x_states_global[10]
        # sweepLEV =  x_states_global[11]
        # dihedralV = x_states_global[12]
        # posZV = x_states_global[13]
        # posXV = x_states_global[14]
        #
        # # horizontalSpan = np.sqrt(aspectRatioV*areaV)
        # # horizontalRootChord = 2*areaV/horizontalSpan/(1+taperV)
        # # horizontalTipChord = horizontalRootChord*taperV
        # # horizontalXPosition = posXV
        # verticalSpanTotal = np.sqrt(aspectRatioV*areaV)
        # verticalSpanAVL = verticalSpanTotal/2
        # verticalRootChord = 2*areaV/verticalSpanTotal/(1+taperV)
        # verticalTipChord = verticalRootChord*taperV
        # verticalXPosition = posXV
        #
        # x_states[5] =  verticalSpanAVL
        # x_states[6] = verticalRootChord
        # x_states[7] = verticalTipChord
        # x_states[8] = verticalXPosition
        #
        # # verticalSpan = x_states[8]
        # # verticalRootChord = x_states[9]
        # # verticalTipChord = x_states[10]
        #
        # return x_states

    if variables == 'short':
        if isinstance(x_states_global, list):
            x_states = _parse_from_list(x_states_global)
        elif isinstance(x_states_global, dict):
            x_states_global = _parse_dict_to_list(x_states_global, x_states_default_values=x_states_default_values)
            x_states = _parse_from_list(x_states_global)
        return x_states


def _parse_from_list(x_states_global):
    x_states = [0] * len(x_states_global)

    # VARIABLES
    # -----------------------------
    # WING
    aspectRatio = x_states_global[0]
    wingSecPercentage = x_states_global[1]
    wingArea = x_states_global[2]
    taperRatio1 = x_states_global[3]
    taperRatio2 = x_states_global[4]
    # sweepWing1 = x_states_global[6]
    # sweepWing2 = x_states_global[7]

    wingSpan = np.sqrt(aspectRatio * wingArea)
    wingRootChord = wingArea / \
                    wingSpan / \
                    ((1 + taperRatio1) / 2 * wingSecPercentage + taperRatio1 * (1 + taperRatio2) / 2 *
                     (1 - wingSecPercentage))
    wingMiddleChord = wingRootChord * taperRatio1  # wingMiddleChord
    wingTipChord = wingMiddleChord * taperRatio2  # wingTipChord

    x_states[0] = wingSpan  # wingSpan
    x_states[1] = wingSecPercentage  # wingSecPercentage
    x_states[2] = wingRootChord
    x_states[3] = wingMiddleChord
    x_states[4] = wingTipChord

    # -----------------------------
    # invert V
    aspectRatioV = x_states_global[5]
    areaV = x_states_global[6]
    taperV = x_states_global[7]
    posXV = x_states_global[8]
    # sweepLEV =  x_states_global[11]
    # dihedralV = x_states_global[12]
    # posZV = x_states_global[13]
    verticalSpanTop = np.sqrt(aspectRatioV * areaV)
    verticalSpanTotal = verticalSpanTop / np.sqrt(2)
    verticalSpanAVL = verticalSpanTotal / 2
    verticalRootChord = 2 * areaV / verticalSpanTop / (1 + taperV)
    verticalTipChord = verticalRootChord * taperV
    verticalXPosition = posXV

    x_states[5] = verticalSpanAVL
    x_states[6] = verticalRootChord
    x_states[7] = verticalTipChord
    x_states[8] = verticalXPosition


    # -----------------------------
    # Fuselage
    fuselageLength = x_states_global[9]
    x_states[9] = fuselageLength

    return x_states


def _parse_dict_to_list(x_states_global, x_states_default_values=None):

    x_states_global[0] = x_states_global['aspectRatio'] \
        if 'aspectRatio' in x_states_global else x_states_default_values['aspectRatio']
    x_states_global[1] = x_states_global['wingSecPercentage'] \
        if 'wingSecPercentage' in x_states_global else x_states_default_values['wingSecPercentage']
    x_states_global[2] = x_states_global['wingArea'] \
        if 'wingArea' in x_states_global else x_states_default_values['wingArea']
    x_states_global[3] = x_states_global['taperRatio1'] \
        if 'taperRatio1' in x_states_global else x_states_default_values['taperRatio1']
    x_states_global[4] = x_states_global['taperRatio2'] \
        if 'taperRatio2' in x_states_global else x_states_default_values['taperRatio2']
    x_states_global[5] = x_states_global['aspectRatioV'] \
        if 'aspectRatioV' in x_states_global else x_states_default_values['aspectRatioV']
    x_states_global[6] = x_states_global['areaV'] \
        if 'areaV' in x_states_global else x_states_default_values['areaV']
    x_states_global[7] = x_states_global['taperV'] \
        if 'taperV' in x_states_global else x_states_default_values['taperV']
    x_states_global[8] = x_states_global['posXV'] \
        if 'posXV' in x_states_global else x_states_default_values['posXV']
    x_states_global[9] = x_states_global['fuselageLength'] \
        if 'fuselageLength' in x_states_global else x_states_default_values['fuselageLength']

    return x_states_global