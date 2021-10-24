import numpy as np


def parseStateVariable(x_states_global, variables='short'):
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
        x_states = [0]*len(x_states_global)

        # VARIABLES
        # -----------------------------
        # WING
        aspectRatio = x_states_global[0]
        wingSecPercentage = x_states_global[1]
        wingArea =  x_states_global[2]
        taperRatio1 = x_states_global[3]
        taperRatio2 = x_states_global[4]
        # sweepWing1 = x_states_global[6]
        # sweepWing2 = x_states_global[7]

        wingSpan = np.sqrt(aspectRatio*wingArea)
        wingRootChord = wingArea/wingSpan/ \
                        ((1+taperRatio1)/2*wingSecPercentage + taperRatio1*(1+taperRatio2)/2*(1-wingSecPercentage))
        wingMiddleChord = wingRootChord * taperRatio1  # wingMiddleChord
        wingTipChord = wingMiddleChord * taperRatio2 # wingTipChord

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

        verticalSpanTotal = np.sqrt(aspectRatioV * areaV)
        verticalSpanAVL = verticalSpanTotal / 2
        verticalRootChord = 2 * areaV / verticalSpanTotal / (1 + taperV)
        verticalTipChord = verticalRootChord*taperV
        verticalXPosition = posXV

        x_states[5] =  verticalSpanAVL
        x_states[6] = verticalRootChord
        x_states[7] = verticalTipChord
        x_states[8] = verticalXPosition

        # -----------------------------
        # Fuselage
        fuselageLength = x_states_global[9]
        x_states[9] = fuselageLength

        return x_states