import os
import time
from _collections import OrderedDict
import numpy as np
import pandas as pd
from configparser import ConfigParser

from aircraftInfo import AircraftInfo
import MDO

config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))


def main(x_states_global, logger=None):
    # ----Vertical Stabilizer-------------------------------------
    # Options: "conventional", "v".
    # Warning: option "h" is broken
    verticalType = "v"

    # --Airfoils------------------------------------------------
    wingAirfoil = "ls417mod_cruise"
    stabAirfoil = "naca0012_cruise"

    # ----Variables Optimizer---------------------------------------
    x_states_avl = MDO.parseStateVariable(x_states_global)

    wingSpan = x_states_avl[0]
    wingSecPercentage = x_states_avl[1]
    wingRootChord = x_states_avl[2]
    wingMiddleChord = x_states_avl[3]
    wingTipChord = x_states_avl[4]

    verticalSpan = x_states_avl[5]
    verticalRootChord = x_states_avl[6]
    verticalTipChord = x_states_avl[7]
    verticalXPosition = x_states_avl[8]

    if os.environ["DEBUG"] == 'yes':
        print(f"wingSpan: {wingSpan}")
        print(f"wingSecPercentage: {wingSecPercentage}")
        print(f"wingRootChord: {wingRootChord}")
        print(f"wingMiddleChord: {wingMiddleChord}")
        print(f"wingTipChord: {wingTipChord}")
        print(f"verticalSpan: {verticalSpan}")
        print(f"verticalRootChord: {verticalRootChord}")
        print(f"verticalTipChord: {verticalTipChord}")
        print(f"verticalXPosition: {verticalXPosition}")


    # endPlateTipChord = 0.4

    wingSecPosition = wingSpan / 2 * wingSecPercentage
    wingPosSec = wingSpan / 2 * (1 - wingSecPercentage)

    # ----Config CG---------------------------------------
    # Priority order: smFixed > cgFixed
    cgFixed = None
    smFixedPercent = 5  # In percentage
    # ----Parser to dict---------------------------------------
    stateVariables, controlVariables, avlMandatoryCases, avlCases, engineInfo, missionProfile = MDO.set_state_variables(
        wingRootChord=wingRootChord, wingAirfoil=wingAirfoil, wingMiddleChord=wingMiddleChord,
        wingSecPosition=wingSecPosition, wingTipChord=wingTipChord, wingPosSec=wingPosSec,
        horizontalRootChord=None,
        horizontalXPosition=None, verticalXPosition=verticalXPosition,
        horizontalTipChord=None,
        horizontalSpan=None, verticalRootChord=verticalRootChord, verticalTipChord=verticalTipChord,
        verticalSpan=verticalSpan, stabAirfoil=stabAirfoil
    )

    # ---- Aircraft Info Class ----------------------------------------
    aircraftInfo = AircraftInfo(stateVariables, controlVariables, engineInfo=engineInfo)

    # ---- Aircraft Neutral Point Calc ----------------------------------------
    if smFixedPercent is not None:
        results = MDO.avlMain(aircraftInfo, avlMandatoryCases, verticalType=verticalType)
        # cL1 = results['NeutralPoint_0']['Totals']['CLtot']
        # cL2 = results['NeutralPoint_1']['Totals']['CLtot']
        # cm1 = results['NeutralPoint_0']['Totals']['Cmtot']
        # cm2 = results['NeutralPoint_1']['Totals']['Cmtot']
        #
        # test = (cL2 - cL1)/(cm2-cm1)

        aircraftInfo.xNeutralPoint = (results['NeutralPoint_0']['StabilityDerivatives']['Xnp']
                                      + results['NeutralPoint_1']['StabilityDerivatives']['Xnp'])/2
        aircraftInfo.adjustCG(cgFixed=None, smFixedPercent=smFixedPercent)
    else:
        aircraftInfo.adjustCG(cgFixed=cgFixed, smFixedPercent=None)

    # ---- Avl -----------------------------------------
    results = MDO.avlMain(aircraftInfo, avlCases, verticalType=verticalType)

    # ---- Results -----------------------------------------
    output_dict = MDO.mainResults(results=results, aircraftInfo=aircraftInfo, avlCases=avlCases,
                                  missionProfile=missionProfile, logger=logger)

    return pd.DataFrame(output_dict, index=[0])


if __name__ == '__main__':
    # ----Process Time--------------------------------------------
    startTime = time.time()

    # ----logging--------------------------------------------
    logger = MDO.createLog(name="main")
    logger.info("------------------BEGIN------------------")

    # ----Config ----------------------------------------------
    MDO.parseConfig("outputsConfig.cfg")

    num_states = 9
    x_states_global = np.array([0.0] * num_states)

    x_states_global[0] = 9  # aspectRatio
    x_states_global[1] = 0.5  # wingSecPercentage
    x_states_global[2] = 3  # wingArea
    x_states_global[3] = 1  # taperRatio1
    x_states_global[4] = 1  # taperRatio2
    x_states_global[5] = 5  # aspectRatioV
    x_states_global[6] = 0.8  # areaV
    x_states_global[7] = 1  # taperV
    x_states_global[8] = 1.5  # posXV


    # x_states[0] = 6  # wingSpan = 6
    # x_states[1] = 0.5  # wingSecPercentage = 0.5
    # x_states[2] = 0.68  # wingRootChord = 0.68
    # x_states[3] = 0.35  # wingTipChord = 0.35
    # wingMiddleChord = (x_states[2] + x_states[3]) / 2
    #
    # x_states[4] = 1.5  # horizontalSpan = 1.5
    # x_states[5] = 0.5  # horizontalRootChord = 0.5
    # x_states[6] = 0.5  # horizontalTipChord = 0.5
    # x_states[7] = 2  # horizontalXPosition = 2
    #
    # x_states[8] = 0.8  # verticalSpan = 0.8 Remember that is H vertical
    # x_states[9] = 0.375  # verticalRootChord = 0.375
    # x_states[10] = 0.375  # verticalTipChord = 0.375

    # endPlateTipChord = 0.4  # endPlateTipChord = 0.4

    # wingSecPosition = x_states[0] / 2 * x_states[1]
    # wingPosSec = x_states[0] / 2 * (1 - x_states[1])

    main(x_states_global)

    # ---- Time-----------------------------------------
    print(f"Process Time: {round((time.time() - startTime), 1)} s")
    logger.info(f"Process Time: {round((time.time() - startTime), 1)} s")
    logger.info("------------------END------------------")
